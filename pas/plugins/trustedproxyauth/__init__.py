
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
    from AccessControl.Permissions import manage_users
    from pas.plugins.trustedproxyauth import plugin


    registerMultiPlugin(plugin.TrustedProxyAuthPlugin.meta_type)
    context.registerClass(plugin.TrustedProxyAuthPlugin,
            permission=manage_users,
            constructors=(plugin.manage_addTrustedProxyAuthPlugin,
                          plugin.addTrustedProxyAuthPlugin),
            visibility=None)
