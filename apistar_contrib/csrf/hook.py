"""
Copied from Django
https://github.com/django/django/blob/master/django/middleware/csrf.py

Cross Site Request Forgery Middleware.

This module provides a middleware that implements protection
against request forgeries from other sites.
"""
from urllib.parse import urlparse

from apistar import App, http, exceptions
from markupsafe import Markup
from werkzeug.http import dump_cookie, parse_cookie

from apistar_contrib.csrf import utils
from apistar_contrib.csrf.settings import CsrfSettings

REASON_NO_REFERER = "Referer checking failed - no Referer."
REASON_BAD_REFERER = "Referer checking failed - %s does not match any trusted origins."
REASON_NO_CSRF_COOKIE = "CSRF cookie not set."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."
REASON_MALFORMED_REFERER = "Referer checking failed - Referer is malformed."
REASON_INSECURE_REFERER = "Referer checking failed - Referer is insecure while host is secure."


def get_token(request: http.Request) -> str:
    """
    Get a CSRF token
    """
    if hasattr(request, '_csrf_hook'):
        return request._csrf_hook.get_token()


def rotate_token(request: http.Request):
    """
    Change the CSRF token in use for a request - should be done on login
    for security purposes.
    """
    if hasattr(request, '_csrf_hook'):
        request._csrf_hook.rotate_token()


