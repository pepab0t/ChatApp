import base64
import re

from werkzeug.test import TestResponse

from application import repository
from application.auth.entity import UserRegisterEntity
from application.database.models import User

username = "test"
email = "test@test.com"
password = "12345"

user1 = {"username": "user1", "email": "user1@test.com", "password": "1234"}
user2 = {"username": "user2", "email": "user2@test.com", "password": "1234"}
user3 = {"username": "user3", "email": "user3@test.com", "password": "1234"}


def parse_cookies(response):
    out = {}
    for c in response.headers.getlist("Set-Cookie"):
        if (m := re.search(f"([A-Za-z_]+)=(.+?);", c)) is not None:
            out[m[1]] = m[2]
    return out


def code_ok(status_code: int):
    return 200 <= status_code <= 299


def code_ok_response(response) -> bool:
    return 200 <= response.status_code <= 299


def set_client_cookies(client, cookies: dict[str, str]):
    for k, v in cookies.items():
        client.set_cookie(k, v)


def set_client_cookies_from_response(client, response):
    set_client_cookies(client, parse_cookies(response))


class AuthAction:
    def __init__(self, client):
        self.client = client

    def register(self, username: str, email: str, password: str) -> TestResponse:
        return self.client.post(
            "/auth/register",
            json={"username": username, "email": email, "password": password},
        )

    def login(self, username: str, password: str) -> TestResponse:
        auth = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
        return self.client.post("/auth/login", headers={"Authorization": auth})

    def login_defined_user(self, user: dict[str, str]):
        return self.login(user["username"], user["password"])

    def register_fixed(self):
        return self.register(username=username, email=email, password=password)

    def login_fixed(self):
        return self.login(username=username, password=password)

    def register_and_login(self):
        r = self.register_fixed()
        assert self.code_ok(r.status_code)
        return self.login_fixed()

    def logout(self) -> TestResponse:
        return self.client.post("/auth/logout")

    @staticmethod
    def parse_cookies(response):
        out = {}
        for c in response.headers.getlist("Set-Cookie"):
            if (m := re.search(f"([A-Za-z_]+)=(.+?);", c)) is not None:
                out[m[1]] = m[2]
        return out

    @staticmethod
    def code_ok(status_code: int):
        return 200 <= status_code <= 299


class DBAction:
    def __init__(self, app):
        self._app = app

    def create_sample_users(self):
        with self._app.app_context():
            repository.register_user(UserRegisterEntity(**user1))
            repository.db.session.rollback()
            repository.register_user(UserRegisterEntity(**user2))
            repository.db.session.rollback()
            repository.register_user(UserRegisterEntity(**user3))
