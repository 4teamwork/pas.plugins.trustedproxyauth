Tests for pas.plugins.trustedproxyauth

test setup
----------

    >>> from Testing.ZopeTestCase import user_password
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()

Plugin setup
------------

    >>> acl_users_url = "%s/acl_users" % self.portal.absolute_url()
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % ('portal_owner', user_password))
    >>> browser.open("%s/manage_main" % acl_users_url)
    >>> browser.url
    'http://nohost/plone/acl_users/manage_main'
    >>> form = browser.getForm(index=0)
    >>> select = form.getControl(name=':action')

pas.plugins.trustedproxyauth should be in the list of installable plugins:

    >>> 'Trusted Proxy Authentication' in select.displayOptions
    True

and we can select it:

    >>> select.getControl('Trusted Proxy Authentication').click()
    >>> select.displayValue
    ['Trusted Proxy Authentication']
    >>> select.value
    ['manage_addProduct/pas.plugins.trustedproxyauth/manage_addTrustedProxyAuthPlugin']

we add 'Trustedproxy Helper' to acl_users:

    >>> from pas.plugins.trustedproxyauth.plugin import TrustedProxyAuthPlugin
    >>> myplugin = TrustedProxyAuthPlugin('myplugin', 'Trustedproxy Plugin')
    >>> self.portal.acl_users['myplugin'] = myplugin

and so on. Continue your tests here

    >>> 'ALL OK'
    'ALL OK'

