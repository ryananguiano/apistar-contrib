from apistar import types, validators


# Settings for Session
class SessionSettings(types.Type):
    cookie_name = validators.String(default='session_id')
    cookie_age = validators.Integer(allow_null=True)
    cookie_domain = validators.String(allow_null=True)
    cookie_path = validators.String(default='/')
    cookie_secure = validators.Boolean(default=False)
    cookie_httponly = validators.Boolean(default=False)
