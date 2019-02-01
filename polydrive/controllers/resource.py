from flask import request, send_file
from flask_login import login_required, current_user

from polydrive import app
from polydrive.models import Resource, resource_type, Version
from polydrive.config import db
from polydrive.services.messages import bad_request, ok, created
from polydrive.services.middleware import resource_middleware, file_version_middleware, \
    parent_middleware, file_middleware


@app.route('/res', methods=['GET'])
@login_required
def root_content():
    """
    Get resources located in user's root.

    Get the list of all user's resources with no parent.

    :return: user's resources in root folder
    """
    resources = Resource.query.filter_by(owner_id=current_user.id, parent_id=None).all()
    return ok('OK', [r.deep for r in resources])


@app.route('/res/<int:res_id>', methods=['GET'])
@login_required
@resource_middleware
def resource_details(res_id=None):
    """
    Get a resource's details.

    Return the specified resource's details. If the resource is a folder, the recursive
    hierarchy is also returned.

    :param res_id: the requested resource's id
    :return: the requested resource's details
    """
    file = Resource.query.get(res_id)
    return ok('OK', file.deep)


@app.route('/res', methods=['POST'])
@login_required
@parent_middleware(False)
def resource_create():
    """
    Create a resource.

    Create a resource with given details. The name and type are required. If no parent id is given,
    the resource is created in user's root folder. The resource cannot be a file

    :return: the created resource's details
    """
    content = request.get_json()
    if content is None:
        content = {}
    messages = []
    name = content.get('name', None)
    if name is None:
        messages.append('Name parameter required.')
    r_type = content.get('type', None)
    if r_type is None:
        messages.append('Type parameter required.')
    else:
        if r_type == resource_type.file:
            messages.append('Cannot create file without content.')
        if r_type not in resource_type:
            messages.append('Not a valid type')
    if len(messages) > 0:
        return bad_request(messages)
    parent_id = content.get('parent_id', None)
    parent = None
    if parent_id is not None:
        parent = Resource.query.get(parent_id)
    folder = Resource.create_folder(name, current_user, parent)
    db.session.commit()
    return created('Folder created', folder.deep)


@app.route('/res/<int:res_id>', methods=['DELETE'])
@login_required
@resource_middleware
def file_delete(res_id):
    """
    Delete a resource.

    If the resource is a file, all versions and files on the disk will be removed.
    If the resource is a folder, all children are also deleted.

    :param res_id: the requested resource's id
    :return: the deleted resource
    """
    resource = Resource.query.get(res_id)
    Resource.delete(resource)
    db.session.commit()
    return ok('File successfully deleted.', resource.deep)


@app.route('/res/<int:res_id>', methods=['PUT'])
@login_required
@resource_middleware
@parent_middleware(False)
def file_update(res_id):
    """
    Update a resource's details.

    :param res_id: the requested resource's id
    :return: the updated resource
    """
    resource = Resource.query.get(res_id)
    content = request.get_json()
    params = {}
    if 'name' in content:
        params['name'] = content['name']
    if 'extension' in content and resource.type == resource_type.file:
        params['extension'] = content['extension']
    if 'parent_id' in content:
        parent = Resource.query.get(content['parent_id'])
        params['parent'] = parent
    Resource.update(resource, **params)
    db.session.commit()
    return ok('Resource updated', resource.deep)


@app.route('/res/upload', methods=['POST'])
@app.route('/res/upload/<int:parent_id>', methods=['POST'])
@login_required
@parent_middleware(False)
def file_upload(parent_id=None):
    """
    Upload a file.

    The file must be a multi-part parameter called "file". If no parent id is given,
    the file is located on user's root.

    :param parent_id: the parent's id, null if root folder
    :return: the created file's details
    """
    if 'file' not in request.files:
        return bad_request('File parameter required.')
    buffer = request.files['file']
    if buffer.filename == '':
        return bad_request('No selected file.')
    parent = None
    if parent_id is not None:
        parent = Resource.query.get(parent_id)
    f_details = buffer.filename.rsplit('.', 1)
    filename = f_details[0]
    extension = None
    if len(f_details) > 1:
        extension = f_details[1]
    file = Resource.create(filename, extension, current_user, parent, buffer)
    db.session.commit()
    return created('File uploaded.', file.deep)


@app.route('/res/<int:res_id>/download', methods=['GET'])
@login_required
@resource_middleware
@file_middleware
def file_download(res_id):
    """
    Get a file content.

    The file's blob is sent into the body.

    :param res_id: the requested file's id
    :return: the requested file's content
    """
    file = Resource.query.get(res_id)
    return send_file(file.last_version.real_path, mimetype=file.mime)


@app.route('/res/<int:res_id>/upload', methods=['PUT'])
@login_required
@resource_middleware
def file_upload_version(res_id):
    """
    Upload a new version for an existing file.

    :param res_id: the file's id
    :return: the file's details
    """
    if 'file' not in request.files:
        return bad_request('File parameter required.')
    file = Resource.query.get(res_id)
    buffer = request.files['file']
    if buffer.filename == '':
        return bad_request('No selected file.')
    Resource.add_version(file, buffer)
    db.session.commit()
    return ok('File version uploaded.', file.deep)


@app.route('/res/<int:res_id>/<int:version_id>', methods=['GET'])
@login_required
@resource_middleware
@file_version_middleware
def file_version_details(res_id, version_id):
    """
    Get the details of a specific version of a file.

    :param res_id: the file's id
    :param version_id: the version's id
    :return: the version's details
    """
    version = Version.query.filter_by(id=version_id, res_id=res_id).first()
    return ok('OK', version.serialized)


@app.route('/res/<int:res_id>/<int:version_id>', methods=['DELETE'])
@login_required
@resource_middleware
@file_version_middleware
def file_version_delete(res_id, version_id):
    """
    Delete a specific version of a file.

    :param res_id: the file's id
    :param version_id: the version's id
    :return: the version's details
    """
    version = Version.query.filter_by(id=version_id, res_id=res_id).first()
    Version.delete(version)
    db.session.commit()
    return ok('File version successfully deleted.', version.serialized)


@app.route('/res/<int:res_id>/<int:version_id>/download', methods=['GET'])
@login_required
@resource_middleware
@file_version_middleware
def file_version_download(res_id, version_id):
    """
    Download the content of a specific version of a file.

    :param res_id: the file's id
    :param version_id: the version's id
    :return:
    """
    version = Version.query.filter_by(id=version_id, res_id=res_id).first()
    return send_file(version.real_path, mimetype=version.file.mime)
