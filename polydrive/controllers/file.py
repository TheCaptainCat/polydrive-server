from flask import request, send_file
from flask_login import login_required, current_user

from polydrive import app
from polydrive.models import File, Version
from polydrive.services import db
from polydrive.services.messages import bad_request, ok
from services.middleware import file_middleware, file_version_middleware


@app.route('/files', methods=['POST'])
@login_required
def file_upload():
    if 'file' not in request.files:
        return bad_request('File parameter required.')
    buffer = request.files['file']
    if buffer.filename == '':
        return bad_request('No selected file.')
    f_details = buffer.filename.rsplit('.', 1)
    filename = f_details[0]
    extension = None
    if len(f_details) > 1:
        extension = f_details[1]
    file = File.create(filename, extension, current_user, buffer)
    db.session.commit()
    return ok('File uploaded.', file.deep)


@app.route('/files/<int:file_id>', methods=['GET'])
@login_required
@file_middleware
def file_details(file_id):
    file = File.query.get(file_id)
    return ok('OK', file.deep)


@app.route('/files/<int:file_id>/file', methods=['GET'])
@login_required
@file_middleware
def file_download(file_id):
    file = File.query.get(file_id)
    return send_file(file.last_version.real_path, mimetype=file.mime)


@app.route('/files/<int:file_id>', methods=['DELETE'])
@login_required
@file_middleware
def file_delete(file_id):
    file = File.query.get(file_id)
    File.delete(file)
    db.session.commit()
    return ok('File successfully deleted.', file.deep)


@app.route('/files/<int:file_id>', methods=['PUT'])
@login_required
@file_middleware
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
@file_middleware
@file_version_middleware
def file_version_details(file_id, version_id):
    version = Version.query.filter_by(id=version_id, file_id=file_id).first()
    return ok('OK', version.serialized)


@app.route('/files/<int:file_id>/versions/<int:version_id>/file', methods=['GET'])
@login_required
@file_middleware
@file_version_middleware
def file_version_download(file_id, version_id):
    version = Version.query.filter_by(id=version_id, file_id=file_id).first()
    return send_file(version.real_path, mimetype=version.file.mime)
