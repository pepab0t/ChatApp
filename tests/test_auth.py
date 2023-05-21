import os
from flask import Flask
from application.database.models import User
from application.auth import utils as auth_utils
from application.exceptions import InvalidJWT
from .helper import AuthAction, email, username, password
import pytest
import time
from unittest import mock


def test_jwt_valid():
    token = auth_utils.create_access_token(1)
    assert auth_utils.validate_jwt(token)


def test_jwt_invalid():
    token = auth_utils.create_access_token(1) + "!"
    with pytest.raises(InvalidJWT):
        auth_utils.validate_jwt(token)


def test_registration(auth: AuthAction, app: Flask):
    auth.register_fixed()

    with app.app_context():
        assert User.query.count() == 1
        user = User.query.first()
        assert user.email == email
        assert user.username == username
        assert user.password == auth_utils.encrypt_password(password)


def test_invalid_registration(auth: AuthAction):
    response = auth.register(username=username, email=email, password="12")
    assert response.status_code == 422


def test_duplicate_register(auth: AuthAction):
    response = auth.register_fixed()
    assert auth.code_ok(response.status_code)
    response = auth.register_fixed()
    assert (
        response.status_code == 422
        and "UNIQUE constraint failed" in response.json["message"]  # type: ignore
    )


def test_valid_login(auth: AuthAction):
    username = "test"
    email = "test@test.com"
    password = "12345"

    res = auth.register_and_login()
    cookies = auth.parse_cookies(res)

    auth_utils.validate_jwt(cookies["access_token"])
    auth_utils.validate_jwt(cookies["refresh_token"])


def test_invalid_login(auth: AuthAction):
    res = auth.register_fixed()
    assert auth.code_ok(res.status_code)
    res = auth.login(username=username, password=password + "!")
    assert res.status_code == 401
    cookies = auth.parse_cookies(res)

    with pytest.raises(KeyError):
        cookies["access_token"]
    with pytest.raises(KeyError):
        cookies["refresh_token"]


def test_validate_token_true(auth: AuthAction, client):
    res = auth.register_and_login()
    cookies = auth.parse_cookies(res)
    r1 = client.get("/auth/validate", json={"token": cookies["access_token"]})
    assert r1.json["state"] == "true" and r1.json.get("payload") is not None
    r2 = client.get("/auth/validate", json={"token": cookies["refresh_token"]})
    assert r2.json["state"] == "true"


@mock.patch.dict(
    os.environ,
    {
        "ACCESS_TOKEN_DURATION_MINS": "0",
        "ACCESS_TOKEN_TOLERANCE_MINS": str(2 / 60),
        "REFRESH_TOKEN_DURATION_HOURS": "1",
    },
)
def test_validate_token_refresh(auth: AuthAction, client):
    res = auth.register_and_login()
    cookies = auth.parse_cookies(res)
    r1 = client.get("/auth/validate", json={"token": cookies["access_token"]})
    assert r1.json["state"] == "refresh"


@mock.patch.dict(
    os.environ,
    {
        "ACCESS_TOKEN_DURATION_MINS": "0",
        "ACCESS_TOKEN_TOLERANCE_MINS": "0",
        "REFRESH_TOKEN_DURATION_HOURS": "1",
    },
)
def test_validate_token_false(auth: AuthAction, client):
    res = auth.register_and_login()
    cookies = auth.parse_cookies(res)
    r1 = client.get("/auth/validate", json={"token": cookies["access_token"]})
    assert r1.json["state"] == "false"


@mock.patch.dict(
    os.environ,
    {
        "ACCESS_TOKEN_DURATION_MINS": "-1",
        "ACCESS_TOKEN_TOLERANCE_MINS": "2",
        "REFRESH_TOKEN_DURATION_HOURS": "1",
    },
)
def test_refresh(auth: AuthAction, client):
    res = auth.register_and_login()
    assert auth.code_ok(res.status_code)
    cookies = auth.parse_cookies(res)
    for k, v in cookies.items():
        client.set_cookie(k, v)

    time.sleep(1)

    res = client.get("/api/test")
    assert auth.code_ok(res.status_code)
    cookies_after = auth.parse_cookies(res)
    assert cookies["access_token"] != cookies_after["access_token"]
    assert cookies["refresh_token"] != cookies_after["refresh_token"]


@mock.patch.dict(
    os.environ,
    {
        "ACCESS_TOKEN_DURATION_MINS": "0",
        "ACCESS_TOKEN_TOLERANCE_MINS": "1",
        "REFRESH_TOKEN_DURATION_HOURS": "0",
    },
)
def test_refresh_invalid(auth: AuthAction, client):
    res = auth.register_and_login()
    assert auth.code_ok(res.status_code)
    for k, v in auth.parse_cookies(res).items():
        client.set_cookie(k, v)

    res = client.get("/api/test")
    assert res.json.get("message") == "Invalid refresh token"
    assert res.status_code == 401


@mock.patch.dict(
    os.environ,
    {
        "ACCESS_TOKEN_DURATION_MINS": "1",
        "ACCESS_TOKEN_TOLERANCE_MINS": "2",
        "REFRESH_TOKEN_DURATION_HOURS": "1",
    },
)
def test_refresh_bad_jwt(auth: AuthAction, client):
    res = auth.register_and_login()
    assert auth.code_ok(res.status_code)
    cookies = auth.parse_cookies(res)
    client.set_cookie("refresh_token", cookies["refresh_token"])
    client.set_cookie("access_token", "abcd")

    res = client.get("/api/test")
    assert res.status_code == 401


def test_logout(auth):
    res = auth.logout()
    assert auth.code_ok(res.status_code)
