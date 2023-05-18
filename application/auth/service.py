from ..exceptions import InvalidRequestException, EntityNotFound, Unauthenticated
from ..entity import UserLoginEntity, UserRegisterEntity, ValidationError
from . import utils
from flask_jwt_extended import create_access_token
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

    return create_tokens(user_db.id), 200


def create_tokens(user_id):
    return {
        "access": utils.create_access_token(user_id),
        "refresh": utils.create_refresh_token(user_id),
    }
