from flask import request
from flask_login import login_required, login_user, logout_user

from polydrive import app
from polydrive.services import bcrypt, message_builder
from polydrive.models import User


@app.route('/login', methods=['POST'])
def user_login():
    """
    This route is called to log the user in.
    """
    content = request.get_json()
    username = content['username']
    if username is None:
        return message_builder.bad_request('Username must be submitted.').http_format()
    user = User.query.filter_by(username=username).first()
    if user is None:
        return message_builder.unauthorized('Wrong credentials.').http_format()
    password = content['password']
    if not bcrypt.check_password_hash(user.password, password):
        return message_builder.unauthorized('Wrong credentials.').http_format()
    login_user(user)
    return message_builder.ok('Login successful.', user.serialized).http_format()


@app.route('/logout', methods=['GET'])
@login_required
def user_logout():
    """
    This route is called to log the user out.
    """
    logout_user()
    return message_builder.ok('Logout successful.').http_format()


@app.route('/register', methods=['POST'])
def user_register():
    content = request.get_json()
    username = content['username']
    password = content['password']
    email = content['email']
