from flask import Blueprint, render_template, url_for, request, redirect, make_response
import requests
import base64
from functools import wraps
from . import repository

views = Blueprint("views", __name__)


def get_url(endpoint: str, **path_params):
    return f"http://localhost:5000{url_for(endpoint, **path_params)}"


def redirect_login():
    return redirect(get_url("views.login"))


def validate_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("access_token")
        if token is None:
            return redirect_login()

        response = requests.get(get_url("auth.validate"), json={"token": token})
        response = response.json()

        match response["state"]:
            case "refresh":
                refresh_response = requests.get(
                    get_url("auth.refresh"),
                    cookies={
                        "access_token": request.cookies.get("access_token", ""),
                        "refresh_token": request.cookies.get("refresh_token", ""),
                    },
                )
                data = refresh_response.json()
                if not refresh_response.ok:
                    print(data)
                    return redirect_login()

                r = make_response(
                    fn(
                        data["access_token"],
                        current_user(data["user_id"]),
                        *args,
                        **kwargs,
                    ),
                )
                r.set_cookie("access_token", data["access_token"])
                r.set_cookie("refresh_token", data["refresh_token"])
                return r

            case "true":
                return fn(
                    token, current_user(response["payload"]["id"]), *args, **kwargs
                )
            case "false":
                return redirect_login()
            case _:
                return redirect_login()

    return wrapper


def current_user(user_id: int):
    return repository.get_user_by_id(user_id)


@views.get("/")
@validate_token
def home(token, user):
    response = requests.get(
        get_url("api.get_friends"),
        cookies={"access_token": token},
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

    data = response.json()
    access_token = data.get("access_token", "")
    refresh_token = data.get("refresh_token", "")
    r = make_response(redirect(url_for("views.home")))
    r.set_cookie("access_token", access_token)
    r.set_cookie("refresh_token", refresh_token)
    return r


@views.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    if any(map(lambda x: x is None, [username, email, password])):
        return render_template("register.html")

    response = requests.post(
        get_url("auth.register"),
        json={"username": username, "email": email, "password": password},
    )

    if not response.ok:
        return render_template("register.html")

    user = response.json()

    auth = (
        "Basic " + base64.b64encode(f"{user['username']}:{password}".encode()).decode()
    )
    response = requests.post(get_url("auth.login"), headers={"Authorization": auth})
    if not response.ok:
        return render_template("login.html")

    token = response.json()
    r = make_response(redirect(url_for("views.home")))
    r.set_cookie("access_token", token)
    return r


@views.get("/logout")
def logout():
    response = make_response(redirect_login())
    response.delete_cookie("access_token")
    return response


@views.get("/requests")
@validate_token
def friend_requests(token, user):
    response = requests.get(
        get_url("api.get_requests"),
        cookies={"access_token": token},
    )

    if not response.ok:
        return redirect_login()

    data = response.json()

    return render_template("requests.html", user=user, requests=data)


@views.get("/add_friend")
@validate_token
def add_friend(token, user):
    return render_template("add_friend.html", user=user)


@views.get("/chat/<string:username>")
@validate_token
def open_chat(token, user, username: str):
    response = requests.get(
        get_url("api.get_room", username=username),
        cookies={"access_token": token},
    )

    if not response.ok:
        return redirect(url_for("views.home"))

    return render_template(
        "chat.html",
        user=user,
        with_user=username,
        room=response.json()["room"],
    )
