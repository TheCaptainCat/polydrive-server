from polydrive import manager
from polydrive.services.database import init_db


@manager.command
def initdb():
    init_db()
    print('Database initialized')
