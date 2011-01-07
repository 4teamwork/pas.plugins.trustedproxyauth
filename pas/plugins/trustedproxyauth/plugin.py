import re
import logging
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from OFS.Cache import Cacheable
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from socket import getaddrinfo, herror

logger = logging.getLogger('pas.plugins.trustedproxyauthauth')

IS_IP = re.compile("^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
                   "(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}$")


manage_addTrustedProxyAuthPlugin = PageTemplateFile("www/addPlugin",
    globals(), __name__="manage_addTrustedProxyAuthPlugin")


def addTrustedProxyAuthPlugin(dispatcher, id, title="", trusted_proxies=(),
                              login_header='', lowercase_logins= False,
                              REQUEST=None):
    """Add a TrustedProxy plugin to a PAS."""
    p=TrustedProxyAuthPlugin(id, title, trusted_proxies, login_header,
                             lowercase_logins)
    dispatcher._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST.response.redirect("%s/manage_workspace"
                "?manage_tabs_message=TrustedProxyAuthPlugin+plugin+added." %
                dispatcher.absolute_url())


class TrustedProxyAuthPlugin(BasePlugin, Cacheable):
    """A PAS Plugin that authenticats users coming from a trusted proxy with
       their login name set in a request header.
    """

    meta_type = 'Trusted Proxy Authentication'
    security = ClassSecurityInfo()

    _properties = BasePlugin._properties + (
            { 'id'    : 'trusted_proxies',
              'label' : 'IP addresses of trusted proxies',
              'type'  : 'lines',
              'mode'  : 'w',
            },
            { 'id'    : 'login_header',
              'label' : 'HTTP header containing the login name',
              'type'  : 'string',
              'mode'  : 'w',
            },
            { 'id'    : 'lowercase_logins',
              'label' : 'Transform login names to lowercase',
              'type'  : 'boolean',
              'mode'  : 'w',
            },
    )


    def __init__(self, id, title=None, trusted_proxies=None,
                 login_header=None, lowercase_logins=False):
        self._setId(id)
        self.title = title
        self.trusted_proxies = trusted_proxies
        self.login_header = login_header
        self.lowercase_logins = lowercase_logins

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """Authenticate Credentials for Trusted Proxy
        """
        trusted_proxies = list(self.getProperty('trusted_proxies', ()))
        login = credentials.get('login')
        extractor = credentials.get('extractor')
        uid = credentials.get('id')
        remote_address = credentials.get('remote_address')
        remote_host = credentials.get('remote_host')

        if not trusted_proxies:
            logger.warn('authenticateCredentials ignoring request '
                        'because trusted_proxies is not configured')
            return None

        if (not login or extractor != self.getId()):
            logger.debug('authenticateCredentials ignoring request '
                         'from %r for %r/%r', extractor, uid, login)
            return None

        for idx, addr in enumerate(trusted_proxies):
            if IS_IP.match(addr):
                continue
            # If it's not an IP, then it's a hostname, and we need to
            # resolve it to an IP.
            try:
                # XXX Should we cache calls to getaddrinfo? Supposedly
                # it can be quite expensive for a 'DNS Miss'.
                trusted_proxies[idx+1:idx+1] = [t[-1][0] for t in getaddrinfo(addr, None)]
            except herror:
                logger.debug('Could not resolve hostname to address: %r', addr)

        for addr in (remote_address, remote_host):
            if addr in trusted_proxies:
                logger.debug('trusted user is %r:%r/%r', 
                             addr, uid, login)
                return uid, login

        logger.warn('authenticateCredentials ignoring request '
                    'from %r - not in the list of trusted proxies (%r)',
                    (remote_address, remote_host), trusted_proxies)
        return None

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """Extract Credentials for Trusted Proxy
        """
        creds = {}
        login_header = self.getProperty('login_header', 'X_REMOTE_USER')
        login = request.get_header(login_header, '')

        # We need the IP of the Proxy, not the real client ip, thus we
        # can't use request.getClientAddr()
        remote_address = request.get('REMOTE_ADDR', '')

        if login and remote_address:
            if self.getProperty('lowercase_logins', False):
                login = login.lower()
            # `login` and `id` might be overriden below.
            creds['id'] = login
            creds['login'] = login
            creds['remote_address'] = remote_address
            creds['remote_host'] = request.get_header('REMOTE_HOST', '')

            logger.debug('extractCredentials has %r:%r',
                         remote_address, login)

        return creds



classImplements(TrustedProxyAuthPlugin,
                IAuthenticationPlugin,
                IExtractionPlugin)

InitializeClass(TrustedProxyAuthPlugin)
