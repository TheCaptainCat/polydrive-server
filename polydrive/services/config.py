from flask_sqlalchemy import SQLAlchemy

from polydrive import app
from polydrive.services.files import make_path

import env

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + make_path(env.sqlite_file)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
