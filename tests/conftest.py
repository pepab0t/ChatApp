import pytest
from application import create_app, db
from .helper import AuthAction, DBAction


@pytest.fixture()
def app():
    _, app = create_app("sqlite://")
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        db.create_all()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth(client):
    return AuthAction(client)


@pytest.fixture()
def db_action(app):
    return DBAction(app)


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
