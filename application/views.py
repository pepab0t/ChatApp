import base64

import requests
from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from . import repository, get_url
from .auth import fake_controller

views = Blueprint("views", __name__, url_prefix="")


def redirect_login():
    return redirect(get_url("views.login"))


def current_user():
    return repository.get_user_by_id(session.get("user_id", -1))


def set_cookies(response, cookies) -> None:
    for k, v in cookies.items():
        response.set_cookie(k, v, httponly=True)


def get_request_count() -> int:
    response = requests.get(get_url("api.get_requests_count"), cookies=request.cookies)
    if not response.ok or "count" not in (data := response.json()):
        return 0
    else:
        return data["count"]


@views.get("/")
def home():
    response = requests.get(
        get_url("api.get_friends"),
        cookies=request.cookies,
    )
    if not response.ok:
        return redirect_login()

    request_count: int = get_request_count()
    print(f"{request_count=}")

    data = response.json().get("data")
    r = make_response(
        render_template(
            "messages-list.html",
            user=current_user(),
            request_count=request_count,
            friends=data,
            nav=True,
        )
    )
    set_cookies(r, response.cookies)
    return r


@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username == "" or password == "":
        return render_template(
            "login.html",
            message_username="Please enter username and password",
            username=username,
        )

    authorization = (
        "Basic " + base64.b64encode(f"{username}:{password}".encode()).decode()
    )

    response = requests.post(
        get_url("auth.login"), headers={"Authorization": authorization}
    )

    # response = fake_controller.login(username=username, password=password)

    if not response.ok:
        return render_template(
            "login.html",
            message_username="Invalid username or password",
            username=username,
        )

    data = response.json()
    session["user_id"] = data["id"]

    r = make_response(redirect(url_for("views.home")))
    set_cookies(
        r,
        {
            "access_token": data.get("access", ""),
            "refresh_token": data.get("refresh", ""),
        },
    )
    return r


@views.route("/register/", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "")
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    password2 = request.form.get("password2", "")
    if any(map(lambda x: x == "", [username, email, password, password2])):
        return render_template(
            "register.html",
            username=username,
            email=email,
            message_email="Please enter all necessary information",
        )

    if password != password2:
        return render_template(
            "register.html",
            username=username,
            email=email,
            message_password="Passwords don't match",
        )

    if len(username) > 20:
        return render_template(
            "register.html",
            email=email,
            message_email="Username too long (max 20 characters)",
        )

    if len(email) > 50:
        return render_template(
            "register.html",
            message_email="Email too long (max 50 characters)",
        )

    if len(password) > 100:
        return render_template(
            "register.html",
            email=email,
            username=username,
            message_email="Password exceeded 100 characters",
        )

    response = requests.post(
        get_url("auth.register"),
        json={"username": username, "email": email, "password": password},
    )

    # response = fake_controller.register(username, email, password)

    if not response.ok:
        data = response.json()
        return render_template(
            "register.html",
            message_email=data.get("message"),
            username=username,
            email=email,
        )

    user = response.json()

    auth = (
        "Basic " + base64.b64encode(f"{user['username']}:{password}".encode()).decode()
    )
    response = requests.post(get_url("auth.login"), headers={"Authorization": auth})
    if not response.ok:
        return render_template("login.html")

    data = response.json()
    session["user_id"] = data["id"]
    r = make_response(redirect(url_for("views.home")))
    set_cookies(
        r,
        {
            "access_token": data.get("access", ""),
            "refresh_token": data.get("refresh", ""),
        },
    )
    return r


@views.get("/logout")
def logout():
    response = make_response(redirect_login())
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    if "user_id" in session:
        del session["user_id"]
    return response


@views.get("/requests")
def friend_requests():
    response = requests.get(
        get_url("api.get_requests"),
        cookies=request.cookies,
    )
    if not response.ok:
        return redirect_login()

    data = response.json().get("data")
    r = make_response(
        render_template("requests.html", user=current_user(), requests=data, nav=True)
    )
    set_cookies(r, response.cookies)
    return r


@views.get("/add_friend")
def add_friend():
    response = requests.get(get_url("api.test"), cookies=request.cookies)
    if not response.ok:
        return redirect_login()
    request_count: int = get_request_count()
    r = make_response(
        render_template(
            "search.html", user=current_user(), nav=True, request_count=request_count
        )
    )
    set_cookies(r, response.cookies)
    return r


@views.get("/chat/<string:username>")
def open_chat(username: str):
    response = requests.get(
        get_url("api.get_room", username=username),
        cookies=request.cookies,
    )
    if not response.ok:
        return redirect(url_for("views.home"))

    r = make_response(
        render_template(
            "chat.html",
            user=current_user(),
            with_user=username,
            room=response.json()["room"],
            nav=True,
        )
    )

    set_cookies(r, response.cookies)
    return r
