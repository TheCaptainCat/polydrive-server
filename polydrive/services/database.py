import yaml

from polydrive.services import db
from polydrive.services.files import make_path
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
            u = User(username=user['username'], password=user['password'])
            db.session.add(u)
        db.session.commit()

