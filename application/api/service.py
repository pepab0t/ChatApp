from . import repository
from ..exceptions import EntityNotFound, Forbidden, InvalidRequestException


def already_friends(user1, user2):
    return user2 in set(user1.friends)


def send_request(user_id: int, user_to: str):
    if (user1 := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"User `{user_id}` not found")
    if (user2 := repository.get_user_by_username(user_to)) is None:
        raise EntityNotFound(f"User `{user_to}` not found")

    if user1 == user2:
        raise InvalidRequestException(
            f"user `{user1.username}` cannot add himself as a friend"
        )

    if already_friends(user1, user2):
        raise InvalidRequestException("users are already friends", 400)

    request = repository.create_request(user1, user2)
    return request.dict(), 201


def get_all_requests_received(user_id):
    requests = repository.get_all_requests_received(user_id)
    if requests is None:
        raise EntityNotFound(f"User ID `{user_id}` not found")

    return [r.dict() for r in requests]


def approve_request(user_id: int, request_id: int):
    if (request := repository.get_request_by_id(request_id)) is None:
        raise EntityNotFound(f"Request ID `{request_id}` not found")
    if (user := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"Request ID `{user_id}` not found")

    if request.receiver != user:
        raise Forbidden(f"User {user_id} not allowed to accept request")

    repository.add_friends(request)
    return request.dict(), 201


def search(user_id: int, text: str):
    user = repository.get_user_by_id(user_id)
    text = f"%{text}%"
    users = repository.get_users_by_text(text)
    users.remove(user)
    return [u.dict() for u in users], 200


def send_message(user_id: int, username: str, text: str):
    if text == "":
        raise InvalidRequestException("Message cannot be empty")
    if (sender := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"Request ID `{user_id}` not found")
    if (receiver := repository.get_user_by_username(username)) is None:
        raise EntityNotFound(f"Request ID `{username}` not found")

    if not already_friends(sender, receiver):
        raise InvalidRequestException("Users are not friends")

    message = repository.create_message(sender, receiver, text)
    return message.dict(), 201
