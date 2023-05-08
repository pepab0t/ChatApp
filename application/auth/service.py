from ..exceptions import InvalidRequestException, EntityNotFound, Unauthenticated
from ..entity import UserLoginEntity, UserRegisterEntity, ValidationError
from typing import Any
from . import utils

from . import repository


def prepare_validation_error(err: ValidationError):
    errors = err.errors()[0]
    return InvalidRequestException(f"{errors['loc'][0]}: {errors['msg']}", 422)


def register(body: dict[str, str]):
    if not body:
        raise InvalidRequestException("Empty body not accepted", 400)

    try:
        user = UserRegisterEntity(**body)
    except ValidationError as err:
        raise prepare_validation_error(err)

    return repository.register_user(user), 201


def login(auth):
    if auth is None:
        raise Unauthenticated()

    try:
        user = UserLoginEntity(username=auth.username, password=auth.password)
    except ValidationError as err:
        raise prepare_validation_error(err)

    if (user_db := repository.get_user_by_username(user.username)) is None:
        raise EntityNotFound(f"User `{user.username}` not found")

    if not utils.validate_password(user.password, user_db.password):
        raise Unauthenticated()

    return {"token": utils.create_jwt(user_db.id, user_db.username)}, 200
