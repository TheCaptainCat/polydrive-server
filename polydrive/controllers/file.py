from flask import request, send_file
from flask_login import login_required, current_user

from polydrive import app
from polydrive.models import File, Version
from polydrive.config import db
from polydrive.services.messages import bad_request, ok, created
from polydrive.services.middleware import rights_middleware, file_version_middleware, \
    parent_middleware, file_middleware


@app.route('/files', methods=['POST'])
@app.route('/files/<int:parent_id>', methods=['POST'])
@login_required
@parent_middleware
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
        parent = File.query.get(parent_id)
    f_details = buffer.filename.rsplit('.', 1)
    filename = f_details[0]
    extension = None
    if len(f_details) > 1:
        extension = f_details[1]
    file = File.create(filename, extension, current_user, parent, buffer)
    db.session.commit()
    return created('File uploaded.', file.deep)


@app.route('/folders', methods=['GET'])
@app.route('/folders/<int:parent_id>', methods=['GET'])
@login_required
@parent_middleware
def files_get_list(parent_id=None):
    """
    Get the recursive content of a folder.

    If no parent id is given, returns the content of user's root folder.

    :param parent_id: the parent's id, null if root folder
    :return: the recursive list of the folder's content
    """
    files = File.query.filter(File.parent_id == parent_id, File.owner_id == current_user.id).all()
    return ok('OK', [f.deep for f in files])


@app.route('/folders', methods=['POST'])
@login_required
@parent_middleware
def folder_create():
    """
    Create a folder.

    Create a folder with given details. The name is required. If no parent id is given,
    the folder is created in user's root folder.

    :return: the created folder's details
    """
    content = request.get_json()
    name = content.get('name', None)
    if name is None:
        return bad_request('Name parameter required.')
    parent_id = content.get('parent_id', None)
    parent = None
    if parent_id is not None:
        parent = File.query.get(parent_id)
    folder = File.create_folder(name, current_user, parent)
    db.session.commit()
    return created('Folder created', folder.deep)


@app.route('/files/<int:file_id>', methods=['GET'])
@login_required
@rights_middleware
def file_details(file_id):
    """
    Get a resource's details.

    Return the specified resource's details. If the resource is a folder, the recursive
    hierarchy is also returned.

    :param file_id: the requested resource's id
    :return: the requested resource's details
    """
    file = File.query.get(file_id)
    return ok('OK', file.deep)


@app.route('/files/<int:file_id>/file', methods=['GET'])
@login_required
@rights_middleware
@file_middleware
def file_download(file_id):
    """
    Get a file content.

    The file's blob is sent into the body.

    :param file_id: the requested file's id
    :return: the requested file's content
    """
    file = File.query.get(file_id)
    return send_file(file.last_version.real_path, mimetype=file.mime)


@app.route('/files/<int:file_id>', methods=['DELETE'])
@login_required
@rights_middleware
def file_delete(file_id):
    """
    Delete a resource.

    If the resource is a file, all versions and files on the disk will be removed.
    If the resource is a folder, all children are also deleted.

    :param file_id: the requested resource's id
    :return:
    """
    file = File.query.get(file_id)
    File.delete(file)
    db.session.commit()
    return ok('File successfully deleted.', file.deep)


@app.route('/files/<int:file_id>', methods=['PUT'])
@login_required
@rights_middleware
def file_update(file_id):
    if 'file' not in request.files:
        return bad_request('File parameter required.')
    file = File.query.get(file_id)
    buffer = request.files['file']
    if buffer.filename == '':
        return bad_request('No selected file.')
    File.add_version(file, buffer)
    db.session.commit()
    return ok('File version uploaded.', file.deep)


@app.route('/files/<int:file_id>/versions/<int:version_id>', methods=['GET'])
@login_required
@rights_middleware
@file_version_middleware
def file_version_details(file_id, version_id):
    version = Version.query.filter_by(id=version_id, file_id=file_id).first()
    return ok('OK', version.serialized)


@app.route('/files/<int:file_id>/versions/<int:version_id>/file', methods=['GET'])
@login_required
@rights_middleware
@file_version_middleware
def file_version_download(file_id, version_id):
    version = Version.query.filter_by(id=version_id, file_id=file_id).first()
    return send_file(version.real_path, mimetype=version.file.mime)
