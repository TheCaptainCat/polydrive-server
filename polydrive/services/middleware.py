from functools import wraps
from flask import request
from flask_login import current_user

from polydrive.models import Resource, Version, resource_type, User
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
    def wrapper(*args, **kwargs):
        res_id = extract_parameter('res_id')
        if res_id is None:
            return bad_request('No resource id provided.')
        res_id = Resource.query.get(res_id)
        if res_id is None:
            return not_found('This resource does not exist.')
        if not check_resource_rights(res_id, current_user):
            return unauthorized('You cannot access this resource.')
        return f(*args, **kwargs)

    return wrapper


def file_middleware(f):
    """
    Check if the requested resource is a file.

    This decorator must always be called after @rights_middleware().
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        res_id = extract_parameter('res_id')
        file = Resource.query.get(res_id)
        if file.type != resource_type.file:
            return bad_request('Resource is not a file.')
        return f(*args, **kwargs)

    return wrapper


def file_version_middleware(f):
    """
    Check if the requested file version exists.

    This decorator must always be called after @rights_middleware().
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        res_id = extract_parameter('res_id')
        version_id = extract_parameter('version_id')
        if version_id is None or res_id is None:
            return bad_request('No file version id provided.')
        version = Version.query.filter_by(id=version_id, res_id=res_id).first()
        if version is None:
            return not_found('This resource does not exist.')
        return f(*args, **kwargs)

    return wrapper


def parent_middleware(required):
    """
    Check if the parent is a folder and if the user can access it.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            parent_id = extract_parameter('parent_id')
            if parent_id is None:
                if not required:
                    return f(*args, **kwargs)
                else:
                    return bad_request('No parent id provided.')
            folder = Resource.query.get(parent_id)
            if folder is None:
                return not_found('Parent folder does not exist.')
            if folder.type != resource_type.folder:
                return bad_request('Parent is not a folder.')
            if not check_resource_rights(folder, current_user):
                return unauthorized('You cannot access parent folder.')
            return f(*args, **kwargs)

        return wrapper

    return decorator


def user_middleware(f):
    """
    Check if the user exists.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = extract_parameter('user_id')
        if user_id is None:
            return bad_request('No user id provided.')
        user = User.query.get(user_id)
        if user is None:
            return not_found('User not found.')
        return f(*args, **kwargs)

    return wrapper
