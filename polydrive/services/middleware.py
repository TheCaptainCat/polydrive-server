from functools import wraps
from flask import request
from flask_login import current_user

from polydrive.models import File, Version, file_type
from polydrive.services.messages import not_found, unauthorized, bad_request
from polydrive.services.files import check_file_rights


def extract_parameter(param_name):
    param = request.view_args.get(param_name, None)
    if param is None:
        param = request.form.get(param_name, None)
    if param is None and request.content_type == 'application/json' and request.method in ['POST', 'PUT']:
        param = request.get_json().get(param_name, None)
    return param


def file_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        file_id = extract_parameter('file_id')
        if file_id is None:
            return bad_request('No file id provided.')
        file = File.query.get(file_id)
        if file is None:
            return not_found('This resource does not exist.')
        if not check_file_rights(file, current_user):
            return unauthorized('You cannot access this resource.')
        return f(*args, **kwargs)
    return decorated_function


def file_version_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        file_id = extract_parameter('file_id')
        version_id = extract_parameter('version_id')
        if version_id is None or file_id is None:
            return bad_request('No file version id provided.')
        version = Version.query.filter_by(id=version_id, file_id=file_id).first()
        if version is None:
            return not_found('This resource does not exist.')
        return f(*args, **kwargs)
    return decorated_function


def parent_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        parent_id = extract_parameter('parent_id')
        if parent_id is None:
            return f(*args, **kwargs)
        folder = File.query.get(parent_id)
        if folder is None:
            return not_found('Parent folder does not exist.')
        if folder.type != file_type.folder:
            return bad_request('Parent is not a folder.')
        if not check_file_rights(folder, current_user):
            return unauthorized('You cannot access parent folder.')
        return f(*args, **kwargs)
    return decorated_function
