from .database.models import User, Request, Message
from .database import db
from .exceptions import DatabaseError
from sqlalchemy.exc import IntegrityError
from .entity import UserRegisterEntity


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


def remove_friends(user1: User, user2: User):
    user1.friends.remove(user2)
    user2.friends.remove(user1)
    db.session.commit()


def create_request(user1: User, user2: User):
    r = Request(sender=user1, receiver=user2)
    db.session.add(r)
    db.session.commit()
    db.session.refresh(r)
    return r


def get_all_requests_received(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return None

    return user.requests_received


def get_request_by_id(id: int):
    return Request.query.get(id)


def get_user_by_id(id: int):
    return User.query.get(id)


def get_user_by_username(username: str):
    return User.query.filter_by(username=username).first()


def get_users_by_text(text: str):
    return User.query.filter(User.username.like(text)).order_by(User.username).all()


def create_message(sender: User, receiver: User, text: str):
    message = Message(sender=sender, receiver=receiver, text=text)
    db.session.add(message)
    db.session.commit()
    db.session.refresh(message)
    return message
