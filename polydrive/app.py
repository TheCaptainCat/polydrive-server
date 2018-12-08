from flask import Flask
from flask_cors import CORS
from flask_script import Manager

import env


app = Flask(__name__)
CORS(app, supports_credentials=True)

app.debug = env.debug
app.config['SECRET_KEY'] = env.secret_key

app.env = env.environment

manager = Manager(app)
