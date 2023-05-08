from ..database import db, IntegrityError
from ..entity import UserRegisterEntity, UserDict
from ..database.models import User
from ..exceptions import DatabaseError, EntityNotFound


def register_user(user: UserRegisterEntity) -> UserDict:
    new_user = User(**user.dict())
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError as e:
        raise DatabaseError(e.args[0], 422)

    db.session.refresh(new_user)
    del new_user.password
    return new_user.dict()  # type: ignore


def get_user_by_username(username: str):
    return User.query.filter_by(username=username).first()
