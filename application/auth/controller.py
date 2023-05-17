from flask import Blueprint, request, abort, jsonify, make_response
from . import service
from ..entity import UserRegisterEntity

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["POST"])
def register():
    json, code = service.register(request.get_json())
    return jsonify(json), code


@auth.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    token, code = service.login(auth)
    response = make_response(jsonify(message="Successfully logged in"), code)
    response.set_cookie("access_token", token, httponly=True)
    print(f"cookie set {token}")
    return response


@auth.post("/logout")
def logout():
    response = make_response(jsonify(message="Logout successfull"), 200)
    response.delete_cookie("access_token", httponly=True)
    response.delete_cookie("access_token")
    print("logged out")
    return response
