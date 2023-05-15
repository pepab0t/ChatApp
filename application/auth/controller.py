from flask import Blueprint, request, abort, jsonify
from . import service
from ..entity import UserRegisterEntity
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["POST"])
def register():
    json, code = service.register(request.get_json())
    return jsonify(json), code


@auth.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    token, code = service.login(auth)
    response = jsonify(token)
    # set_access_cookies(response, token)
    return response, code


@auth.post("/logout")
def logout():
    response = jsonify({"message": "logout successfull"})
    unset_jwt_cookies(response)
    return response, 200
