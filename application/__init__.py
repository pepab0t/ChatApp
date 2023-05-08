from flask import Flask, render_template
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from dotenv import get_key

from .database import db, DB_NAME, models
from .error_handlers import (
    handle_invalid_body,
    handle_database_error,
    handle_entity_404,
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = get_key(".env", "APP_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    from .auth.controller import auth
    from .api.controller import api

    app.register_blueprint(auth)
    app.register_blueprint(api)

    app.register_error_handler(handle_invalid_body.exc, handle_invalid_body)
    app.register_error_handler(handle_database_error.exc, handle_database_error)
    app.register_error_handler(handle_entity_404.exc, handle_entity_404)

    return app


def create_socketio():
    app = create_app()
    socket = SocketIO(app, cors_allowed_origins="*")
    return socket, app
