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
    """Special testcase for pas.plugins.trustedproxyauth tests.
    """

    class layer(PloneSite):
        """Special test layer setting up pas.plugins.trustedproxyauth.
        """

        @classmethod
        def setUp(cls):
            """Sets up pas.plugins.trustedproxyauth so that the plugin
            is registered.
            """
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             pas.plugins.trustedproxyauth)
            fiveconfigure.debug_mode = False
            installPackage('pas.plugins.trustedproxyauth', quiet=True)

        @classmethod
        def tearDown(cls):
            """Method for tearing down the pas.plugins.trustedproxyauth layer.
            """
            pass


def test_suite():
    """Returns the pas.plugins.trustedproxyauth test suite.
    """

    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'README.txt', package='pas.plugins.trustedproxyauth',
            test_class=TestCase),

        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

