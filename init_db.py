import os

from application import create_flask
from application.auth.entity import UserRegisterEntity
from application.database import db, models
from application.repository import get_user_by_username

os.system("rm instance/database.db")
os.system("rd instance/database.db")

app = create_flask()


def create_users():
    with app.app_context():
        users = []

        pepa = {"username": "pepa", "email": "pepa@test.com", "password": "pepa"}
        eliska = {
            "username": "eliska",
            "email": "eliska@email.com",
            "password": "eliska",
        }
        users.append(models.User(**UserRegisterEntity(**pepa).dict()))
        users.append(models.User(**UserRegisterEntity(**eliska).dict()))

        for i in range(1, 26):
            user = {
                "username": f"user{i}",
                "email": f"user{i}@test.com",
                "password": "1234",
            }
            users.append(models.User(**UserRegisterEntity(**user).dict()))

        db.session.add_all(users)
        db.session.commit()

        print(get_user_by_username("pepa"))

        # for sen, rec in ((1, 0), (2, 1), (2, 0)):
        #     r = models.Request(sender=users[sen], receiver=users[rec])
        #     db.session.add(r)
        #     db.session.commit()

        # room = models.Room()
        # room.users.append(users[0])
        # room.users.append(users[1])
        # db.session.add(room)
        # db.session.commit()


if __name__ == "__main__":
    create_users()
