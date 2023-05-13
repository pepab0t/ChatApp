from application.entity import UserRegisterEntity
from application.database import db, models

from application import create_app

import os

app = create_app()

os.system("rm instance/database.db")


def create_users():
    with app.app_context():
        db.create_all()

        users = []
        for i in range(1, 5):
            user = UserRegisterEntity(
                username=f"u{i}", email=f"user{i}@gmail.com", password="1234"
            )
            users.append(models.User(**user.dict()))

        db.session.add_all(users)
        db.session.commit()

        r = models.Request(sender=users[0], receiver=users[1])
        db.session.add(r)
        db.session.commit()

        room = models.Room()
        room.users.append(users[0])
        room.users.append(users[1])
        db.session.add(room)
        db.session.commit()


create_users()
