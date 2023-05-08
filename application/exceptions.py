from werkzeug.exceptions import HTTPException, Forbidden


class ChatAppException(Exception):
    """Base Exception class for this app"""


class InvalidRequestException(ChatAppException):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code


class EntityNotFound(ChatAppException):
    def __init__(self, message: str, status_code: int = 404) -> None:
        self.message = message
        self.status_code = status_code


class DatabaseError(ChatAppException):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code


class Unauthenticated(HTTPException):
    code = 401
    description = "Unauthenticated"
