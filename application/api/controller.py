import json

from flask import Blueprint, jsonify, request
from flask.wrappers import Response

from ..auth.token import token_valid
from ..exceptions import InvalidRequestException
from . import service

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/test")
@token_valid()
def test():
    return jsonify(message="API is working"), 200


@api.route("/send_request/<string:username>", methods=["POST"])
@token_valid()
def send_request(user_id: int, username: str):
    r, code = service.send_request(user_id, username)
    return jsonify(r), code


@api.route("/approve", methods=["POST"])
@token_valid()
def approve_request(user_id: int):
    if (request_id := request.args.get("request_id", type=int)) is None:
        raise InvalidRequestException("no query parameter `request_id`")

    req, code = service.approve_request(user_id, request_id)
    return jsonify(req), code


@api.route("/decline", methods=["POST"])
@token_valid()
def decline_request(user_id: int):
    if (request_id := request.args.get("request_id", type=int)) is None:
        raise InvalidRequestException("no query parameter `request_id`")

    req, code = service.decline_request(user_id, request_id)
    return jsonify(req), code


@api.route("/requests", methods=["GET"])
@token_valid()
def get_requests(user_id: int):
    page: int | None = request.args.get("page", None, type=lambda x: int(x) or None)
    requests = service.get_all_pending_requests_received(user_id, page)
    return jsonify(requests), 200


@api.route("/requests/count", methods=["GET"])
@token_valid()
def get_requests_count(user_id: int):
    count: int = service.get_pending_requests_count(user_id)
    return jsonify({"count": count}), 200


@api.route("/delete_friend/<string:username>", methods=["DELETE"])
@token_valid()
def remove_friend(user_id: int, username: str):
    service.remove_friend(user_id, username)
    return jsonify(), 204


@api.route("/search", methods=["GET"])
@token_valid()
def search(user_id: int):
    if (text := request.args.get("search", type=str)) is None:
        raise InvalidRequestException("no query parameter `search`")
    page: int | None = request.args.get("page", None, type=lambda x: int(x) or None)
    exclude_friends = request.args.get(
        "exclude_friends", "false", type=lambda x: x.lower() in {"true", "1"}
    )
    results, code = service.search(user_id, text, exclude_friends, page)  # type: ignore
    return jsonify(results), code


@api.route("/send_message/<string:username>", methods=["POST"])
@token_valid()
def send_message(user_id: int, username: str):
    message = request.get_json().get("message", None)
    seen = request.get_json().get("seen", None)
    if message is None:
        raise InvalidRequestException("Missing json body key `message`")
    if seen is None:
        raise InvalidRequestException("Missing json body key `seen`")
    result, code = service.send_message(user_id, username, message, seen)
    return jsonify(result), code


@api.route("/friends", methods=["GET"])
@token_valid()
def get_friends(user_id: int):
    page = request.args.get("page", None, type=int)
    friends, code = service.get_friends(user_id, page)
    return jsonify(friends), code


@api.get("/room/<string:username>")
@token_valid()
def get_room(user_id: int, username: str):
    room, code = service.get_room(user_id, username)
    return jsonify(room), code


@api.get("/messages/<string:username>")
@token_valid()
def get_messages(user_id: int, username: str):
    page: int | None = request.args.get("page", None, type=int)
    messages, code = service.get_messages(user_id, username, page)
    return jsonify(messages), code


@api.get("/see_messages/<string:username>")
@token_valid()
def see_messages(user_id: int, username: str):
    response, code = service.see_messages(user_id, username)
    return jsonify(response), code
