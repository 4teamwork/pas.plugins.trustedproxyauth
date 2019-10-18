from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import IS_PLONE_5
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class PasLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'pas.plugins.trustedproxyauth')

    def setUpPloneSite(self, portal):
        if IS_PLONE_5:
            applyProfile(portal, 'plone.app.contenttypes:default')


PAS_FIXTURE = PasLayer()
PAS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PAS_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="pas.plugins.trustedproxyauth:functional")
