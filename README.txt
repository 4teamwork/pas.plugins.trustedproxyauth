Introduction
============

``pas.plugins.trustedproxyauth`` is a PAS plugin for Plone/Zope2 which
authenticates requests coming from a trusted reverse proxy where the user name
is provided by a HTTP header.

The idea is to delegate user authentication to a reverse proxy (e.g. Apache
with mod_auth_kerb) which is placed in front of the Zope instance. For any
request coming from the reverse proxy, the user name is extracted from a
HTTP header (typically ``X_REMOTE_USER``) that was set by the authenticating
proxy server.


Installation
============

- Add ``pas.plugins.trustedproxyauth`` to the list of eggs in your buildout.
  Then rerun buildout and restart your instance.

- In the ZMI go to your acl_users folder and select `Trusted Proxy
  Authentication` from the `Add` menu.

- Activate the `Authentiation` and `Extraction` functionality on the
  `Activate` tab. You may want to change the order of the extraction and
  authentication plugins by moving `Trusted Proxy Authentication` on top.


Options
=======

The following mandatory settings must be configured:

Trusted Proxy IPs
    Specify the ip address of your reverse proxy here. Only requests coming
    from a trusted ip will be considered for user name extraction. You can
    specify multiple ip addresses. Defaults to 127.0.0.1.

Login Name Header
    The name of the HTTP header containing the users login name. This header
    must be set by the authentication proxy. Defaults to ``X_REMOTE_USER``.

Require Exisiting PAS User
    If disabled, any login name provided in the header is authenticated
    (recommended). If enabled, only login names that can be looked up with PAS
    are authenticated.

``pas.plugins.trustedproxyauth`` supports user name transformations that may
be needed in combination with some reverse proxies. The following options are
supported:

Lowercase Login
    Transform the extracted login name to lowercase.

Lowercase Domain
    Transform the domain name part of the extracted login name to lowercase.
    This is useful when using Kerberos authentication and the user id consists
    of ``userid@REALM``.

Strip NT Domain
    Remove the NT domain part from the extracted user name. All user names
    in the form ``DOMAIN\userid`` are transformed to ``userid``.

Strip AD Domain
    Remove the AD domain part from the extracted user name. All user names
    in the form ``userid@domain`` are transformed to ``userid``.

User Name Mapping
    Specify a custom user name mapping by providing the extracted user name
    and the mapped user name separated by colon per line.

    Example::

        user1:guest
        user2:admin


Links
=====

- Main github project repository:
  https://github.com/4teamwork/pas.plugins.trustedproxyauth
- Issue tracker:
  https://github.com/4teamwork/pas.plugins.trustedproxyauth/issues
- Package on pypi: http://pypi.python.org/pypi/pas.plugins.trustedproxyauth
- Continuous Integration:
  https://jenkins.4teamwork.ch/job/pas.plugins.trustedproxyauth/


Copyright and License
=====================

This package is copyright by `4teamwork GmbH <http://www.4teamwork.ch/>`_

``pas.plugins.trustedproxyauth`` is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
