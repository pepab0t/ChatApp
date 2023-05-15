from flask import Blueprint, render_template, url_for, request, redirect, make_response
import requests
import base64
from functools import wraps
from flask_socketio import join_room
from .auth.utils import decode_jwt
from . import repository

views = Blueprint("views", __name__)


def get_url(endpoint: str, **path_params):
    return f"http://localhost:5000{url_for(endpoint, **path_params)}"


def redirect_login():
    return redirect(get_url("views.login"))


def response_with_token(response, token: str):
    r = make_response(response)
    r.set_cookie("access_token", token)
    return r


# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     username = jwt_data["username"]
#     return repository.get_user_by_username(username)
def current_user(token: str):
    try:
        payload = decode_jwt(token)
        username = payload["user"]
    except Exception:
        return None

    return repository.get_user_by_username(username)


def parse_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token", None)
        return fn(token, *args, **kwargs)

    return wrapper


@views.get("/")
@parse_token
def home(token: str):
    response = requests.get(
        get_url("api.get_friends"), headers={"Authorization": f"Bearer {token}"}
    )

    if not response.ok:
        return redirect_login()

    data = response.json()

    print(current_user(token))

    return render_template("home.html", user=current_user(token), friends=data), token


@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    if username is None or password is None:
        return render_template("login.html")

    auth = "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()

    response = requests.post(get_url("auth.login"), headers={"Authorization": auth})

    if not response.ok:
        return render_template("login.html")

    return response_with_token(
        redirect(url_for("views.home")), response.json()["token"]
    )


@views.get("/logout")
def logout():
    return response_with_token(redirect(url_for("views.login")), "")


@views.get("/requests")
@parse_token
def friend_requests(token: str):
    response = requests.get(
        get_url("api.get_requests"), headers={"Authorization": f"Bearer {token}"}
    )

    if not response.ok:
        return redirect_login()

    data = response.json()

    return render_template("requests.html", user=current_user(token), requests=data)


@views.get("/add_friend")
@parse_token
def add_friend(token: str):
    return render_template("add_friend.html", user=current_user(token))


@views.get("/chat/<string:username>")
@parse_token
def open_chat(token: str, username: str):
    response = requests.get(
        get_url("api.get_room", username=username),
        headers={"Authorization": f"Bearer {token}"},
    )

    if not response.ok:
        return redirect(url_for("views.home"))

    return render_template(
        "chat.html",
        user=current_user(token),
        with_user=username,
        room=response.json()["room"],
    )
