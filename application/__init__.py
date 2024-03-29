import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, url_for
from flask_socketio import SocketIO, join_room, leave_room, send

load_dotenv()

from .database import db
from .error_handlers import (
    handle_chat_app_exception,
    handle_database_error,
    handle_entity_404,
    handle_invalid_body,
)


def get_url(endpoint: str, **path_params):
    url = f"{request.host_url[:-1]}{url_for(endpoint, **path_params)}"
    print(url)
    return url


def create_flask():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("APP_JWT_SECRET")
    if (db_uri := os.getenv("DB_URI")) is not None:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    else:
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    app.config["JWT_TOKEN_LOCATION"] = "cookies"

    db.init_app(app)

    from .api.controller import api
    from .auth.controller import auth
    from .views import get_url, views

    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(views)

    app.register_error_handler(handle_chat_app_exception.exc, handle_chat_app_exception)
    app.register_error_handler(handle_invalid_body.exc, handle_invalid_body)
    app.register_error_handler(handle_database_error.exc, handle_database_error)
    app.register_error_handler(handle_entity_404.exc, handle_entity_404)

    app.jinja_env.globals.update(get_url=get_url)

    @app.template_filter()
    def short(text: str, max_len: int):
        if len(text) > max_len:
            return text[:max_len] + "..."
        return text

    return app


def create_app():
    app = create_flask()
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
        # len(socket.server.manager.rooms["/"]["R1"])
        room = data.get("room")
        message = data.get("message")
        if room is None or message is None or not message.strip():
            return

        response = requests.post(
            get_url("api.send_message", username=data.get("with_user")),
            json={
                "message": message,
                "seen": len(socket.server.manager.rooms["/"][room]) > 1,  # type: ignore
            },
            cookies=request.cookies.to_dict(),
            headers={},
        )
        if response.ok:
            send(response.json(), to=room)

    return socket, app
