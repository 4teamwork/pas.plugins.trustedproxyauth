from AccessControl.Permissions import manage_users
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService import registerMultiPlugin

import plugin

manage_add_trustedproxyauth_form = PageTemplateFile('browser/add_plugin',
                            globals(), __name__='manage_add_trustedproxyauth_form' )


def manage_add_trustedproxyauth_helper( dispatcher, id, title=None, REQUEST=None ):
    """Add an trustedproxyauth Helper to the PluggableAuthentication Service."""

    sp = plugin.TrustedproxyHelper( id, title )
    dispatcher._setObject( sp.getId(), sp )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'trustedproxyauthHelper+added.'
                                      % dispatcher.absolute_url() )


def register_trustedproxyauth_plugin():
    try:
        registerMultiPlugin(plugin.TrustedproxyHelper.meta_type)
    except RuntimeError:
        # make refresh users happy
        pass


def register_trustedproxyauth_plugin_class(context):
    context.registerClass(plugin.TrustedproxyHelper,
                          permission = manage_users,
                          constructors = (manage_add_trustedproxyauth_form,
                                          manage_add_trustedproxyauth_helper),
                          visibility = None,
                          icon='browser/icon.gif'
                         )
