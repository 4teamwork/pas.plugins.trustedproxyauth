# -*- coding: utf-8 -*-
"""
This module contains the tool of pas.plugins.trustedproxyauth
"""
import os
from setuptools import setup, find_packages

version = '1.1'
maintainer = 'Thomas Buchberger'

tests_require = ['zope.testing']

setup(name='pas.plugins.trustedproxyauth',
      version=version,
      description="Authenticates requests coming from a reverse proxy doing "
                  "user authentication.",
      long_description=open('README.txt').read() + '\n' + \
                       open(os.path.join('docs', 'HISTORY.txt')).read(),
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Zope2',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        ],
      keywords='',
      author='Thomas Buchberger',
      author_email='t.buchberger@4teamwork.ch',
      maintainer=maintainer,
      url='https://github.com/pas.plugins.trustedproxyauth',
      license='GPL',
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
