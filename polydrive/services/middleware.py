from functools import wraps
from flask import request
from flask_login import current_user

from polydrive.models import File
from polydrive.services.messages import not_found, unauthorized


def file_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        file_id = request.view_args.get('file_id', None)
        if file_id is None:
            return not_found('This resource does not exist')
        file = File.query.get(file_id)
        if file is None:
            return not_found('This resource does not exist')
        if file.owner_id != current_user.id:
            return unauthorized('You cannot access this resource.')
        request.file = file
        return f(*args, **kwargs)
    return decorated_function
