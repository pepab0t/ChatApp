import pytest

from application import create_app, db

from .helper import AuthAction, DBAction, user1, user2, user3


@pytest.fixture(scope="session")
def app():
    _, app = create_app("sqlite://")
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    print("start")
    yield app
    print("finish")


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def auth(client):
    return AuthAction(client)


@pytest.fixture(scope="session")
def login_response(auth):
    return auth.login_fixed()


@pytest.fixture(scope="session")
def login_response_user1(auth: AuthAction):
    return auth.login_defined_user(user1)


@pytest.fixture(scope="session")
def login_response_user2(auth: AuthAction):
    return auth.login_defined_user(user2)


@pytest.fixture(scope="session")
def login_response_user3(auth: AuthAction):
    return auth.login_defined_user(user3)


@pytest.fixture()
def db_action(app):
    return DBAction(app)


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
