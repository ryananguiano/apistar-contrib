from apistar_contrib.compat import redis, pickle, PICKLE_VERSION
from apistar_contrib.sessions.base import Session, SessionStore


class RedisSessionStore(SessionStore):
    def __init__(self, redis_url, **kwargs):
        assert redis is not None, 'redis must be installed'
        self.client = redis.StrictRedis.from_url(redis_url)
        super().__init__(**kwargs)

    def get_key(self, session_id):
        return f'session:{session_id}'

    def new(self) -> Session:
        session_id = self._generate_key()
        return Session(self, session_id=session_id)

    def load(self, session_id: str) -> Session:
        key = self.get_key(session_id)
        if not self.client.exists(key):
            return self.new()
        data = self.client.get(key)
        return Session(self, session_id=session_id,
                       data=self.decode(data))

    def save(self, session: Session):
        if session.is_cleared:
            self.client.delete(
                self.get_key(session.session_id)
            )
            session.session_id = self._generate_key()
        if session.is_new or session.is_modified or session.is_cleared:
            self.client.set(
                self.get_key(session.session_id),
                self.encode(session.data)
            )

    def encode(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            value = pickle.dumps(value, PICKLE_VERSION)
            return value
        return value

    def decode(self, value):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = pickle.loads(value)
        return value
