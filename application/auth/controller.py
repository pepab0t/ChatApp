from flask import Blueprint, request, abort, jsonify
from . import service
from ..entity import UserRegisterEntity

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/hello", methods=["GET"])
def hello():
    return "Hello world"


@auth.route("/register", methods=["POST"])
def register():
    json, code = service.register(request.get_json())
    return jsonify(json), code


@auth.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    token, code = service.login(auth)
    return jsonify(token), code
