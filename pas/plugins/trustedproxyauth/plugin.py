"""Provides the trusted proxy auth plugin.
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from Acquisition import aq_inner, aq_parent
from App.class_init import default__class_init__ as InitializeClass
from OFS.Cache import Cacheable
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList
from socket import gethostbyname, herror, gaierror
import logging
import re


logger = logging.getLogger('pas.plugins.trustedproxyauthauth')


IS_IP = re.compile("^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
                   "(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}$")


manage_addTrustedProxyAuthPlugin = PageTemplateFile(
    "www/addPlugin",
    globals(), __name__="manage_addTrustedProxyAuthPlugin")


def addTrustedProxyAuthPlugin(dispatcher, id, title="", REQUEST=None):
    """Add a TrustedProxy plugin to a PAS."""
    p=TrustedProxyAuthPlugin(id, title)
    dispatcher._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST.response.redirect(
            "%s/manage_workspace"
            "?manage_tabs_message=TrustedProxyAuthPlugin+plugin+added." % \
                dispatcher.absolute_url())


class TrustedProxyAuthPlugin(BasePlugin, Cacheable):
    """A PAS Plugin that authenticats users coming from a trusted proxy with
    their login name set in a request header.
    """

    meta_type = 'Trusted Proxy Authentication'
    security = ClassSecurityInfo()

    # ZMI tab for configuration page
    manage_options = (({'label': 'Configuration',
                        'action': 'manage_config'},)
                      + BasePlugin.manage_options
                      + Cacheable.manage_options
                     )

    security.declareProtected(ManagePortal, 'manage_config')
    manage_config = PageTemplateFile('www/config', globals(),
                                     __name__='manage_config')


    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title
        self.trusted_proxies = PersistentList(['127.0.0.1'])
        self.login_header = 'HTTP_X_REMOTE_USER'
        self.lowercase_logins = False
        self.lowercase_domain = False
        self.strip_nt_domain = False
        self.strip_ad_domain = False
        self.username_mapping = PersistentList()
        self._username_mapping = PersistentMapping()
        self.verify_login = False

    security.declarePrivate('_getUsernameMapping')
    def _getUsernameMapping(self):
        """Returns a dict containing the username
        mapping configuration.
        """
        mapping = PersistentMapping()
        for line in self.username_mapping:
            if not line.strip():
                continue
            login, mapped_login = line.strip().split(':')
            mapping[login] = mapped_login

        return mapping

    security.declarePrivate('_convertUsername')
    def _convertUsername(self, login):
        """Converts usernames based on the plugin configuration.
        This includes:
        - lowercasing
        - strip NT domain
        - strip AD domain
        """
        if self.lowercase_logins:
            login = login.lower()

        elif self.lowercase_domain and '@' in login:
            user, domain = login.rsplit('@', 1)
            login = '%s@%s' % (user, domain.lower())
            
        if self.strip_nt_domain:
            # DOMAIN\userid
            if '\\' in login:
                login = login.split('\\', 1)[1]

        if self.strip_ad_domain:
            # userid@domain.name
            if '@' in login:
                login = login.split('@', 1)[0]

        return login

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """Authenticate Credentials for Trusted Proxy
        """
        login = credentials.get('login')
        extractor = credentials.get('extractor')
        uid = credentials.get('id')
        remote_address = credentials.get('remote_address')
        remote_host = credentials.get('remote_host')

        if not self.trusted_proxies:
            logger.warn('authenticateCredentials ignoring request '
                        'because trusted_proxies is not configured')
            return None

        if (not login or extractor != self.getId()):
            logger.debug('authenticateCredentials ignoring request '
                         'from %r for %r/%r', extractor, uid, login)
            return None

        for idx, addr in enumerate(self.trusted_proxies):
            if IS_IP.match(addr):
                continue
            # If it's not an IP, then it's a hostname, and we need to
            # resolve it to an IP.
            try:
                # XXX Should we cache calls to gethostbyname? Supposedly
                # it can be quite expensive for a 'DNS Miss'.
                self.trusted_proxies[idx+1:idx+1] = [gethostbyname(addr)]
            except (herror, gaierror):
                logger.warn('Could not resolve hostname to address: %r', addr)

        for addr in (remote_address, remote_host):
            if addr in self.trusted_proxies:

                # Upgrade config for versions<1.1
                if not hasattr(self, 'verify_login'):
                    self.verify_login = False

                if self.verify_login:
                    pas = aq_parent(aq_inner(self))
                    if pas.getUserById(login) is None:
                        return None

                logger.debug('trusted user is %r:%r/%r',
                             addr, uid, login)
                return uid, login

        logger.warn('authenticateCredentials ignoring request '
                    'from %r - not in the list of trusted proxies (%r)',
                    (remote_address, remote_host), self.trusted_proxies)
        return None

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """Extract Credentials for Trusted Proxy
        """
        creds = {}
        login = request.get_header(self.login_header, '')

        # We need the IP of the Proxy, not the real client ip, thus we
        # can't use request.getClientAddr()
        remote_address = request.get('REMOTE_ADDR', '')

        if login and remote_address:

            login = self._convertUsername(login)

            # Upgrade username_mappings for versions<1.1
            if not hasattr(self, '_username_mapping'):
                self._username_mapping = self._getUsernameMapping()

            if login in self._username_mapping:
                login = self._username_mapping[login]

            creds['id'] = login
            creds['login'] = login
            creds['remote_address'] = remote_address
            creds['remote_host'] = request.get_header('REMOTE_HOST', '')

            logger.debug('extractCredentials has %r:%r',
                         remote_address, login)

        return creds

    security.declareProtected(ManagePortal, 'manage_updateConfig')
    @postonly
    def manage_updateConfig(self, REQUEST):
        """Update configuration of Trusted Proxy Authentication Plugin.
        """
        response = REQUEST.response

        self.trusted_proxies = PersistentList(
            [line.strip() for line in REQUEST.form.get(
             'trusted_proxies').split('\n') if line.strip()])
        self.login_header = REQUEST.form.get('login_header')

        for flag in ['lowercase_logins',
                     'lowercase_domain',
                     'strip_nt_domain',
                     'strip_ad_domain',
                     'verify_login']:
            if flag in REQUEST.form:
                setattr(self, flag, True)
            else:
                setattr(self, flag, False)
        
        self.username_mapping = PersistentList(
            [line.strip() for line in REQUEST.form.get(
             'username_mapping').split('\n') if line.strip()])
        self._username_mapping = self._getUsernameMapping()

        response.redirect('%s/manage_config?manage_tabs_message=%s' %
            (self.absolute_url(), 'Configuration+updated.'))


classImplements(TrustedProxyAuthPlugin,
                IAuthenticationPlugin,
                IExtractionPlugin)

InitializeClass(TrustedProxyAuthPlugin)
