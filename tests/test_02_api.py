from .helper import (
    DBAction,
    AuthAction,
    set_client_cookies_from_response,
    user1,
    user2,
    repository,
    username,
    code_ok,
    code_ok_response,
)
import pytest


def test_setup(db_action, auth):
    db_action.create_sample_users()
    auth.register_fixed()


def test_send_friend_request(client, login_response, login_response_user1):
    set_client_cookies_from_response(client, login_response)

    res1 = client.post("/api/send_request/user1")
    res2 = client.post("/api/send_request/user2")
    res3 = client.post("/api/send_request/user3")
    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res3.status_code == 201

    set_client_cookies_from_response(client, login_response_user1)
    res4 = client.post("/api/send_request/user3")
    assert res4.status_code == 201


def test_accept_friend(app, client, auth):
    res = auth.login_defined_user(user1)
    set_client_cookies_from_response(client, res)

    r_id = client.get("/api/requests").json[0]["id"]
    res = client.post(f"/api/approve?request_id={r_id}")
    assert auth.code_ok(res.status_code)

    with app.app_context():
        test_user = repository.get_user_by_username(username)
        user1_ = repository.get_user_by_username(user1["username"])
        assert user1_ in test_user.friends
        assert repository.get_request_by_id(r_id).accepted == True


def test_decline_friend(app, client, login_response_user2):
    set_client_cookies_from_response(client, login_response_user2)

    r_id = client.get("/api/requests").json[0]["id"]  # id of first received request
    res = client.post(f"/api/decline?request_id={r_id}")
    assert code_ok(res.status_code)

    with app.app_context():
        test_user = repository.get_user_by_username(username)
        user2_ = repository.get_user_by_username(user2["username"])
        assert user2_ not in test_user.friends
        assert repository.get_request_by_id(r_id).accepted == False


def test_have_two_requests(client, login_response_user3):
    set_client_cookies_from_response(client, login_response_user3)

    data = client.get("/api/requests").json
    assert len(data) == 2


def test_request_already_exists(client, login_response_user3):
    set_client_cookies_from_response(client, login_response_user3)

    res = client.post(f"/api/send_request/{username}")
    assert not code_ok(res.status_code)
    assert res.json.get("message") == "This request already exists"


def test_search(client, login_response):
    set_client_cookies_from_response(client, login_response)

    res = client.get("/api/search?search=user&exclude_friends=true")
    assert code_ok_response(res)
    assert len(res.json) == 1
    assert res.json[0]["username"] == "user2"

    res = client.get("/api/search?search=user&exclude_friends=false")
    assert code_ok_response(res)
    assert len(res.json) == 3
    assert (
        res.json[0]["username"] == "user1"
        and res.json[1]["username"] == "user2"
        and res.json[2]["username"] == "user3"
    )
