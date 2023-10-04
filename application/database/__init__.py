import typing as t
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import ROOT
from sqlalchemy.exc import IntegrityError


def create_all(app):
    with app.app_context():
        db.create_all()


class SQLAlchemyCustom(SQLAlchemy):
    def init_app(self, app: Flask) -> None:
        super().init_app(app)
        create_all(app)


db = SQLAlchemyCustom()
