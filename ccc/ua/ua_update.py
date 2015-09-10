import datetime
# see decorators
from plone.formwidget.autocomplete import AutocompleteFieldWidget

from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder, ITokenizedTerm, ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid, implements

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from ccc.ua import MessageFactory as _

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IVocabularyFactory
from z3c.formwidget.query.interfaces import IQuerySource
from plone.indexer.decorator import indexer
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import ITerms
from Products.ZCTextIndex.ParseTree import ParseError
from plone.app.vocabularies.catalog import parse_query
from zope.interface.interface import Attribute, InterfaceClass, Interface
from zope.interface import directlyProvides
from DateTime import DateTime


# get the organisation from the registry

class uaorgSource(object):
    implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        registry = queryUtility(IRegistry)
        self.uaorgs = registry.get('ccc.ua.orgs', ())
        self.vocab = SimpleVocabulary.fromItems(
            [(x, x) for x in self.uaorgs])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        return self.vocab.getTerm(value)

    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)

    def search(self, query_string):
        q = query_string.lower()
        return [self.getTerm(kw) for kw in self.uaorgs if q in kw.lower()]


class uaorgSourceBinder(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        return uaorgSource(context)


# Interface class; used to define content-type schema.

class IUAUpdate(form.Schema, IImageScaleTraversable):
    """
    Update to Urgent Appeal
    """

    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/ua_update.xml to define the content type
    # and add directives here as necessary.

#    form.model("models/ua_update.xml")


    update_date = schema.Date(title=_(u"Date this update was received"))

#    form.widget(uaorganisation=AutocompleteFieldWidget)
    uaorganisation = schema.Choice(
        title=_(u"Organisation for this update"),
        description = _(u''),
#        source=uavocSourceBinder(),
#        vocabulary=u"plone.principalsource.Groups",
#       source=CatalogQuerySourceBinder(portal_type='FSDDepartment',),
       source=uaorgSourceBinder(),
       required=True,
       )

    post_in_summary = schema.Bool(
        title=_(u"Update in summary"),
        description=_(u"Please use sparingly"),
        required=False,
        )
    details = RichText(
        title=_(u"Details"),
        description=_(u"Update on this Urgent Appeal"),
        required=False,
        )
    updateattach = NamedBlobFile(
        title=_(u"Attachment"),
        description=_(u"File attachment"),
        required=False,
        )
    updateattach2 = NamedBlobFile(
        title=_(u"Attachment 2"),
        description=_(u"File attachment number 2"),
        required=False,
        )
    updateattach3 = NamedBlobFile(
        title=_(u"Attachment 3"),
        description=_(u"File attachment number 3"),
        required=False,
        )
    updatepic = NamedBlobImage(
        title=_(u"Image"),
        description=_(u"You can also include an image"),
        required=False,
        )






#decorators
@form.default_value(field=IUAUpdate['update_date'])
def makeittoday(data):
    return datetime.datetime.today()

@indexer(IUAUpdate)
def searchableIndexer(obj):
    return ' '.join([obj.Title(), obj.Description(), obj.details.output])
grok.global_adapter(searchableIndexer, name="SearchableText")

@indexer(IUAUpdate)
def date_receivedIndexer(obj):
    if obj.update_date is None:
        return None
    return DateTime(obj.update_date.isoformat())
grok.global_adapter(date_receivedIndexer, name="update_date")



# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class UAUpdate(dexterity.Item):
    grok.implements(IUAUpdate)

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# ua_update_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class SampleView(grok.View):
    grok.context(IUAUpdate)
    grok.require('zope2.View')

    # grok.name('view')
