from apistar import types, validators


# Settings for CSRF cookie.
class CsrfSettings(types.Type):
    CSRF_COOKIE_NAME = validators.String(default='csrftoken')
    CSRF_COOKIE_AGE = validators.Integer(default=60 * 60 * 24 * 7 * 52)
    CSRF_COOKIE_DOMAIN = validators.String(allow_null=True)
    CSRF_COOKIE_PATH = validators.String(default='/')
    CSRF_COOKIE_SECURE = validators.Boolean(default=False)
    CSRF_COOKIE_HTTPONLY = validators.Boolean(default=False)
    CSRF_HEADER_NAME = validators.String(default='HTTP_X_CSRFTOKEN')
    CSRF_TOKEN_FIELD_NAME = validators.String(default='csrf_token')
    CSRF_TRUSTED_ORIGINS = validators.Array(default=[])
