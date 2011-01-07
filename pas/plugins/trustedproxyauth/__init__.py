from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from AccessControl.Permissions import manage_users
from pas.plugins.trustedproxyauth import plugin


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    registerMultiPlugin(plugin.TrustedProxyAuthPlugin.meta_type)
    context.registerClass(plugin.TrustedProxyAuthPlugin,
            permission=manage_users,
            constructors=(plugin.manage_addTrustedProxyAuthPlugin,
                          plugin.addTrustedProxyAuthPlugin),
            visibility=None)
