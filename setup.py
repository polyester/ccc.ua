from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='ccc.ua',
      version=version,
      description="CleanClothes Urgent Appeals",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='CCC Urgent Appeals',
      author='Paul Roeland',
      author_email='paul@cleanclothes.org',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ccc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.namedfile [blobs]',
          'collective.autopermission',
          'plone.app.registry',
          'plone.principalsource',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.formwidget.autocomplete',
          'plone.formwidget.contenttree',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],

      )
