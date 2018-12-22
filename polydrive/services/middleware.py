from functools import wraps
from flask import request
from flask_login import current_user

from polydrive.models import Resource, Version, resource_type
from polydrive.services.messages import not_found, unauthorized, bad_request
from polydrive.services.files import check_resource_rights


def extract_parameter(param_name):
    """
    Look for a parameter in the request.

    A parameter can be in the URI, the JSON content or the form data. The method checks
    several places to find the parameter.

    :param param_name: the name of the parameter
    :return: the parameter's value, None if not found
    """
    param = request.view_args.get(param_name, None)
    if param is None and request.content_type == 'application/json' \
            and request.method in ['POST', 'PUT']:
        param = request.get_json().get(param_name, None)
    if param is None:
        param = request.form.get(param_name, None)
    return param


def resource_middleware(f):
    """
    Check if the user can access the requested resource.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r_id = extract_parameter('r_id')
        if r_id is None:
            return bad_request('No resource id provided.')
        r_id = Resource.query.get(r_id)
        if r_id is None:
            return not_found('This resource does not exist.')
        if not check_resource_rights(r_id, current_user):
            return unauthorized('You cannot access this resource.')
        return f(*args, **kwargs)

    return decorated_function


def file_middleware(f):
    """
    Check if the requested resource is a file.

    This decorator must always be called after @rights_middleware().
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r_id = extract_parameter('r_id')
        file = Resource.query.get(r_id)
        if file.type != resource_type.file:
            return bad_request('Resource is not a file.')
        return f(*args, **kwargs)

    return decorated_function


def file_version_middleware(f):
    """
    Check if the requested file version exists.

    This decorator must always be called after @rights_middleware().
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r_id = extract_parameter('r_id')
        version_id = extract_parameter('version_id')
        if version_id is None or r_id is None:
            return bad_request('No file version id provided.')
        version = Version.query.filter_by(id=version_id, r_id=r_id).first()
        if version is None:
            return not_found('This resource does not exist.')
        return f(*args, **kwargs)

    return decorated_function


def parent_middleware(f):
    """
    Check if the parent is a folder and if the user can access it.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        parent_id = extract_parameter('parent_id')
        if parent_id is None:
            return f(*args, **kwargs)
        folder = Resource.query.get(parent_id)
        if folder is None:
            return not_found('Parent folder does not exist.')
        if folder.type != resource_type.folder:
            return bad_request('Parent is not a folder.')
        if not check_resource_rights(folder, current_user):
            return unauthorized('You cannot access parent folder.')
        return f(*args, **kwargs)

    return decorated_function
