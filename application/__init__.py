from flask import Flask, session
from flask_socketio import SocketIO, send, join_room, leave_room
from dotenv import get_key

from .database import db, DB_NAME
from .error_handlers import (
    handle_invalid_body,
    handle_database_error,
    handle_entity_404,
)


def create_app():
    app = Flask(__name__)
    app.config["SESSION_TYPE"] = "cookie"
    app.config["SECRET_KEY"] = get_key(".env", "APP_SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = get_key(".evn", "APP_JWT_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    from .auth.controller import auth
    from .api.controller import api
    from .views import views, get_url

    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(views)

    app.register_error_handler(handle_invalid_body.exc, handle_invalid_body)
    app.register_error_handler(handle_database_error.exc, handle_database_error)
    app.register_error_handler(handle_entity_404.exc, handle_entity_404)

    app.jinja_env.globals.update(get_url=get_url)

    return app


def create_socketio():
    app = create_app()
    socket = SocketIO(app, cors_allowed_origins="*")

    @socket.on("connect")
    def connect(data):
        room = session.get("room")
        if room is None:
            return

        join_room(room)

    @socket.on("disconnect")
    def disconnect():
        room = session.get("room")
        if room is None:
            return

        leave_room(room)
        del session["room"]

    @socket.on("message")
    def message(data):
        room = session.get("room")
        if room is None:
            return

        send(data, to=room)

    return socket, app
