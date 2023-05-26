from flask import Flask
import os
from flask_socketio import SocketIO, send, join_room, leave_room
from dotenv import load_dotenv

load_dotenv()

from .database import db, DB_NAME
from .error_handlers import (
    handle_invalid_body,
    handle_database_error,
    handle_entity_404,
    handle_chat_app_exception,
)


def create_flask(db_uri: str):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("APP_JWT_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["JWT_TOKEN_LOCATION"] = "cookies"

    db.init_app(app)

    from .auth.controller import auth
    from .api.controller import api
    from .views import views, get_url

    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(views)

    app.register_error_handler(handle_chat_app_exception.exc, handle_chat_app_exception)
    app.register_error_handler(handle_invalid_body.exc, handle_invalid_body)
    app.register_error_handler(handle_database_error.exc, handle_database_error)
    app.register_error_handler(handle_entity_404.exc, handle_entity_404)

    app.jinja_env.globals.update(get_url=get_url)

    return app


def create_app(db_uri):
    app = create_flask(db_uri)
    socket = SocketIO(app, cors_allowed_origins="*")  # ["http://127.0.0.1:5500"])

    @socket.on("join_room")
    def connect(data):
        room = data.get("room")
        print(data)
        if room is None:
            return
        join_room(room)

    @socket.on("leave_room")
    def disconnect(data):
        room = data.get("room")
        if room is None:
            return
        leave_room(room)

    @socket.on("message")
    def message(data):
        room = data.get("room")
        if room is None:
            return
        send(data, to=room)

    return socket, app
