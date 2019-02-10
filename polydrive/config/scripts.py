from polydrive import manager
from polydrive.services.database import init_db, clear_db, fill_db


@manager.command
def init_fake_db():
    clear_db()
    init_db()
    fill_db('../data/data.yml')


@manager.command
def init_db():
    clear_db()
    init_db()
