from flask import Blueprint, jsonify, request
from ..auth.token import token_valid
from ..exceptions import InvalidRequestException
from . import service

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/approve", methods=["POST"])
@token_valid
def add_friend(user_id: int):
    if (request_id := request.args.get("request_id", type=int)) is None:
        raise InvalidRequestException("no query parameter `request_id`")

    req, code = service.approve_request(user_id, request_id)
    return jsonify(req), code


@api.route("/decline", methods=["POST"])
@token_valid
def decline_request(user_id: int):
    if (request_id := request.args.get("request_id", type=int)) is None:
        raise InvalidRequestException("no query parameter `request_id`")

    req, code = service.decline_request(user_id, request_id)
    return jsonify(req), code


@api.route("/delete_friend/<string:username>", methods=["DELETE"])
@token_valid
def remove_friend(user_id: int, username: str):
    service.remove_friend(user_id, username)
    return jsonify({"message": "success"}), 204


@api.route("/send_request/<string:username>", methods=["POST"])
@token_valid
def send_request(user_id: int, username: str):
    r, code = service.send_request(user_id, username)
    return jsonify(r), code


@api.route("/requests", methods=["GET"])
@token_valid
def get_requests(user_id: int):
    requests = service.get_all_pending_requests_received(user_id)
    return jsonify(requests), 200


@api.route("/search", methods=["GET"])
@token_valid
def search(user_id: int):
    if (text := request.args.get("search")) is None:
        raise InvalidRequestException("no query parameter `search`")
    results, code = service.search(user_id, text)
    return jsonify(results), code


@api.route("/send_message/<string:username>", methods=["POST"])
@token_valid
def send_message(user_id: int, username: str):
    message = request.get_json().get("message", None)
    if message is None:
        raise InvalidRequestException("Missing body key `message`")
    result, code = service.send_message(user_id, username, message)
    return jsonify(result), code


@api.route("/friends", methods=["GET"])
@token_valid
def get_friends(user_id: int):
    friends, code = service.get_friends(user_id)
    return jsonify(friends), code
