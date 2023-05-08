from typing import Any
from .exceptions import InvalidRequestException, DatabaseError, EntityNotFound
from flask import jsonify
from functools import wraps
from typing import Type


class _associate_exception:
    def __init__(self, exc: Type[Exception]) -> None:
        self.exc = exc

    def __call__(self, fn) -> Any:
        fn.exc = self.exc
        return fn


@_associate_exception(InvalidRequestException)
def handle_invalid_body(exc: InvalidRequestException):
    """handle InvalidFormException"""
    return jsonify({"message": exc.message}), exc.status_code


@_associate_exception(DatabaseError)
def handle_database_error(exc: DatabaseError):
    return jsonify({"message": exc.message}), exc.status_code


@_associate_exception(EntityNotFound)
def handle_entity_404(exc: EntityNotFound):
    return jsonify({"message": exc.message}), exc.status_code
