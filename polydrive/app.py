import os
from flask import Flask
from flask_cors import CORS
from flask_script import Manager

import env


def make_path(path):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), path))


app = Flask(__name__)
CORS(app, supports_credentials=True)

app.debug = env.debug
app.config['SECRET_KEY'] = env.secret_key

app.config['UPLOAD_FOLDER'] = make_path(env.upload_folder)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.env = env.environment

manager = Manager(app)
