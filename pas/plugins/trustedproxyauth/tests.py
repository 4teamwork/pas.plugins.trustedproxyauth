"""Test setup.
"""

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.PloneTestCase import installPackage
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc
import pas.plugins.trustedproxyauth
import unittest


ptc.setupPloneSite()


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             pas.plugins.trustedproxyauth)
            fiveconfigure.debug_mode = False
            installPackage('pas.plugins.trustedproxyauth', quiet=True)

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'README.txt', package='pas.plugins.trustedproxyauth',
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

