from flask import request, send_file
from flask_login import login_required, current_user

from polydrive import app
from polydrive.models import File
from polydrive.services.messages import bad_request, ok, not_found, unauthorized
from services.middleware import file_middleware


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
    return ok('File uploaded.', file.serialized)


@app.route('/files/<int:file_id>', methods=['GET'])
@login_required
@file_middleware
def file_download(file_id):
    file = File.query.get(file_id)
    return send_file(file.real_path, mimetype=file.mime)


@app.route('/files/<int:file_id>', methods=['DELETE'])
@login_required
@file_middleware
def file_delete(file_id):
    file = File.query.get(file_id)
    File.delete(file)
    return ok('File successfully deleted.', file.serialized)


@app.route('/files/<int:file_id>', methods=['PUT'])
@login_required
@file_middleware
def file_update(file_id):
    file = File.query.get(file_id)
