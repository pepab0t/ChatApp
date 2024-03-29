from flask_sqlalchemy.pagination import Pagination

from .. import repository
from ..exceptions import EntityNotFound, Forbidden, InvalidRequestException
from datetime import datetime


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
        raise InvalidRequestException("users are already friends")

    request = repository.create_request(user1, user2)
    if request is None:
        raise InvalidRequestException("This request already exists")
    return request.dict(), 201


def get_all_pending_requests_received(user_id, page: int | None = None):
    requests = repository.get_all_pending_requests_received(user_id, page)
    if requests is None:
        raise EntityNotFound(f"User ID `{user_id}` not found")

    data = list(map(lambda r: r.dict(), requests))
    if isinstance(requests, Pagination):
        return {"page": page, "pages": requests.pages, "data": data}

    return {"page": None, "pages": None, "data": data}


def get_pending_requests_count(user_id: int) -> int:
    user = repository.get_user_by_id(user_id)
    return repository.get_pending_requests_count(user)


def approve_request(user_id: int, request_id: int):
    if (request := repository.get_opened_request_by_id(request_id)) is None:
        raise EntityNotFound(f"Request ID `{request_id}` not found")
    if (user := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"Request ID `{user_id}` not found")

    if request.receiver != user:
        raise Forbidden(f"User {user_id} not allowed to accept request")

    repository.add_friends(request)
    return request.dict(), 201


def decline_request(user_id: int, request_id: int):
    if (request := repository.get_opened_request_by_id(request_id)) is None:
        raise EntityNotFound(f"Request ID `{request_id}` not found")
    if (user := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"Request ID `{user_id}` not found")

    if request.receiver != user:
        raise Forbidden(f"User {user_id} not allowed to decline request")

    request = repository.decline_request(request)
    return request.dict(), 200


def remove_friend(user_id: int, username: str):
    if (user1 := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"Request ID `{user_id}` not found")
    if (user2 := repository.get_user_by_username(username)) is None:
        raise EntityNotFound(f"Request ID `{username}` not found")

    if user2 not in set(user1.friends):
        raise InvalidRequestException("Users are not friends")

    repository.remove_friends(user1, user2)


def search(
    user_id: int,
    text: str,
    exclude_friends: bool,
    page: int | None = None,
    offset: int = 0,
):
    if text == "":
        return [], 200

    user = repository.get_user_by_id(user_id)
    text = f"%{text}%"

    if exclude_friends:
        users = repository.get_users_by_text_exlude_friends(
            user, text, page=page, offset=offset
        )
    else:
        users = repository.get_users_by_text(user, text, page=page)

    if isinstance(users, Pagination):
        page_ = users.page
        pages_ = users.pages
    else:
        page_ = None
        pages_ = None

    return {
        "page": page_,
        "pages": pages_,
        "data": [u.dict() for u in users],
    }, 200  ### ENDED HERE


def send_message(user_id: int, username: str, text: str, seen: bool):
    if text.strip() == "":
        raise InvalidRequestException("Message cannot be empty")
    if (sender := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"User ID `{user_id}` not found")
    if (receiver := repository.get_user_by_username(username)) is None:
        raise EntityNotFound(f"User `{username}` not found")

    if not already_friends(sender, receiver):
        raise InvalidRequestException("Users are not friends")

    message = repository.create_message(sender, receiver, text, seen)
    repository.update_last_room_message(sender, receiver, message)

    return message.dict(), 201


def add_last_message_to_friend(friend, message_dict):
    data = friend.dict()
    data["last_message"] = message_dict or None
    return data


def sorter(user):
    def inner(item):
        if not (lm := item["last_message"]):
            return (False, 0)
        print(datetime.strptime(lm["timestamp"], r"%H:%M %d.%m.%Y").timestamp())
        return (
            lm["seen"] if user.id == lm["receiver"]["id"] else True,
            -datetime.strptime(lm["timestamp"], r"%H:%M %d.%m.%Y").timestamp(),
        )

    return inner


def get_friends(user_id: int, page: int | None = None):
    ### ADD SORTING FRIENDS BY NEWEST MESSAGES

    user = repository.get_user_by_id(user_id)
    if user is None:
        raise EntityNotFound(f"User ID `{user_id}` not found")

    if page is None:
        friends = repository.get_friends(user)
    else:
        friends = repository.get_friends_paginate(user, page)

    if friends:
        messages = repository.get_last_messages(user, friends)
    else:
        messages = []

    data = []
    for friend, message in zip(friends, messages):
        item = friend.dict()
        item["last_message"] = message.dict() if message else dict()
        data.append(item)

    data.sort(
        key=sorter(user),
        reverse=False,
    )

    if isinstance(friends, Pagination):
        return {"page": friends.page, "pages": friends.pages, "data": data}, 200
    return {"page": None, "pages": None, "data": data}, 200


def get_room(user_id: int, username: str):
    if (user1 := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"User ID `{user_id}` not found")
    if (user2 := repository.get_user_by_username(username)) is None:
        raise EntityNotFound(f"User `{username}` not found")

    if not already_friends(user1, user2):
        raise InvalidRequestException("Users are not friends")

    room = repository.get_room(user1, user2)
    return {"room": room.get_name()}, 200


def get_messages(user_id: int, friend_username: str, page: int | None = None):
    if (user := repository.get_user_by_id(user_id)) is None:
        raise EntityNotFound(f"User ID `{user_id}` not found")
    if (friend := repository.get_user_by_username(friend_username)) is None:
        raise EntityNotFound(f"User `{friend_username}` not found")

    messages = repository.get_messages(user, friend, page)
    data = map(lambda m: m.dict(), messages)
    if isinstance(messages, Pagination):
        return {"page": page, "pages": messages.pages, "data": list(data)}, 200

    return {"page": None, "pages": None, "data": list(data)}, 200


def see_messages(user_id: int, username_other: str):
    user = repository.get_user_by_id(user_id)
    friend = repository.get_user_by_username(username_other)
    messages = repository.get_unseen_messages(user, friend)
    repository.see_messages(messages)

    return {}, 204
