from flask import request
from .utils import validate_jwt
from ..exceptions import Unauthenticated
from functools import wraps
import inspect
from functools import cache


@cache
def arg_available(argname: str, fn):
    return argname in set(inspect.signature(fn).parameters.keys())


def token_valid(fn):
    @wraps(fn)
    def wrapper(*args, **kwds):
        token = request.cookies.get("access_token")
        if token is None:
            raise Unauthenticated()

        payload = validate_jwt(token)

        if payload is None:
            raise Unauthenticated()

        if arg_available("user_id", fn):
            return fn(*args, **kwds, user_id=payload["id"])
        return fn(*args, **kwds)

    return wrapper
