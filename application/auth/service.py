from ..exceptions import (
    InvalidRequestException,
    EntityNotFound,
    Unauthenticated,
    InvalidJWT,
    ExpiredJWT,
    TolerableExpiredJWT,
)
from ..entity import UserLoginEntity, UserRegisterEntity, ValidationError
from . import utils
from .. import repository


def prepare_validation_error(err: ValidationError):
    errors = err.errors()[0]
    return InvalidRequestException(f"{errors['loc'][0]}: {errors['msg']}", 422)


def register(body):
    if not body:
        raise InvalidRequestException("Empty body not accepted", 400)

    try:
        user = UserRegisterEntity(**body)
    except ValidationError as err:
        raise prepare_validation_error(err)

    return repository.register_user(user).dict(), 201


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

    payload = create_tokens(user_db.id)
    return payload, 200


def create_tokens(user_id):
    return {
        "access": utils.create_access_token(user_id),
        "refresh": utils.create_refresh_token(user_id),
        "id": user_id,
    }


def validate(token: str):
    body = {}
    try:
        body["payload"] = utils.validate_jwt(token)
    except (InvalidJWT, ExpiredJWT):
        body["state"] = "false"
    except TolerableExpiredJWT:
        body["state"] = "refresh"
    else:
        body["state"] = "true"

    return body, 200
