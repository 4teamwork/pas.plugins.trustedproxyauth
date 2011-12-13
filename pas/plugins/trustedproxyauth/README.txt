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
    >>> form.getControl(name='username_mapping:list').value
    ''

    >>> form.getControl(name='title').value = 'Trusted Proxy Auth'
    >>> form.getControl('add plugin').click()

    >>> browser.url
    'http://.../manage_main'
    >>> 'trusted_proxy_auth' in browser.contents
    True


test extracting credentials:
============================

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

We can lowercase the AD domain part of the login.

    >>> plugin.lowercase_domain = True
    >>> plugin.lowercase_logins = False
    >>> plugin.strip_ad_domain = False
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE@DOMAIN.LOCAL'
    >>> plugin.extractCredentials(request)['login']
    'JOHN.DOE@domain.local'

We can lowercase the whole login

    >>> plugin.lowercase_logins = True
    >>> plugin.lowercase_domain = False
    >>> request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE@DOMAIN.LOCAL'
    >>> plugin.extractCredentials(request)['login']
    'john.doe@domain.local'


test authentication
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

If the extractor is wrong, then nothing is done:

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

If the extractor is right, authentication will happen:

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

    >>> list(plugin.getProperty('trusted_proxies', ()))
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
    >>> list(plugin.getProperty('trusted_proxies', ()))
    ['localhost']
    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')

If a name could not be looked up, it does not work:

    >>> plugin.trusted_proxies = ['foohost']
    >>> print plugin.authenticateCredentials(creds)
    None

Reset the trusted proxies property:

    >>> plugin.trusted_proxies = ['127.0.0.1']

Username mapping
================

It's possible to map a AD username to a plone username. Let's test
that. We wan't to map jane.doe to john.doe. This should not work without
configuring the username_mapping:

    >>> creds = gencreds(plugin, 'jane.doe', '127.0.0.1')
    >>> print plugin.authenticateCredentials(creds)
    ('jane.doe', 'jane.doe')


When we configure the mapping now, it should work properly:

    >>> browser.open('%s/trusted_proxy_auth/manage_propertiesForm' % acl_users_url)
    >>> browser.url
    'http://nohost/plone/acl_users/trusted_proxy_auth/manage_propertiesForm'

    >>> form = browser.getForm(index=0)
    >>> form.getControl(name='username_mapping:lines').value
    ''
    >>> form.getControl(name='username_mapping:lines').value = 'jane.doe:john.doe'
    >>> form.getControl('Save Changes').click()
    >>> browser.url
    'http://nohost/plone/acl_users/trusted_proxy_auth'
    >>> 'Saved changes.' in browser.contents
    True

    >>> pprint(plugin._getUsernameMapping())
    {'jane.doe': 'john.doe'}

    >>> creds = gencreds(plugin, 'jane.doe', '127.0.0.1')
    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')

The strip_nt_domain option should also work:

    >>> plugin.username_mapping = ['localdomain\\JANE.DOE:john.doe']
    >>> print plugin.authenticateCredentials(creds)
    ('jane.doe', 'jane.doe')

    >>> plugin.strip_nt_domain = True
    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')
    >>> plugin.strip_nt_domain = False

And also the strip_ad_domain option:

    >>> plugin.strip_ad_domain = False
    >>> plugin.username_mapping = ['JANE.DOE@domain.local:john.doe']
    >>> pprint(plugin._getUsernameMapping())
    {'jane.doe@domain.local': 'john.doe'}
    >>> print plugin.authenticateCredentials(creds)
    ('jane.doe', 'jane.doe')

    >>> plugin.strip_ad_domain = True
    >>> pprint(plugin._getUsernameMapping())
    {'jane.doe': 'john.doe'}
    >>> print plugin.authenticateCredentials(creds)
    ('john.doe', 'john.doe')
    >>> plugin.strip_ad_domain = False

    