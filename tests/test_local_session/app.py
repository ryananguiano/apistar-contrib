from apistar import App, Route, http
from apistar_contrib.sessions import Session, SessionComponent, SessionHook, LocalMemorySessionStore


def use_session(session: Session, params: http.QueryParams):
    for key, value in params:
        session[key] = value
    return session.data


def clear_session(session: Session):
    session.clear()
    return session.data


routes = [
    Route('/', 'GET', use_session),
    Route('/clear', 'GET', clear_session),
]

app = App(
    routes=routes,
    components=[SessionComponent(LocalMemorySessionStore)],
    event_hooks=[SessionHook]
)
