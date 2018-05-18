import string
import typing

from apistar import http
from werkzeug.http import dump_cookie, parse_cookie

from apistar_contrib.compat import random
from apistar_contrib.sessions import Session

local_memory_sessions = {}  # type: typing.Dict[str, typing.Dict[str, typing.Any]]


class LocalMemorySessionStore:
    cookie_name = 'session_id'

    def new(self) -> Session:
        session_id = self._generate_key()
        return Session(session_id=session_id)

    def load(self, session_id: str) -> Session:
        try:
            data = local_memory_sessions[session_id]
        except KeyError:
            return self.new()
        return Session(session_id=session_id, data=data)

    def save(self, session: Session) -> typing.Dict[str, str]:
        headers = {}
        if session.is_cleared:
            local_memory_sessions.pop(session.session_id, None)
            session.session_id = self._generate_key()
            session.is_new = True
        if session.is_new:
            cookie = dump_cookie(self.cookie_name, session.session_id)
            headers['set-cookie'] = cookie
        if session.is_new or session.is_modified:
            local_memory_sessions[session.session_id] = session.data
        return headers

    def _generate_key(self, length=30) -> str:
        allowed_chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(allowed_chars) for _ in range(length))


class LocalMemorySessionHook:
    def __init__(self) -> None:
        self.store = LocalMemorySessionStore()

    def on_request(self, request: http.Request, cookie: http.Header):
        if cookie:
            cookies = parse_cookie(cookie)
            session_id = cookies.get('session_id')
        else:
            session_id = None

        if session_id is not None:
            session = self.store.load(session_id)
        else:
            session = self.store.new()

        request._session = session

    def on_response(self, request: http.Request, response: http.Response, exc: Exception):
        if exc is not None:
            return
        session = getattr(request, '_session', None)
        if session:
            session_headers = self.store.save(session)
            for key, value in session_headers.items():
                response.headers[key] = value
