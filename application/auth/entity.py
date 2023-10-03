from pydantic import BaseModel, ValidationError, validator

from .utils import encrypt_password


class User(BaseModel):
    id: int
    username: str
    email: str


class UserRegisterEntity(BaseModel):
    username: str
    email: str
    password: str

    @validator("password")
    @classmethod
    def valid_password(cls, value: str) -> str:
        if len(value) < 4:
            raise ValueError("attribute must have at least 4 characters")
        return encrypt_password(value)


class UserLoginEntity(BaseModel):
    username: str
    password: str

    @validator("password")
    @classmethod
    def valid_password(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("attribute cannot be empty")
        return value

    @validator("username")
    @classmethod
    def valid_username(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("attribute cannot be empty")
        return value
