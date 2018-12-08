from polydrive import manager
from polydrive.services.database import init_db, clear_db, fill_db


@manager.command
def initdb():
    clear_db()
    init_db()
    fill_db('../data/data.yml')
    print('Database initialized')
