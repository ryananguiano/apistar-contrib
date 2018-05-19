import typing

from apistar_contrib.sessions import Session, SessionStore

local_memory_sessions = {}  # type: typing.Dict[str, typing.Dict[str, typing.Any]]


class LocalMemorySessionStore(SessionStore):
    def new(self) -> Session:
        session_id = self._generate_key()
        return Session(self, session_id=session_id)

    def load(self, session_id: str) -> Session:
        try:
            data = local_memory_sessions[session_id]
        except KeyError:
            return self.new()
        return Session(self, session_id=session_id, data=data)

    def save(self, session: Session):
        if session.is_cleared:
            local_memory_sessions.pop(session.session_id, None)
            session.session_id = self._generate_key()
        if session.is_new or session.is_modified or session.is_cleared:
            local_memory_sessions[session.session_id] = session.data
