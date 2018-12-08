import yaml

from polydrive.config import db
from polydrive.config.files import make_path
from polydrive.models import User


def init_db():
    db.create_all()


def clear_db():
    db.drop_all()


def fill_db(path):
    with open(make_path(path)) as f:
        y = yaml.load(f)

        users = y.get('users', None)
        for user in users:
            u = User.create(username=user['username'], password=user['password'], email=None)
            db.session.add(u)
        db.session.commit()

