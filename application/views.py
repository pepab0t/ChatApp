from flask import Blueprint, render_template, url_for, request, redirect
import requests

views = Blueprint("views", __name__)


def get_url(endpoint: str):
    return f"http://localhost:5000{url_for(endpoint)}"


@views.get("/")
def home():
    response = requests.get(get_url("api.get_friends"))

    if response.status_code == 401:
        return redirect(url_for("views.login_page"))

    return render_template("index.html")


@views.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")
