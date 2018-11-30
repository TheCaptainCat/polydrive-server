from flask_sqlalchemy import SQLAlchemy

from polydrive import app

import env


def init_db():
    db.create_all()


def clear_db():
    db.drop_all()


app.config['SQLALCHEMY_DATABASE_URI'] = env.sql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
