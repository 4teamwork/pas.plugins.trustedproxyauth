Tests for pas.plugins.trustedproxyauth

test setup
----------

    >>> from pprint import pprint
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

we add the plugin:

    >>> form.getControl('Add').click()

    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='id').value
    'trusted_proxy_auth'
    >>> form.getControl(name='title').value
    ''
    >>> form.getControl(name='trusted_proxies:list').value
    '127.0.0.1'
    >>> form.getControl(name='login_header').value
    'HTTP_X_REMOTE_USER'
    >>> form.getControl(name='lowercase_logins').value
    ['1']

    >>> form.getControl(name='title').value = 'Trusted Proxy Auth'
    >>> form.getControl('add plugin').click()

    >>> browser.url
    'http://.../manage_main'
    >>> 'trusted_proxy_auth' in browser.contents
    True


test extracting credentials:

    >>> plugin = self.portal.acl_users.trusted_proxy_auth
    >>> plugin
    <TrustedProxyAuthPlugin at /plone/acl_users/trusted_proxy_auth>
    >>> plugin.getProperty('login_header')
    'HTTP_X_REMOTE_USER'

    >>> request = self.portal.REQUEST
    >>> request
    <HTTPRequest, URL=http://nohost>

    >>> request.get('REMOTE_ADDR')
    ''
    >>> plugin.extractCredentials(request)
    {}

    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> plugin.extractCredentials(request)
    {}

    >>> request.set('REMOTE_ADDR', '')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
    >>> plugin.extractCredentials(request)
    {}

    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': ''}

    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': ''}

    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'localdomain\\JOHN.DOE'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'localdomain\\john.doe',
     'login': 'localdomain\\john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': ''}

    >>> plugin.strip_nt_domain = True
    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'localdomain\\JOHN.DOE'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': ''}
    >>> plugin.strip_nt_domain = False

    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE@domain.local'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'john.doe@domain.local',
     'login': 'john.doe@domain.local',
     'remote_address': '207.46.197.32',
     'remote_host': ''}

    >>> plugin.strip_ad_domain = True
    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE@domain.local'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': ''}
    >>> plugin.strip_ad_domain = True
