import typing

from apistar import http, Component


class Session(object):
    def __init__(self, session_id: str, data: typing.Dict[str, typing.Any]=None) -> None:
        if data is not None:
            self.data = data
            self.is_new = False
        else:
            self.data = {}
            self.is_new = True

        self.is_modified = False
        self.is_cleared = False
        self.session_id = session_id

    def __getitem__(self, key: str) -> typing.Any:
        return self.data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def get(self, key: str, default=None) -> typing.Any:
        return self.data.get(key, default)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self.data[key] = value
        self.is_modified = True

    def __delitem__(self, key: str):
        del self.data[key]
        self.is_modified = True

    def clear(self):
        self.data = {}
        self.is_cleared = True


class SessionComponent(Component):
    def resolve(self, request: http.Request) -> Session:
        return getattr(request, '_session', None)
