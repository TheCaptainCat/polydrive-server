from flask import request, send_file
from flask_login import login_required, current_user

from polydrive import app
from polydrive.models import File
from polydrive.services.messages import bad_request, ok, not_found, unauthorized


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
    mime = buffer.content_type
    file = File.create(filename, extension, mime, current_user)
    buffer.save(file.real_path)
    return ok('File uploaded.', file.serialized)


@app.route('/files/<int:file_id>', methods=['GET'])
@login_required
def file_download(file_id):
    file = File.query.get(file_id)
    if file is None:
        return not_found('This resource does not exist')
    if file.user_id != current_user.id:
        return unauthorized('You cannot access this resource.')
    return send_file(file.real_path, mimetype=file.mime, attachment_filename=file.real_name)
