from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from application import login

class User(UserMixin):

    id = ""
    username = ""
    password_hash = ""

    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):

    u = User("admin")
    return u