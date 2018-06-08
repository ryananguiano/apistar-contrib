import abc
import random
import typing

from apistar import http, Component
from werkzeug.http import parse_cookie, dump_cookie

from apistar_contrib.sessions.settings import SessionSettings, SettingsMapping

NOT_SET = object()


class Session(object):
    def __init__(self, store, session_id: str, data: typing.Dict[str, typing.Any]=None) -> None:
        self.store = store
        self.settings = store.session_settings

        if data is not None:
            self.data = data
            self.is_new = False
            self.needs_cookie = False
        else:
            self.data = {}
            self.is_new = True
            self.needs_cookie = True

        self.is_modified = False
        self.is_cleared = False
        self.session_id = session_id
        self.expires = NOT_SET

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def __getitem__(self, key: str) -> typing.Any:
        return self.data[key]

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self.data[key] = value
        self.is_modified = True

    def __delitem__(self, key: str):
        del self.data[key]
        self.is_modified = True

    def __getattr__(self, item):
        if item in ('get', 'pop', 'update'):
            return getattr(self.data, item)
        raise AttributeError

    def clear(self):
        self.data = {}
        self.is_cleared = True
        self.needs_cookie = True
        self.expires = NOT_SET

    def save(self):
        return self.store.save(self)

    def expire_cookie(self, max_age: int=None):
        self.expires = max_age
        self.needs_cookie = True


class SessionStore(abc.ABC):
    def __init__(self, session_settings: SessionSettings, **kwargs):
        self.session_settings = session_settings

    def new(self) -> Session:
        session_id = self._generate_key()
        return Session(self, session_id=session_id)

    @abc.abstractmethod
    def load(self, session_id: str) -> Session:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, session: Session) -> None:
        raise NotImplementedError

    def _generate_key(self) -> str:
        length = 30
        allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        urandom = random.SystemRandom()
        return ''.join(urandom.choice(allowed_chars) for i in range(length))


class SessionComponent(Component):
    def __init__(self, store: type, *args, session_settings: SettingsMapping=None, **kwargs):
        assert issubclass(store, SessionStore)
        self.settings = SessionSettings(session_settings or {})
        kwargs['session_settings'] = self.settings
        self.store = store(*args, **kwargs)

    def resolve(self, cookie: http.Header) -> Session:
        if cookie:
            cookies = parse_cookie(cookie)
            session_id = cookies.get(self.settings.cookie_name)
        else:
            session_id = None

        if session_id is not None:
            session = self.store.load(session_id)
        else:
            session = self.store.new()

        return session


class SessionHook:
    def on_response(self, session: Session, response: http.Response):
        session.save()
        if session.needs_cookie:
            cookie = dump_cookie(
                session.settings.cookie_name,
                session.session_id,
                max_age=session.settings.cookie_age if session.expires is NOT_SET else session.expires,
                domain=session.settings.cookie_domain,
                path=session.settings.cookie_path,
                secure=session.settings.cookie_secure,
                httponly=session.settings.cookie_httponly,
            )
            response.headers['set-cookie'] = cookie
