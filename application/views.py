from flask import Blueprint, render_template, url_for, request, redirect, make_response
import requests
import base64
from functools import wraps
from .auth.utils import decode_jwt
from . import repository

views = Blueprint("views", __name__)


def get_url(endpoint: str, **path_params):
    return f"http://localhost:5000{url_for(endpoint, **path_params)}"


def redirect_login():
    return redirect(get_url("views.login"))


def current_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token", "")

        try:
            payload = decode_jwt(token)
            username = payload["user"]
        except Exception:
            current_user = None
        else:
            current_user = repository.get_user_by_username(username)
        return fn(current_user, *args, **kwargs)

    return wrapper


def parse_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token", None)
        return fn(token, *args, **kwargs)

    return wrapper


@views.get("/")
@current_user
def home(user):
    response = requests.get(
        get_url("api.get_friends"),
        cookies={"access_token": request.cookies.get("access_token", "")},
    )

    if not response.ok:
        return redirect_login()

    data = response.json()
    return render_template("home.html", user=user, friends=data)


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

    token = response.cookies.get("access_token")
    r = make_response(redirect(url_for("views.home")))
    r.set_cookie("access_token", token)
    return r


@views.get("/logout")
def logout():
    requests.post(get_url("auth.logout"))
    response = make_response(redirect_login())
    # response.delete_cookie("access_token")
    return response


@views.get("/requests")
@current_user
def friend_requests(user):
    response = requests.get(
        get_url("api.get_requests"),
        cookies={"access_token": request.cookies.get("access_token", "")},
    )

    if not response.ok:
        return redirect_login()

    data = response.json()

    return render_template("requests.html", user=user, requests=data)


@views.get("/add_friend")
@current_user
def add_friend(user):
    return render_template("add_friend.html", user=user)


@views.get("/chat/<string:username>")
@current_user
def open_chat(user, username: str):
    response = requests.get(
        get_url("api.get_room", username=username),
        cookies={"access_token": request.cookies.get("access_token", "")},
    )

    if not response.ok:
        return redirect(url_for("views.home"))

    return render_template(
        "chat.html",
        user=user,
        with_user=username,
        room=response.json()["room"],
    )
