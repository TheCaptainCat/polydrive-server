from flask_sqlalchemy import SQLAlchemy

from polydrive import app

import env


def init_db():
    db.create_all()


app.config['SQLALCHEMY_DATABASE_URI'] = f'{env.sql_dbms}://{env.sql_user}:{env.sql_password}' \
                                        f'@{env.sql_server}/{env.sql_database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
