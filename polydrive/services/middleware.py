from functools import wraps
from flask import request
from flask_login import current_user

from polydrive.models import File, Version
from polydrive.services.messages import not_found, unauthorized, bad_request


def file_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        file_id = request.view_args.get('file_id', None)
        if file_id is None:
            return bad_request('No file id provided.')
        file = File.query.get(file_id)
        if file is None:
            return not_found('This resource does not exist.')
        if file.owner_id != current_user.id:
            return unauthorized('You cannot access this resource.')
        return f(*args, **kwargs)
    return decorated_function


def file_version_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        file_id = request.view_args.get('file_id', None)
        version_id = request.view_args.get('version_id', None)
        if version_id is None or file_id is None:
            return bad_request('No file version id provided.')
        version = Version.query.filter_by(id=version_id, file_id=file_id).first()
        if version is None:
            return not_found('This resource does not exist.')
        return f(*args, **kwargs)
    return decorated_function
