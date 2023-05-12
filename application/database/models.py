from __future__ import annotations
from . import db
from datetime import datetime
from sqlalchemy.orm import validates

friends = db.Table(
    "friends",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE")),
    db.Column("friend_id", db.Integer, db.ForeignKey("user.id", ondelete="CASCADE")),
    # db.UniqueConstraint("user_id", "friend_id", name="friends"),
)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    friends = db.relationship(
        "User",
        secondary=friends,
        primaryjoin=id == friends.c.user_id,
        secondaryjoin=id == friends.c.friend_id,
    )

    def dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}


class Request(db.Model):
    __tablename__ = "request"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    accepted = db.Column(db.Boolean, default=lambda: None)

    sender = db.relationship("User", backref="requests_sent", foreign_keys=[sender_id])
    receiver = db.relationship(
        "User", backref="requests_received", foreign_keys=[receiver_id]
    )

    # __table_args__ = (
    #     db.UniqueConstraint(sender_id, receiver_id, name="unique_sender_receiver"),
    # )

    def dict(self):
        return {
            "id": self.id,
            "sender": self.sender.dict(),
            "receiver": self.receiver.dict(),
            "timestamp": self.timestamp,
            "accepted": self.accepted,
        }

    # @validates("sender_id", "receiver_id")
    # def validate_unique_sender_receiver(self, key, value):
    #     if self.accepted is None:
    #         existing_relationship = User.query.filter_by(
    #             sender_id=value,
    #             receiver_id=getattr(
    #                 self, "sender_id" if key == "receiver_id" else "receiver_id"
    #             ),
    #             accepted=None,
    #         ).first()
    #         if existing_relationship and existing_relationship != self:
    #             raise ValueError(
    #                 "The combination of sender_id and receiver_id must be unique when accepted is None"
    #             )
    #     return value


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    text = db.Column(db.String(256), nullable=False)

    sender = db.relationship("User", backref="messages_sent", foreign_keys=[sender_id])
    receiver = db.relationship(
        "User",
        backref="messages_received",
        foreign_keys=[receiver_id],
    )

    def dict(self):
        return {
            "id": self.id,
            "sender": self.sender.username,
            "receiver": self.receiver.username,
            "text": self.text,
            "timestamp": self.timestamp,
        }
