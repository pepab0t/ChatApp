import jwt
import os
import bcrypt
import datetime
from dotenv import get_key
from typing import TypedDict
from functools import partial
from ..exceptions import InvalidJWT, ExpiredJWT, TolerableExpiredJWT

SALT: bytes = bcrypt.gensalt()
_hashpw = partial(bcrypt.hashpw, salt=SALT)

SECRET = get_key(".env", "APP_JWT_SECRET")
# ACCESS_TOKEN_DURATION_MINS = float(os.getenv("ACCESS_TOKEN_DURATION_MINS"))  # type: ignore
# ACCESS_TOKEN_TOLERANCE_MINS = float(os.getenv("ACCESS_TOKEN_TOLERANCE_MINS"))  # type: ignore
# REFRESH_TOKEN_DURATION_HOURS = float(os.getenv("REFRESH_TOKEN_DURATION_HOURS"))  # type: ignore
assert SECRET is not None, "Unable to read APP_JWT_SECRET env variable"


class JWTEntity(TypedDict):
    id: int
    exp: float


def _create_jwt(id: int, fn) -> str:
    return jwt.encode(
        {
            "id": id,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(**fn()),
        },
        SECRET,
        algorithm="HS256",
    )


create_access_token = partial(_create_jwt, fn=lambda: {"minutes": float(os.getenv("ACCESS_TOKEN_DURATION_MINS"))})  # type: ignore
create_refresh_token = partial(_create_jwt, fn=lambda: {"hours": float(os.getenv("REFRESH_TOKEN_DURATION_HOURS"))})  # type: ignore


def _decode_jwt(encoded_jwt: str):
    return jwt.decode(encoded_jwt, SECRET, ["HS256"])


def validate_jwt(encoded_jwt: str) -> JWTEntity:
    """validate a given jwt

    Args:
        encoded_jwt (str)

    Raises:
        InvalidJWT: Raised when JWT is not valid
        TolerableExpiredJWT: Raised when JWT is expired, but within tolerance
        ExpiredJWT: Raised when JWT is valid, but expired

    Returns:
        JWTEntity
    """
    try:
        payload: JWTEntity = _decode_jwt(encoded_jwt)  # type: ignore
    except jwt.DecodeError:
        raise InvalidJWT()
    except jwt.ExpiredSignatureError:
        # if token is expired, try if expired within tolerance
        try:
            payload = jwt.decode(encoded_jwt, SECRET, ["HS256"], leeway=datetime.timedelta(minutes=float(os.getenv("ACCESS_TOKEN_TOLERANCE_MINS"))))  # type: ignore
        except jwt.ExpiredSignatureError:
            # if not in tolerance raise ExpiredJWT
            raise ExpiredJWT()
        else:
            # if in tolerance raise TolerableExpiredJWT
            raise TolerableExpiredJWT(payload=payload)

    return payload


def encrypt_password(raw_password: str) -> str:
    return _hashpw(raw_password.encode()).decode()


def validate_password(raw: str, encoded: str) -> bool:
    return bcrypt.checkpw(raw.encode(), encoded.encode())
