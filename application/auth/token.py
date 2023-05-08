from flask import request
from .utils import validate_jwt
from ..exceptions import Unauthenticated
from functools import wraps


def token_valid(fn):
    @wraps(fn)
    def wrapper(*args, **kwds):
        auth = request.headers.get("Authorization")
        if auth is None:
            raise Unauthenticated()

        token = auth.split(" ")[1]
        payload = validate_jwt(token)

        if payload is None:
            raise Unauthenticated()

        return fn(*args, **kwds, user_id=payload["id"])

    return wrapper
