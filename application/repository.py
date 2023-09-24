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


def get_user_by_id(id: int) -> User:
    return User.query.get(id)


def get_friends_query(user: User):
    q = (
        User.query.filter(User.friends.any(User.id == user.id))
        # .join(Room, User.rooms)
        # .join(Message, Room.last_message)
        # .order_by(Message.timestamp.desc())
    )

    return q


def get_friends(user: User):
    return get_friends_query(user).all()


def get_friends_paginate(user: User, page):
    query = get_friends_query(user)
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


def create_message(sender: User, receiver: User, text: str, seen: bool):
    message = Message(sender=sender, receiver=receiver, text=text, seen=seen)
    db.session.add(message)
    db.session.commit()
    db.session.refresh(message)
    return message


def get_room(user1: User, user2: User) -> Room:
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


def update_last_room_message(user1: User, user2: User, last_message: Message):
    room = get_room(user1, user2)
    room.last_message_id = last_message.id
    db.session.commit()


def get_messages_query(user: User, friend: User):
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
    return messages


def get_messages(user: User, friend: User, page: int | None = None):
    messages = get_messages_query(user, friend)
    if page is None:
        return messages.all()
    return messages.paginate(page=page, per_page=MESSAGES_PER_PAGE, error_out=True)


def get_unseen_messages(user: User, friend: User):
    q = Message.query.filter(
        Message.seen == False, Message.sender == friend, Message.receiver == user
    )
    return q.all()


def get_last_messages(user: User, friends: list[User]) -> list[Message | None]:
    messages = []
    for friend in friends:
        message = (
            Message.query.filter(
                or_(
                    and_(
                        Message.sender_id == user.id, Message.receiver_id == friend.id
                    ),
                    and_(
                        Message.receiver_id == user.id, Message.sender_id == friend.id
                    ),
                )
            )
            .order_by(Message.timestamp.desc())
            .first()
        )

        messages.append(message)

    return messages


def see_messages(messages: list[Message]) -> None:
    for message in messages:
        message.seen = True
        print(message)

    db.session.commit()
