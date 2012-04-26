Tests for pas.plugins.trustedproxyauth
======================================

Test setup
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
    >>> form.getControl('Add').click()

    >>> browser.url
    'http://.../manage_main'
    >>> 'trusted_proxy_auth' in browser.contents
    True
    >>> plugin = self.portal.acl_users.trusted_proxy_auth
    >>> plugin
    <TrustedProxyAuthPlugin at /plone/acl_users/trusted_proxy_auth>


Test credentials extraction
---------------------------

    >>> plugin.login_header
    'HTTP_X_REMOTE_USER'
    >>> request = self.portal.REQUEST

If the request is missing either the header with the user name or the remote
ip nothing should be extracted.

    >>> plugin.extractCredentials(request)
    {}
    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> plugin.extractCredentials(request)
    {}
    >>> request.set('REMOTE_ADDR', '')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
    >>> plugin.extractCredentials(request)
    {}

If both headers are present, extraction should return the credentials.

    >>> request.set('REMOTE_ADDR', '207.46.197.32')
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
    >>> pprint(plugin.extractCredentials(request))
    {'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': ''}

Test lowercase logins

    >>> plugin.lowercase_logins
    False
    >>> plugin_config_url = "%s/acl_users/trusted_proxy_auth/manage_config" % self.portal.absolute_url()
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='lowercase_logins').value = True
    >>> form.getControl('Update').click()
    >>> plugin.lowercase_logins
    True
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

Test lowercase domain

    >>> plugin.lowercase_domain
    False
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='lowercase_logins').value = False
    >>> form.getControl(name='lowercase_domain').value = True
    >>> form.getControl('Update').click()
    >>> plugin.lowercase_logins
    False
    >>> plugin.lowercase_domain
    True
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'John.Doe@DOMAIN.LOCAL'
    >>> plugin.extractCredentials(request)['login']
    'John.Doe@domain.local'

Test strip nt domain

    >>> plugin.strip_nt_domain
    False
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='lowercase_domain').value = False
    >>> form.getControl(name='strip_nt_domain').value = True
    >>> form.getControl('Update').click()
    >>> plugin.lowercase_domain
    False
    >>> plugin.strip_nt_domain
    True
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'localdomain\\JOHN.DOE'
    >>> plugin.extractCredentials(request)['login']
    'JOHN.DOE'

Test strip ad domain

    >>> plugin.strip_ad_domain
    False
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='strip_nt_domain').value = False
    >>> form.getControl(name='strip_ad_domain').value = True
    >>> form.getControl('Update').click()
    >>> plugin.strip_nt_domain
    False
    >>> plugin.strip_ad_domain
    True
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE@domain.local'
    >>> plugin.extractCredentials(request)['login']
    'JOHN.DOE'

Test user name mapping

    >>> plugin.username_mapping
    []
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='username_mapping').value = 'john.doe:admin'
    >>> form.getControl('Update').click()
    >>> plugin.username_mapping
    ['john.doe:admin']
    >>> plugin._username_mapping['john.doe']
    'admin'
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
    >>> plugin.extractCredentials(request)['login']
    'admin'
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='username_mapping').value = 'john.doe:admin\nnobody:guest'
    >>> form.getControl('Update').click()
    >>> plugin.username_mapping
    ['john.doe:admin', 'nobody:guest']
    >>> plugin._username_mapping['nobody']
    'guest'


Test authentication
===================

    >>> def gencreds(plugin, user, addr, host=None):
    ...     """generate credentials for testing"""
    ...     data = {}
    ...     if plugin:
    ...         data['extractor'] = plugin.getId()
    ...     if not host:
    ...         host = addr
    ...     data['login'] = data['id'] = user
    ...     data['remote_address'] = addr
    ...     data['remote_host'] = host
    ...     return data

    >>> print plugin.authenticateCredentials({})
    None

Credentials from an unkown extractor are not accepted.

    >>> creds = gencreds(None, 'john.doe', '127.0.0.1')
    >>> pprint(creds)
    {'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '127.0.0.1',
     'remote_host': '127.0.0.1'}
    >>> print plugin.authenticateCredentials(creds)
    None
    >>> creds['extractor'] = 'peter'
    >>> print plugin.authenticateCredentials(creds)
    None

Credentials from our extractor are accepted.

    >>> creds = gencreds(plugin, 'john.doe', '127.0.0.1')
    >>> pprint(creds)
    {'extractor': 'trusted_proxy_auth',
     'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '127.0.0.1',
     'remote_host': '127.0.0.1'}
    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')

If the IP is not trusted, then it won't authenticate:

    >>> plugin.trusted_proxies
    ['127.0.0.1']
    >>> creds = gencreds(plugin, 'john.doe', '207.46.197.32')
    >>> pprint(creds)
    {'extractor': 'trusted_proxy_auth',
     'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': '207.46.197.32'}
    >>> print plugin.authenticateCredentials(creds)
    None

Either remote_address or remote_host needs to be trusted:

    >>> creds = gencreds(plugin, 'john.doe', '207.46.197.32', '127.0.0.1')
    >>> pprint(creds)
    {'extractor': 'trusted_proxy_auth',
     'id': 'john.doe',
     'login': 'john.doe',
     'remote_address': '207.46.197.32',
     'remote_host': '127.0.0.1'}

    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')

If no trusted proxies are defined, no authentication happens:

    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')
    >>> plugin.trusted_proxies = []
    >>> list(plugin.getProperty('trusted_proxies', ()))
    []
    >>> print plugin.authenticateCredentials(creds)
    None

If a hostname is set as trusted proxy, it's looked up

    >>> plugin.trusted_proxies = ['localhost']
    >>> plugin.trusted_proxies
    ['localhost']
    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')

If a name could not be looked up, it does not work:

    >>> plugin.trusted_proxies = ['foohost']
    >>> print plugin.authenticateCredentials(creds)
    None

Test user name verification

    >>> plugin.verify_login
    False
    >>> browser.open(plugin_config_url)
    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='trusted_proxies').value = '127.0.0.1'
    >>> form.getControl(name='verify_login').value = True
    >>> form.getControl('Update').click()
    >>> plugin.verify_login
    True
    >>> creds = gencreds(plugin, 'john.doe', '127.0.0.1')
    >>> print plugin.authenticateCredentials(creds)
    None
    >>> from Testing.ZopeTestCase import user_name
    >>> creds = gencreds(plugin, user_name, '127.0.0.1')
    >>> print plugin.authenticateCredentials(creds)
    ('test_user_1_', 'test_user_1_')
