Tests for pas.plugins.trustedproxy

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

pas.plugins.trustedproxy should be in the list of installable plugins:

    >>> 'Trustedproxy Helper' in select.displayOptions
    True

and we can select it:

    >>> select.getControl('Trustedproxy Helper').click()
    >>> select.displayValue
    ['Trustedproxy Helper']
    >>> select.value
    ['manage_addProduct/pas.plugins.trustedproxy/manage_add_trustedproxy_helper_form']

we add 'Trustedproxy Helper' to acl_users:

    >>> from pas.plugins.trustedproxy.plugin import TrustedproxyHelper
    >>> myhelper = TrustedproxyHelper('myplugin', 'Trustedproxy Helper')
    >>> self.portal.acl_users['myplugin'] = myhelper

and so on. Continue your tests here

    >>> 'ALL OK'
    'ALL OK'

