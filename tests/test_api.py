from .helper import DBAction, AuthAction, u1, username


def test_send_friend_request(client, auth: AuthAction, db_action: DBAction):
    db_action.create_sample_users()
    res = auth.register_and_login()
    auth.set_client_cookies_from_response(client, res)

    res = client.post("/api/send_request/user1")
    assert res.status_code == 201
