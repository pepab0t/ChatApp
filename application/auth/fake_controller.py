from . import service
import typing as t


class FakeResponse:
    def __init__(self, status_code: int, payload=None) -> None:
        self.payload: dict[str, t.Any] | None = payload
        self.status_code: int = status_code

    def json(self):
        return self.payload or dict()

    @property
    def ok(self):
        return 200 <= self.status_code < 400


def login(username: str, password: str):
    payload, code = service.login(service.AuthTuple(username, password))
    response = FakeResponse(payload=payload, status_code=code)
    return response


def register(username: str, email: str, password: str):
    payload, code = service.register(
        {"email": email, "username": username, "password": password}
    )
    return FakeResponse(code, payload=payload)
