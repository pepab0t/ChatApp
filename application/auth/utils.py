import jwt
import bcrypt
import datetime
from dotenv import get_key
from typing import TypedDict
from functools import partial

SALT: bytes = bcrypt.gensalt()
hashpw = partial(bcrypt.hashpw, salt=SALT)

SECRET = get_key(".env", "APP_JWT_SECRET")
assert SECRET is not None, "Unable to read APP_JWT_SECRET env variable"


class JWTEntity(TypedDict):
    id: int
    username: str
    exp: float


def create_jwt(id: int, username: str) -> str:
    return jwt.encode(
        {
            "id": id,
            "user": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(hours=5),
        },
        SECRET,
        algorithm="HS256",
    )


def decode_jwt(encoded_jwt: str):
    return jwt.decode(encoded_jwt, SECRET, ["HS256"])


def validate_jwt(encoded_jwt: str) -> JWTEntity | None:
    try:
        payload: JWTEntity = decode_jwt(encoded_jwt)  # type: ignore
    except jwt.PyJWTError:
        return None

    if datetime.datetime.fromtimestamp(
        payload["exp"], tz=datetime.timezone.utc
    ) < datetime.datetime.now(tz=datetime.timezone.utc):
        return None

    return payload


def encrypt_password(raw_password: str) -> str:
    return hashpw(raw_password.encode()).decode()


def validate_password(raw: str, encoded: str) -> bool:
    return bcrypt.checkpw(raw.encode(), encoded.encode())
