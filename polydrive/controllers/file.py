from flask import request
from flask_login import login_required

from polydrive import app
from polydrive.services.messages import bad_request


@app.route('/files', methods=['POST'])
@login_required
def file_upload():
    messages = []
    if 'file' not in request.files:
        messages.append('Username already in use.')
    if len(messages) > 0:
        return bad_request(messages)
    file = request.files['file']
