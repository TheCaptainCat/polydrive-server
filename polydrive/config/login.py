from flask_login import LoginManager

from polydrive import app
from polydrive.models import User

login = LoginManager(app)


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)
