import os

from application import create_flask
from application.database import db, models
from application.entity import UserRegisterEntity

app = create_flask("sqlite:///database.db")

os.system("rm instance/database.db")
os.system("rd instance/database.db")


def create_users():
    with app.app_context():
        db.create_all()

        users = []
        pepa = {"username": "pepa", "email": "pepa@test.com", "password": "pepa"}
        u1 = {"username": "user1", "email": "user1@test.com", "password": "1234"}
        u2 = {"username": "user2", "email": "user2@test.com", "password": "1234"}
        u3 = {"username": "user3", "email": "user3@test.com", "password": "1234"}
        users.append(models.User(**UserRegisterEntity(**pepa).dict()))
        users.append(models.User(**UserRegisterEntity(**u1).dict()))
        users.append(models.User(**UserRegisterEntity(**u2).dict()))
        users.append(models.User(**UserRegisterEntity(**u3).dict()))

        db.session.add_all(users)
        db.session.commit()

        for sen, rec in ((1, 0), (2, 1), (2, 0)):
            r = models.Request(sender=users[sen], receiver=users[rec])
            db.session.add(r)
            db.session.commit()

        # room = models.Room()
        # room.users.append(users[0])
        # room.users.append(users[1])
        # db.session.add(room)
        # db.session.commit()


create_users()
