import base64
from werkzeug.test import TestResponse
from application import repository
import re

from application.entity import UserRegisterEntity
from application.database.models import User

username = "test"
email = "test@test.com"
password = "12345"

u1 = {"username": "user1", "email": "user1@test.com", "password": "1234"}

u2 = {"username": "user2", "email": "user2@test.com", "password": "4567"}

u3 = {"username": "user3", "email": "user3@test.com", "password": "7895"}


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

    @staticmethod
    def set_client_cookies(client, cookies: dict[str, str]):
        for k, v in cookies.items():
            client.set_cookie(k, v)

    @staticmethod
    def set_client_cookies_from_response(client, response):
        AuthAction.set_client_cookies(client, AuthAction.parse_cookies(response))


class DBAction:
    def __init__(self, app):
        self._app = app

    def create_sample_users(self):
        with self._app.app_context():
            # user1 = User(**UserRegisterEntity(**u1).dict())
            # user2 = User(**UserRegisterEntity(**u2).dict())
            # user3 = User(**UserRegisterEntity(**u3).dict())
            # repository.db.session.add_all([user1, user2, user3])
            # repository.db.session.commit()
            repository.register_user(UserRegisterEntity(**u1))
            repository.db.session.rollback()
            repository.register_user(UserRegisterEntity(**u2))
            repository.db.session.rollback()
            repository.register_user(UserRegisterEntity(**u3))
