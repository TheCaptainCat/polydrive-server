from flask import request
from flask_login import login_required, login_user, logout_user, current_user

from polydrive import app
from polydrive.services import bcrypt
from polydrive.services.messages import ok, created, bad_request, unauthorized
from polydrive.models import User


@app.route('/login', methods=['POST'])
def user_login():
    """
    Log the user in.

    :return: the user info if login is successful
    """
    content = request.get_json()
    username = content['username']
    if username is None:
        return bad_request('Username must be submitted.')
    user = User.query.filter_by(username=username).first()
    if user is None:
        return unauthorized('Wrong credentials.')
    password = content['password']
    if not bcrypt.check_password_hash(user.password, password):
        return unauthorized('Wrong credentials.')
    login_user(user)
    return ok('Login successful.', user.serialized)


@app.route('/logout', methods=['GET'])
@login_required
def user_logout():
    """
    Log the user out.
    """
    logout_user()
    return ok('Logout successful.')


@app.route('/register', methods=['POST'])
def user_register():
    """
    Create a new user with the provided information.
    """
    messages = []
    content = request.get_json()
    username = content.get('username', None)
    if username is None:
        messages.append('Missing parameter: username.')
    password = content.get('password', None)
    if password is None:
        messages.append('Missing parameter: password.')
    if len(messages) > 0:
        return bad_request(messages)
    email = content.get('email', None)
    user = User.query.filter_by(username=username).first()
    if user is not None:
        messages.append('Username already in use.')
    if email not in ['', None]:
        user = User.query.filter_by(email=email).first()
        if user is not None:
            messages.append('Email address already in use.')
    if len(password) < 6:
        messages.append('Password too short.')
    if len(messages) > 0:
        return bad_request(messages)
    user = User.create(username, password, email)
    return created('User created', user.serialized)


@app.route('/user', methods=['GET'])
@login_required
def user_get_details():
    return ok('', current_user.serialized)
