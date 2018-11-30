from polydrive import manager
from polydrive.services.database import init_db, clear_db


@manager.command
def initdb():
    clear_db()
    init_db()
    print('Database initialized')
