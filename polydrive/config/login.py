from flask_login import LoginManager

from polydrive import app
from polydrive.models import User

login = LoginManager(app)


@login.user_loader
def load_user(useres_id):
    return User.query.get(useres_id)
