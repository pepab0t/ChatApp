from __future__ import annotations
from . import db
from datetime import datetime

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
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    accepted = db.Column(db.Boolean, nullable=False, default=lambda: False)

    # db.UniqueConstraint(sender_id, receiver_id)
    sender = db.relationship("User", backref="requests_sent", foreign_keys=[sender_id])
    receiver = db.relationship(
        "User", backref="requests_received", foreign_keys=[receiver_id]
    )

    def dict(self):
        return {
            "id": self.id,
            "sender": self.sender.dict(),
            "receiver": self.receiver.dict(),
            "timestamp": self.timestamp,
            "accepted": self.accepted,
        }


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
