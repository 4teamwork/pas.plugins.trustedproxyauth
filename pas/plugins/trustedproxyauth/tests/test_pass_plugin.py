from ftw.testbrowser import browsing
from ftw.testing import IS_PLONE_5
from pas.plugins.trustedproxyauth.testing import PAS_FUNCTIONAL_TESTING
from pas.plugins.trustedproxyauth.tests.base import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
import time
import transaction


class TestPasPlugin(FunctionalTestCase):

    layer = PAS_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestPasPlugin, self).setUp()
        self.grant('Manager')
        self.pass_add_url = '{}/acl_users/acl_users/manage_addProduct/pas.plugins.trustedproxyauth/manage_addTrustedProxyAuthPlugin'.format(
            self.portal.absolute_url())
        self.manage_config = '{}/acl_users/trusted_proxy_auth/manage_config'.format(
            self.portal.absolute_url())
        self.request = self.portal.REQUEST

        mtool = getToolByName(self.portal, 'portal_membership')
        self.portal.invokeFactory('Folder', 'Members', title='Members')
        mtool.setMemberareaCreationFlag()
        transaction.commit()

    @browsing
    def test_has_pas_plugin(self, browser):
        acl_users_url = '{}/acl_users/manage_main'.format(
            self.portal.absolute_url())
        browser.login()
        browser.open(acl_users_url)
        if IS_PLONE_5:
            plugins = [option.attrib['value']
                       for option in browser.css('select[name=":action"] option')]
        else:
            plugins = [option.attrib['value']
                       for option in browser.css('form input')]
        matching_plugin = filter(lambda x:
                                 'pas.plugins.trustedproxyauth' in x, plugins)

        self.assertTrue(matching_plugin,
                        'The plugin should be in the list of plugins.')

    @browsing
    def test_add_view(self, browser):
        pass_add_url = '{}/acl_users/acl_users/manage_addProduct/pas.plugins.trustedproxyauth/{}'.format(
            self.portal.absolute_url(),
            'manage_addTrustedProxyAuthPlugin')
        browser.login()
        browser.open(pass_add_url)
        settings_form = browser.css(
            'form[action="addTrustedProxyAuthPlugin"]').first

        # assert the values in the add form
        self.assertEqual(
            'trusted_proxy_auth',
            settings_form.css('input[name="id"]').first.attrib['value'],
            'The id is supposed to have "trusted_proxy_auth" as value.')

        with self.assertRaises(KeyError) as context:
            settings_form.css('input[name="title"]').first.attrib['value'],
        self.assertEqual("'value'", str(context.exception),
                         'The title is not supposed to have a value')

        settings_form.submit()

        # assert that the plugin was added
        self.assertIn('trusted_proxy_auth',
                      browser.css('form[name="objectItems"]').first.css('a').text,
                      'The pass plugin is supposed to be added now.')

        plugin = self.portal.acl_users.trusted_proxy_auth

        self.assertTrue(plugin, 'The plugin is supposed to be registered.')

    @browsing
    def test_credentials_extraction(self, browser):
        plugin = self.add_plugin_helper(browser)

        self.assertEqual('HTTP_X_REMOTE_USER', plugin.login_header)

        self.assertEqual({}, plugin.extractCredentials(self.request))

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.assertEqual({}, plugin.extractCredentials(self.request))

        self.request.set('REMOTE_ADDR', '')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
        self.assertEqual({}, plugin.extractCredentials(self.request))

        self.request.set('REMOTE_ADDR', '')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
        self.assertEqual({}, plugin.extractCredentials(self.request))

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'
        self.assertEqual({'id': 'john.doe', 'login': 'john.doe',
                          'remote_address': '207.46.197.32',
                          'remote_host': ''},
                         plugin.extractCredentials(self.request))

    @browsing
    def test_lowercase_logins(self, browser):
        plugin = self.add_plugin_helper(browser)
        self.assertFalse(plugin.lowercase_logins)

        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'lowercase_logins': True}).submit()
        browser.open(self.manage_config)
        self.assertEqual('checked',
                         browser.css('input[name="lowercase_logins"]').first.attrib['checked'])

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE'
        self.assertEqual({'id': 'john.doe', 'login': 'john.doe',
                          'remote_address': '207.46.197.32',
                          'remote_host': ''},
                         plugin.extractCredentials(self.request))

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'localdomain\\JOHN.DOE'

        self.assertEqual({'id': 'localdomain\\john.doe',
                          'login': 'localdomain\\john.doe',
                          'remote_address': '207.46.197.32',
                          'remote_host': ''},
                         plugin.extractCredentials(self.request))

    @browsing
    def test_lowercase_domain(self, browser):
        plugin = self.add_plugin_helper(browser)
        self.assertFalse(plugin.lowercase_domain)

        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'lowercase_domain': True}).submit()

        self.assertFalse(plugin.lowercase_logins)
        self.assertTrue(plugin.lowercase_domain)

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'John.Doe@DOMAIN.LOCAL'
        self.assertEqual('John.Doe@domain.local', plugin.extractCredentials(self.request)['login'])

    @browsing
    def test_strip_nt_domain(self, browser):
        plugin = self.add_plugin_helper(browser)
        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'strip_nt_domain': True}).submit()

        self.assertFalse(plugin.lowercase_domain)
        self.assertTrue(plugin.strip_nt_domain)

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'localdomain\\JOHN.DOE'

        self.assertEqual('JOHN.DOE', plugin.extractCredentials(self.request)['login'])

    @browsing
    def test_strip_ad_domain(self, browser):
        plugin = self.add_plugin_helper(browser)
        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'strip_ad_domain': True}).submit()

        self.assertFalse(plugin.strip_nt_domain)
        self.assertTrue(plugin.strip_ad_domain)

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'JOHN.DOE@domain.local'

        self.assertEqual('JOHN.DOE', plugin.extractCredentials(self.request)['login'])

    @browsing
    def test_user_name_mapping(self, browser):
        plugin = self.add_plugin_helper(browser)
        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'username_mapping': 'john.doe:admin'}).submit()

        self.assertEqual(['john.doe:admin'], plugin.username_mapping)
        self.assertEqual('admin', plugin._username_mapping['john.doe'])

        self.request.set('REMOTE_ADDR', '207.46.197.32')
        self.request.environ['HTTP_X_REMOTE_USER'] = 'john.doe'

        self.assertEqual('admin', plugin.extractCredentials(self.request)['login'])

        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'username_mapping': 'john.doe:admin\nnobody:guest'}).submit()

        self.assertEqual(['john.doe:admin', 'nobody:guest'], plugin.username_mapping)
        self.assertEqual('admin', plugin._username_mapping['john.doe'])
        self.assertEqual('guest', plugin._username_mapping['nobody'])

    @browsing
    def test_authentication(self, browser):
        plugin = self.add_plugin_helper(browser)
        self.assertFalse(plugin.authenticateCredentials({}))

        creds = self.gencreds(None, 'john.doe', '127.0.0.1')
        self.assertEqual({'login': 'john.doe', 'remote_host': '127.0.0.1',
                          'id': 'john.doe', 'remote_address': '127.0.0.1'},
                         creds)
        self.assertFalse(plugin.authenticateCredentials(creds))

        creds['extractor'] = 'peter'
        self.assertFalse(plugin.authenticateCredentials(creds))

    @browsing
    def test_credentials_from_extractor_are_accepted(self, browser):
        plugin = self.add_plugin_helper(browser)

        creds = self.gencreds(plugin, 'john.doe', '127.0.0.1')
        self.assertEqual({'extractor': 'trusted_proxy_auth', 'id': 'john.doe',
                          'login': 'john.doe', 'remote_address': '127.0.0.1',
                          'remote_host': '127.0.0.1'},
                         creds)

        self.assertEqual(('john.doe', 'john.doe'), plugin.authenticateCredentials(creds))

    @browsing
    def test_wont_auth_if_ip_not_trusted(self, browser):
        plugin = self.add_plugin_helper(browser)
        self.assertEqual(['127.0.0.1'], plugin.trusted_proxies)

        creds = self.gencreds(plugin, 'john.doe', '207.46.197.32')

        self.assertEqual({'extractor': 'trusted_proxy_auth', 'id': 'john.doe',
                          'login': 'john.doe',
                          'remote_address': '207.46.197.32',
                          'remote_host': '207.46.197.32'},
                         creds)

        self.assertFalse(plugin.authenticateCredentials(creds))

    @browsing
    def test_remote_address_or_remote_host_must_be_trusted(self, browser):
        plugin = self.add_plugin_helper(browser)
        creds = self.gencreds(plugin, 'john.doe', '207.46.197.32', '127.0.0.1')

        self.assertEqual({'extractor': 'trusted_proxy_auth', 'id': 'john.doe',
                          'login': 'john.doe',
                          'remote_address': '207.46.197.32',
                          'remote_host': '127.0.0.1'},
                         creds)
        self.assertEqual(('john.doe', 'john.doe'),
                         plugin.authenticateCredentials(creds))

    @browsing
    def test_no_proxies_no_auth(self, browser):
        plugin = self.add_plugin_helper(browser)
        creds = self.gencreds(plugin, 'john.doe', '207.46.197.32', '127.0.0.1')
        self.assertEqual(('john.doe', 'john.doe'),
                         plugin.authenticateCredentials(creds))

        plugin.trusted_proxies = []
        self.assertFalse(plugin.getProperty('trusted_proxies', ()))
        self.assertFalse(plugin.authenticateCredentials(creds))

    @browsing
    def test_lookup_if_hostname_set_as_trusted_proxy(self, browser):
        plugin = self.add_plugin_helper(browser)
        creds = self.gencreds(plugin, 'john.doe', '207.46.197.32', '127.0.0.1')
        plugin.trusted_proxies = ['localhost']
        self.assertEqual(['localhost'], plugin.trusted_proxies)

        self.assertEqual(('john.doe', 'john.doe'),
                         plugin.authenticateCredentials(creds))

    @browsing
    def test_no_lookup_no_auth(self, browser):
        plugin = self.add_plugin_helper(browser)
        creds = self.gencreds(plugin, 'john.doe', '207.46.197.32', '127.0.0.1')
        plugin.trusted_proxies = ['foohost']

        self.assertFalse(plugin.authenticateCredentials(creds))

    @browsing
    def test_user_name_verification(self, browser):
        plugin = self.add_plugin_helper(browser)
        self.assertFalse(plugin.verify_login)

        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'trusted_proxies': '127.0.0.1',
                   'verify_login': True}).submit()
        self.assertTrue(plugin.verify_login)

        creds = self.gencreds(plugin, 'john.doe', '127.0.0.1')
        self.assertFalse(plugin.authenticateCredentials(creds))

        creds = self.gencreds(plugin, TEST_USER_ID, '127.0.0.1')
        self.assertEqual(('test_user_1_', 'test_user_1_'), plugin.authenticateCredentials(creds))

    @browsing
    def test_plone_login_emulation(self, browser):
        plugin = self.add_plugin_helper(browser)
        self.assertEqual(-1, plugin.plone_login_timeout)

        browser.open(self.manage_config)
        form = browser.css('form').first
        form.fill({'plone_login_timeout': '2'}).submit()
        self.assertEqual(2, plugin.plone_login_timeout)

        userid = 'jack'
        mtool = getToolByName(self.portal, 'portal_membership')
        self.portal.acl_users.userFolderAddUser(userid, 'secret', [], [], [])
        self.assertFalse(mtool.getHomeFolder(id=userid))

        user = mtool.getMemberById(userid)
        login_time = user.getProperty('login_time')
        self.assertEqual('2000-01-01T00:00:00', login_time.ISO())

        creds = self.gencreds(plugin, userid, '127.0.0.1')
        self.assertEqual(('jack', 'jack'), plugin.authenticateCredentials(creds))
        self.assertTrue(self.portal.Members.jack,
                        'There is supposed to be a user in the member folder.')

        login_time_updated = mtool.getMemberById(userid).getProperty('login_time')
        self.assertTrue(login_time_updated > login_time,
                        'Login updated should be greater than login time.')

        self.assertEqual(('jack', 'jack'), plugin.authenticateCredentials(creds))
        self.assertTrue(mtool.getMemberById(
            userid).getProperty('login_time') == login_time_updated,
            'Login time should be equal to login_time_updated.')

        time.sleep(2)
        self.assertEqual(('jack', 'jack'), plugin.authenticateCredentials(creds))
        self.assertTrue(mtool.getMemberById(
            userid).getProperty('login_time') > login_time_updated,
            'Login time should be greater than updated.')

    def add_plugin_helper(self, browser):
        # add and define plugin
        browser.login()
        browser.open(self.pass_add_url)
        settings_form = browser.css(
            'form[action="addTrustedProxyAuthPlugin"]').first
        settings_form.submit()
        plugin = self.portal.acl_users.trusted_proxy_auth

        return plugin

    @staticmethod
    def gencreds(plugin, user, addr, host=None):
        """generate credentials for testing"""
        data = {}
        if plugin:
            data['extractor'] = plugin.getId()
        if not host:
            host = addr
        data['login'] = data['id'] = user
        data['remote_address'] = addr
        data['remote_host'] = host
        return data
