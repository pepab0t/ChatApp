from application.entity import UserRegisterEntity
from application.database import db, models

from application import create_app

import os

app = create_app()

os.system("rm instance/database.db")

with app.app_context():
    db.create_all()

    user1 = UserRegisterEntity(
        username="user1", email="user1@gmail.com", password="1234"
    )
    user2 = UserRegisterEntity(
        username="user2", email="user2@gmail.com", password="1234"
    )

    u1 = models.User(**user1.dict())
    u2 = models.User(**user2.dict())

    db.session.add_all([u1, u2])
    db.session.commit()
    exit()

    r = models.Request(sender=u1, receiver=u2)
    db.session.add(r)
    db.session.commit()
