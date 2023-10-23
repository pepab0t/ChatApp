import os

from application import create_flask
from application.auth.entity import UserRegisterEntity
from application.database import db, models
from application.repository import get_user_by_username, create_request
from application.api.service import approve_request

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

        for sen, rec in ((1, x) for x in range(15) if x != 1):
            sender = users[sen]
            receiver = users[rec]

            r = create_request(sender, receiver)
            approve_request(receiver.id, r.id)


if __name__ == "__main__":
    create_users()
