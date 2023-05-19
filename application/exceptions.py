class ChatAppException(Exception):
    """Base Exception class for this app"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"

    def __str__(self) -> str:
        return repr(self)


class InvalidRequestException(ChatAppException):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message, status_code)


class EntityNotFound(ChatAppException):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message, status_code)


class DatabaseError(ChatAppException):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message, status_code)


class Unauthenticated(ChatAppException):
    def __init__(
        self, message: str = "Unauthenticated", status_code: int = 401
    ) -> None:
        super().__init__(message, status_code)


class Forbidden(ChatAppException):
    def __init__(self, message: str = "Forbidden", status_code: int = 403) -> None:
        super().__init__(message, status_code)


class JWTError(ChatAppException):
    pass


class InvalidJWT(JWTError):
    def __init__(self, message: str = "JWT is invalid", status_code: int = 401) -> None:
        super().__init__(message, status_code)


class ExpiredJWT(JWTError):
    def __init__(self, message: str = "JWT is expired", status_code: int = 401) -> None:
        super().__init__(message, status_code)


class TolerableExpiredJWT(JWTError):
    def __init__(
        self,
        payload,
        message: str = "JWT is expired, but within tolerance",
        status_code: int = 401,
    ) -> None:
        super().__init__(message, status_code)
        self.payload = payload
