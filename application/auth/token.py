from flask import request, url_for
from .utils import validate_jwt
from ..exceptions import (
    Unauthenticated,
    InvalidJWT,
    ExpiredJWT,
    JWTError,
    TolerableExpiredJWT,
)
import inspect
from functools import cache, partial, update_wrapper, wraps
from typing import Literal

TokenKey = Literal["access_token"] | Literal["refresh_token"]
TOKEN_FROM = "cookies"


@cache
def arg_available(argname: str, fn):
    return argname in set(inspect.signature(fn).parameters.keys())


def parse_token(
    key: TokenKey,
    get_from: Literal["cookies"] | Literal["body"] | Literal["query"] = "cookies",
):
    """Parse a token

    Args:
        - key (Literal[&quot;access_token&quot;] | Literal[&quot;refresh_token&quot;]): key of the token
        - get_from (Literal[&quot;cookies&quot;] | Literal[&quot;body&quot;] | Literal[&quot;query&quot;], optional): Location where to look for token. Defaults to "cookies".

    Raises:
        Unauthenticated: If token not found

    Returns:
        str: parsed token
    """
    match get_from:
        case "cookies":
            token = request.cookies.get(key)
        case "query":
            token = request.args.get(key)
        case "body":
            token = request.get_json().get(key)
        case _:
            token = None

    if token is None:
        raise Unauthenticated(f"missing {key}")
    return token


class token_valid:
    def __init__(
        self, token_name: TokenKey = "access_token", inject_error: bool = False
    ) -> None:
        self.token_name: TokenKey = token_name
        self.inject_error = inject_error

    def __call__(self, fn):
        if self.inject_error:
            wrapper = partial(self._with_error, fn=fn)
        else:
            wrapper = partial(self._without_error, fn=fn)
        wrapper = update_wrapper(wrapper, fn)
        return wrapper

    def _without_error(self, fn, *args, **kwds):
        token = parse_token(self.token_name, get_from=TOKEN_FROM)

        try:
            payload = validate_jwt(token)
        except JWTError as e:
            raise Unauthenticated(f"Invalid {self.token_name}")

        if arg_available("user_id", fn):
            if "user_id" not in kwds:
                kwds["user_id"] = payload["id"] if payload else -1
            return fn(*args, **kwds)
        return fn(*args, **kwds)

    def _with_error(self, fn, *args, **kwds):
        if not arg_available("errors", fn):
            raise AttributeError(
                f"Function `{fn.__name__}` missing argument `errors`. To avoid this use `@{self.__class__.__name__}(inject_error=False)`"
            )
        token = parse_token(self.token_name, get_from=TOKEN_FROM)
        payload = None
        if "errors" not in kwds:
            kwds["errors"] = list()

        try:
            payload = validate_jwt(token)
        except JWTError as err:
            kwds["errors"].append(err)
            payload = getattr(err, "payload", None)

        if arg_available("user_id", fn):
            if "user_id" not in kwds:
                kwds["user_id"] = payload["id"] if payload else -1
            return fn(*args, **kwds)
        return fn(*args, **kwds)
