import pytest
from application import create_app, db
from .helper import AuthAction, DBAction
import os


@pytest.fixture(scope="module")
def app():
    _, app = create_app("sqlite:///")
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        db.create_all()

    print("start")
    yield app
    print("finish")


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def auth(client):
    return AuthAction(client)


@pytest.fixture()
def db_action(app):
    return DBAction(app)


@pytest.fixture(scope="module")
def login_response(auth):
    return auth.login_fixed()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
