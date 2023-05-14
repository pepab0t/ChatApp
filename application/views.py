from flask import Blueprint, render_template, url_for, request, redirect, session
import requests
import base64
from functools import wraps
from .entity import User


views = Blueprint("views", __name__)


def get_url(endpoint: str, **path_params):
    return f"http://192.168.0.31:5000{url_for(endpoint, **path_params)}"


def redirect_login():
    return redirect(get_url("views.login"))


def create_user():
    if (user_dict := session.get("user")) is None:
        return None
    return User(**user_dict)


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = session.get("token", None)
        if token is None:
            return redirect_login()
        return fn(token, *args, **kwargs)

    return wrapper


@views.get("/")
@token_required
def home(token: str):
    print("token", session["token"])
    response = requests.get(
        get_url("api.get_friends"), headers={"Authorization": f"Bearer {token}"}
    )

    if not response.ok:
        return redirect_login()

    data = response.json()

    return render_template("home.html", user=create_user(), friends=data)


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

    data = response.json()
    session["token"] = data["token"]
    session["user"] = data["user"]
    print(session["user"])

    return redirect(url_for("views.home"))


@views.route("/logout", methods=["GET"])
def logout():
    del session["token"]
    del session["user"]
    return redirect_login()


@views.get("/requests")
@token_required
def friend_requests(token: str):
    response = requests.get(
        get_url("api.get_requests"), headers={"Authorization": f"Bearer {token}"}
    )

    if not response.ok:
        return redirect_login()

    data = response.json()

    return render_template("requests.html", user=create_user(), requests=data)


@views.get("/add_friend")
@token_required
def add_friend(token: str):
    return render_template("add_friend.html", user=create_user())


@views.get("/chat/<string:username>")
@token_required
def open_chat(token: str, username: str):
    # if (username := request.args.get("username", None)) is None:
    #     return redirect(url_for("views.home"))

    response = requests.get(
        get_url("api.get_room", username=username),
        headers={"Authorization": f"Bearer {token}"},
    )

    if not response.ok:
        return redirect(url_for("views.home"))

    session["room"] = response.json()["room"]

    return render_template(
        "chat.html",
        user=create_user(),
        with_user=username,
    )
