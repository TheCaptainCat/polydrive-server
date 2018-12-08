import os

from polydrive import app

import env


def make_path(path):
    return os.path.normpath(os.path.join(app.instance_path, path))


app.config['UPLOAD_FOLDER'] = make_path(env.upload_folder)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
