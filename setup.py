import os
from setuptools import setup, find_packages

version = '1.3.0'
maintainer = 'Thomas Buchberger'

tests_require = [
    'Plone',
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'unittest2',
    'zope.testing',
    ]

setup(name='pas.plugins.trustedproxyauth',
      version=version,
      description="Authenticates requests coming from a reverse proxy doing "
      "user authentication.",
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='pas plugins trusted proxy auth plone',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/4teamwork/pas.plugins.trustedproxyauth',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pas', 'pas.plugins'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      test_suite='pas.plugins.trustedproxyauth.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