class EnforceCsrfHook:
    """
    Require a present and correct CSRF_TOKEN_FIELD_NAME for POST requests that
    have a CSRF cookie, and set an outgoing CSRF cookie.

    This middleware should be used in conjunction with the {{ csrf_token() }}
    template tag.
    """
    def __init__(self, settings=None):
        self.settings = CsrfSettings(settings or {})
        self.csrf_token = None
        self.csrf_token_used = False
        self.csrf_cookie_needs_reset = False

    def get_token(self) -> str:
        if self.csrf_token is None:
            csrf_secret = utils._get_new_csrf_string()
            self.csrf_token = utils._salt_cipher_secret(csrf_secret)
        else:
            csrf_secret = utils._unsalt_cipher_token(self.csrf_token)
        self.csrf_token_used = True
        return utils._salt_cipher_secret(csrf_secret)

    def rotate_token(self):
        self.csrf_token = utils._get_new_csrf_token()
        self.csrf_token_used = True
        self.csrf_cookie_needs_reset = True

    def csrf_token_template_hook(self):
        return Markup('<input type="hidden" name="{}" value="{}"/>'
                      .format(self.settings.CSRF_TOKEN_FIELD_NAME, self.get_token()))

    def _accept(self):
        return None

    def _reject(self, reason):
        raise exceptions.Forbidden(reason)

    def _load_token(self, cookie_header):
        if not cookie_header:
            return

        cookies = parse_cookie(cookie_header)
        try:
            cookie_token = cookies[self.settings.CSRF_COOKIE_NAME]
        except KeyError:
            return None

        csrf_token = utils._sanitize_token(cookie_token)
        if csrf_token != cookie_token:
            # Cookie token needed to be replaced;
            # the cookie needs to be reset.
            self.csrf_cookie_needs_reset = True
        return csrf_token

    def _set_token(self, response):
        cookie = dump_cookie(
            self.settings.CSRF_COOKIE_NAME,
            self.csrf_token,
            max_age=self.settings.CSRF_COOKIE_AGE,
            domain=self.settings.CSRF_COOKIE_DOMAIN,
            path=self.settings.CSRF_COOKIE_PATH,
            secure=self.settings.CSRF_COOKIE_SECURE,
            httponly=self.settings.CSRF_COOKIE_HTTPONLY,
        )
        response.headers['set-cookie'] = cookie
        # Set the Vary header since content varies with the CSRF cookie.
        utils.patch_vary_headers(response, ('Cookie',))

    def on_request(self, app: App, request: http.Request, cookie: http.Header, data: http.RequestData,
                   server_scheme: http.Scheme, server_host: http.Host, server_port: http.Port):
        request._csrf_hook = self
        utils.update_global_template_context(app, csrf_token=self.csrf_token_template_hook)

        csrf_token = self._load_token(cookie)
        if csrf_token is not None:
            # Use same token next time.
            self.csrf_token = csrf_token

        # Assume that anything not defined as 'safe' by RFC7231 needs protection
        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                # Mechanism to turn off CSRF checks for test suite.
                # It comes after the creation of CSRF cookies, so that
                # everything else continues to work exactly the same
                # (e.g. cookies are sent, etc.), but before any
                # branches that call reject().
                return self._accept()

            if server_scheme == 'https':
                # Suppose user visits http://example.com/
                # An active network attacker (man-in-the-middle, MITM) sends a
                # POST form that targets https://example.com/detonate-bomb/ and
                # submits it via JavaScript.
                #
                # The attacker will need to provide a CSRF cookie and token, but
                # that's no problem for a MITM and the session-independent
                # secret we're using. So the MITM can circumvent the CSRF
                # protection. This is true for any HTTP connection, but anyone
                # using HTTPS expects better! For this reason, for
                # https://example.com/ we need additional protection that treats
                # http://example.com/ as completely untrusted. Under HTTPS,
                # Barth et al. found that the Referer header is missing for
                # same-domain requests in only about 0.2% of cases or less, so
                # we can use strict Referer checking.
                referer = request.headers.get('HTTP_REFERER')
                if referer is None:
                    return self._reject(REASON_NO_REFERER)

                referer = urlparse(referer)

                # Make sure we have a valid URL for Referer.
                if '' in (referer.scheme, referer.netloc):
                    return self._reject(REASON_MALFORMED_REFERER)

                # Ensure that our Referer is also secure.
                if referer.scheme != 'https':
                    return self._reject(REASON_INSECURE_REFERER)

                # If there isn't a CSRF_COOKIE_DOMAIN, require an exact match
                # match on host:port. If not, obey the cookie rules.
                good_referer = self.settings.CSRF_COOKIE_DOMAIN
                if good_referer is not None:
                    if server_port not in ('443', '80'):
                        good_referer = '%s:%s' % (good_referer, server_port)
                else:
                    if server_port not in ('443', '80'):
                        good_referer = '%s:%s' % (server_host, server_port)
                    else:
                        good_referer = server_host

                # Here we generate a list of all acceptable HTTP referers,
                # including the current host since that has been validated
                # upstream.
                good_hosts = list(self.settings.CSRF_TRUSTED_ORIGINS)
                good_hosts.append(good_referer)

                if not any(utils.is_same_domain(referer.netloc, host) for host in good_hosts):
                    reason = REASON_BAD_REFERER % referer.geturl()
                    return self._reject(reason)

            if self.csrf_token is None:
                # No CSRF cookie. For POST requests, we insist on a CSRF cookie,
                # and in this way we can avoid all CSRF attacks, including login
                # CSRF.
                return self._reject(REASON_NO_CSRF_COOKIE)

            # Check non-cookie token for match.
            request_csrf_token = ""
            if request.method == "POST" and data:
                request_csrf_token = data.get(self.settings.CSRF_TOKEN_FIELD_NAME, '')

            if request_csrf_token == "":
                # Fall back to X-CSRFToken, to make things easier for AJAX,
                # and possible for PUT/DELETE.
                request_csrf_token = request.headers.get(self.settings.CSRF_HEADER_NAME, '')

            request_csrf_token = utils._sanitize_token(request_csrf_token)
            if not utils._compare_salted_tokens(request_csrf_token, self.csrf_token or ''):
                return self._reject(REASON_BAD_TOKEN)

        return self._accept()

    def on_response(self, response: http.Response, exc: Exception):
        if exc is not None:
            raise exc

        if self.csrf_token_used or self.csrf_cookie_needs_reset:
            # Set the CSRF cookie even if it's already set, so we renew
            # the expiry timer.
            self._set_token(response)
