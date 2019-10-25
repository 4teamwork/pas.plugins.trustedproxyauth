import transaction
from pas.plugins.trustedproxyauth.testing import PAS_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest2 import TestCase


class FunctionalTestCase(TestCase):
    layer = PAS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
