import datetime
# see decorators
from plone.formwidget.autocomplete import AutocompleteFieldWidget, AutocompleteMultiFieldWidget
from z3c.form.browser.checkbox import CheckBoxFieldWidget


from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
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
from DateTime import DateTime


class uacountrySource(object):
    implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        registry = queryUtility(IRegistry)
        self.uacountries = registry.get('ccc.ua.countries', ())
        self.vocab = SimpleVocabulary.fromItems(
            [(x, x) for x in self.uacountries])

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
        return [self.getTerm(kw) for kw in self.uacountries if q in kw.lower()]


class uacountrySourceBinder(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        return uacountrySource(context)


class uaviolVocabulary(object):
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        registry = queryUtility(IRegistry)
        terms = []
        if registry is not None:
            for uaviol in registry.get('ccc.ua.violations', ()):
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleVocabulary.createTerm(uaviol, uaviol.encode('utf-8'), uaviol))
        return SimpleVocabulary(terms)
 
grok.global_utility(uaviolVocabulary, name=u"ccc.ua.fixedviolations")

# Interface class; used to define content-type schema.

class IUrgentAppeal(form.Schema, IImageScaleTraversable):
    """
    Container for all Urgent Appeal info
    """
    
    # If you want a schema-defined interface, delete the form.model
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/urgent_appeal.xml to define the content type
    # and add directives here as necessary.
    
    form.model("models/urgent_appeal.xml")

    date_received = schema.Date(title=_(u"Date this Urgent Appeal was received"))

    current_status = schema.Choice(
                title=_(u"Current Status"),
                values=[_(u'Ongoing'),_(u'Resolved'),_(u'Closed'),_(u'Unknown')]
        )
    
    form.widget(countries=AutocompleteMultiFieldWidget)
    countries = schema.Set(
        title=_(u"Countries"),
        description = _(u'Just type away, it autocompletes'),
        value_type=schema.Choice(source=uacountrySourceBinder()),
        required=True,
        )
    

    demands = RichText(
        title=_(u"Demands"),    
        required=False,
        )    
    

    form.widget(violations=CheckBoxFieldWidget)
    violations = schema.Set(
        title=_(u"Key Violations"),
        description = _(u'You can select multiple items'),
        value_type=schema.Choice(vocabulary=(u"ccc.ua.fixedviolations")),
        required=False,    
        )  
    specificviolations = RichText(
        title=_(u"Specific violations"),
        description = _(u'Anything not covered above'),
        required=False,
    )



    form.fieldset('more_info',
        label=_(u"More info"),
        fields = ['garment','accessories','sports_shoes','shoes','other_industry','total_workforce','percent_women'],
    )    

    garment = schema.Bool(title=_(u"Garment Industry"),required=False,)
    accessories = schema.Bool(title=_(u"Accessoriers"),required=False,)
    sports_shoes = schema.Bool(title=_(u"Sports shoes"),required=False,)
    shoes = schema.Bool(title=_(u"Shoes"),required=False,)
    other_industry = schema.Bool(title=_(u"Other Industry"),required=False,)
    total_workforce = RichText(title=_(u"Total Workforce"),required=False,)
    percent_women = RichText(title=_(u"Percentage Women"),required=False,)

    form.fieldset('stakeholders',
        label=_(u"Stakeholders"),
        fields = ['case_coordinator','seeking_assistance','type_assistance','affilliation','contact_info','other_orgs','target','company_ownership','company_clients'],
    )    

    case_coordinator = schema.TextLine(title=_(u"Case Coordinator"),required=False,)
    seeking_assistance = RichText(title=_(u"Organisation or Union Seeking Assistance"),required=False,)
    type_assistance = schema.Choice(
                title=_(u"Type of organisaton seeking assistance"),
                required=False,
                values=[_(u'Trade Union'),_(u'Labour NGO'),_(u'Womens NGO'),_(u'Other NGO'),_(u'Religious'),_(u'Other')]
        )

    affilliation = RichText(title=_(u"Union Affiliation"),required=False,)
    contact_info = RichText(title=_(u"Contact Info"),required=False,)
    other_orgs = RichText(title=_(u"Other Key Organisations Involved"),required=False,)
    target = RichText(title=_(u"Target for demands"),required=False,)
    company_ownership = RichText(title=_(u"Company Ownership"),required=False,)
    company_clients = RichText(title=_(u"Company Clients"),required=False,)

    form.fieldset('after_closure',
        label=_(u"After Closure"),
        fields = ['date_finalised','outcomes_closure','company_evaluation','status_yearafter'],
    )    
    date_finalised = schema.Date(title=_(u"Date Finalised"),required=False,)
    outcomes_closure = RichText(title=_(u"Outcomes at Closure"),required=False,)
    company_evaluation = RichText(title=_(u"Company Evaluation"),required=False,)
    status_yearafter = RichText(title=_(u"Status after one year"),required=False,)

