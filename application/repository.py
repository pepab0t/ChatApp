from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError

from config import MESSAGES_PER_PAGE, REQUESTS_PER_PAGE, USERS_PER_PAGE

from .database import db
from .database.models import Message, Request, Room, User
from .entity import UserRegisterEntity
from .exceptions import DatabaseError


def register_user(user: UserRegisterEntity):
    new_user = User(**user.dict())
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError as e:
        raise DatabaseError(e.args[0], 422)

    db.session.refresh(new_user)
    del new_user.password
    return new_user


def add_friends(request: Request):
    request.sender.friends.append(request.receiver)
    request.receiver.friends.append(request.sender)
    request.accepted = True
    db.session.commit()
    return request


def decline_request(request: Request):
    request.accepted = False
    db.session.commit()
    return request


def remove_friends(user1: User, user2: User):
    user1.friends.remove(user2)
    user2.friends.remove(user1)
    db.session.commit()


def create_request(user1: User, user2: User):
    r = (
        Request.query.filter_by(accepted=None)
        .filter(
            and_((Request.sender == user1), (Request.receiver == user2))
            | and_((Request.sender == user2), (Request.receiver == user1))
        )
        .first()
    )
    if r is not None:
        raise DatabaseError("This request already exists", 422)

    r = Request(sender=user1, receiver=user2)
    db.session.add(r)
    db.session.commit()
    db.session.refresh(r)
    return r


def get_all_pending_requests_received(user_id: int, page: int | None = None):
    user = User.query.get(user_id)
    if user is None:
        return None

    query = Request.query.filter(
        Request.accepted == None, Request.receiver_id == user_id
    ).order_by(Request.timestamp.desc())

    if page is None:
        return query.all()
    return query.paginate(page=page, per_page=REQUESTS_PER_PAGE, error_out=True)


def get_request_by_id(id: int):
    return Request.query.get(id)


def get_opened_request_by_id(id: int):
    out = get_request_by_id(id)
    return out if out.accepted is None else None


def get_user_by_id(id: int):
    return User.query.get(id)


def get_friends_paginate(user: User, page):
    query = user.query.filter(User.friends.any(User.id == user.id))
    return query.paginate(page=page, per_page=USERS_PER_PAGE, error_out=True)


def get_user_by_username(username: str):
    return User.query.filter_by(username=username).first()


def get_users_by_text(user: User, text: str, page: int | None = None):
    q = (
        User.query.except_(  # .filter(User.id != user.id)
            User.query.filter(User.id == user.id)
        )  # .filter(User.id != user.id)
        .filter(User.username.like(text))
        .order_by(User.username)
    )
    if page is None:
        return q.all()
    return q.paginate(page=page, per_page=USERS_PER_PAGE, error_out=True)


def get_users_by_text_exlude_friends(user: User, text: str, page: int | None = None):
    q = (
        User.query.filter(User.username.like(text))
        .except_(User.query.filter(User.id == user.id))  # .filter(User.id != user.id)
        .filter(
            ~User.friends.any(User.id == user.id),
            ~User.requests_received.any(
                and_(Request.sender_id == user.id, Request.accepted == None)
            ),
        )
        .order_by(User.username)
    )
    if page is None:
        return q.all()
    return q.paginate(page=page, per_page=USERS_PER_PAGE, error_out=True)


def create_message(sender: User, receiver: User, text: str):
    message = Message(sender=sender, receiver=receiver, text=text)
    db.session.add(message)
    db.session.commit()
    db.session.refresh(message)
    return message


def get_room(user1: User, user2: User):
    room = (
        Room.query.filter(Room.users.any(User.id == user1.id))
        .filter(Room.users.any(User.id == user2.id))
        .first()
    )

    if room is not None:
        return room

    room = Room()
    room.users.append(user1)
    room.users.append(user2)
    db.session.add(room)
    db.session.commit()
    db.session.refresh(room)
    return room


def get_messages(user: User, friend: User, page: int | None = None):
    messages = (
        Message.query.filter(
            or_(
                Message.sender.has(id=user.id),
                Message.sender.has(id=friend.id),
            )
        )
        .filter(
            or_(
                Message.receiver.has(id=user.id),
                Message.receiver.has(id=friend.id),
            )
        )
        .order_by(Message.timestamp)  # .desc()
    )

    if page is None:
        return messages.all()
    return messages.paginate(page=page, per_page=MESSAGES_PER_PAGE, error_out=True)


def get_last_message(user: User, friend: User) -> Message | None:
    # user.messages_received
    messages = list(filter(lambda m: m.receiver == friend, user.messages_sent)) + list(
        filter(lambda m: m.sender == friend, user.messages_received)
    )
    if not messages:
        return None
    return sorted(messages, key=lambda m: m.timestamp, reverse=True)[0]
