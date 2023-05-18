from flask import Blueprint, request, jsonify, make_response
from . import service
from .token import token_valid
from ..exceptions import ChatAppException, TolerableExpiredJWT

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["POST"])
def register():
    json, code = service.register(request.get_json())
    return jsonify(json), code


@auth.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    token, code = service.login(auth)
    response = make_response(
        jsonify(access_token=token["access"], refresh_token=token["refresh"]), code
    )
    response.set_cookie("access_token", token["access"], httponly=True)
    response.set_cookie("refresh_token", token["refresh"], httponly=True)
    return response


@auth.get("/refresh")
@token_valid(token_name="access_token", inject_error=True)
@token_valid(token_name="refresh_token")
def refresh(errors: list[ChatAppException], user_id: int):
    # allowing refresh only expired tokens
    if not errors:
        return jsonify(message="JWT is valid, no need to refresh"), 400

    # first error from access token must be TolarableExpiredJWT
    if not isinstance(errors[0], TolerableExpiredJWT):
        raise errors[0]

    token = service.create_tokens(user_id)
    response = make_response(
        jsonify(access_token=token["access"], refresh_token=token["refresh"]), 200
    )
    response.set_cookie("access_token", token["access"], httponly=True)
    response.set_cookie("refresh_token", token["refresh"], httponly=True)
    return response


# not needed
@auth.post("/logout")
def logout():
    response = make_response(jsonify(message="Logout successfull"), 200)
    response.delete_cookie("access_token", httponly=True)
    response.delete_cookie("refresh_token", httponly=True)
    return response