# read permission only for UAC's and selected partners

#    dexterity.read_permission(date_received='ccc.ua.uainfo')
#    dexterity.read_permission(current_status='ccc.ua.uainfo')
#    dexterity.read_permission(countries='ccc.ua.uainfo')
    dexterity.read_permission(demands='ccc.ua.uainfo')
#    dexterity.read_permission(violations='ccc.ua.uainfo')
#    dexterity.read_permission(specificviolations='ccc.ua.uainfo')
#    dexterity.read_permission(made_public='ccc.ua.uainfo')
#    dexterity.read_permission(garment='ccc.ua.uainfo')
#    dexterity.read_permission(accessories='ccc.ua.uainfo')
#    dexterity.read_permission(sports_shoes='ccc.ua.uainfo')
#    dexterity.read_permission(shoes='ccc.ua.uainfo')
#    dexterity.read_permission(other_industry='ccc.ua.uainfo')
#    dexterity.read_permission(total_workforce='ccc.ua.uainfo')
#    dexterity.read_permission(percent_women='ccc.ua.uainfo')
#    dexterity.read_permission(case_coordinator='ccc.ua.uainfo')
#    dexterity.read_permission(seeking_assistance='ccc.ua.uainfo')
#    dexterity.read_permission(type_assistance='ccc.ua.uainfo')
#    dexterity.read_permission(affilliation='ccc.ua.uainfo')
    dexterity.read_permission(contact_info='ccc.ua.uainfo')
    dexterity.read_permission(other_orgs='ccc.ua.uainfo')
    dexterity.read_permission(target='ccc.ua.uainfo')
    dexterity.read_permission(company_ownership='ccc.ua.uainfo')
    dexterity.read_permission(company_clients='ccc.ua.uainfo')
#    dexterity.read_permission(date_finalised='ccc.ua.uainfo')
    dexterity.read_permission(outcomes_closure='ccc.ua.uainfo')
    dexterity.read_permission(company_evaluation='ccc.ua.uainfo')
    dexterity.read_permission(status_yearafter='ccc.ua.uainfo')

#decorators
@form.default_value(field=IUrgentAppeal['date_received'])
def makeittoday(data):
    return datetime.datetime.today()


@indexer(IUrgentAppeal)
def searchableIndexer(obj):
    return ' '.join([obj.Title(), obj.Description()])
grok.global_adapter(searchableIndexer, name="SearchableText")

@indexer(IUrgentAppeal)
def date_receivedIndexer(obj):
    if obj.date_received is None:
        return None
    return DateTime(obj.date_received.isoformat())
grok.global_adapter(date_receivedIndexer, name="date_received")

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class UrgentAppeal(dexterity.Container):
    grok.implements(IUrgentAppeal)
    
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# urgent_appeal_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class View(dexterity.DisplayForm):
    grok.context(IUrgentAppeal)
    grok.require('zope2.View')
    
    # grok.name('view')


