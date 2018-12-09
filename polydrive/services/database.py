import yaml
import json
from io import BytesIO

from polydrive import app
from polydrive.config import db
from polydrive.config.files import make_path
from polydrive.models import User


def init_db():
    db.create_all()


def clear_db():
    db.drop_all()


def fill_db(path):
    client = app.test_client()
    with open(make_path(path)) as f:
        y = yaml.load(f)

        parsed_users = []

        users_dict = y.get('users', None)
        for user_dict in users_dict:
            user = User.create(username=user_dict['username'], password=user_dict['password'], email=None)
            db.session.add(user)
            parsed_users.append({'user': user,
                                 'files': user_dict.get('files', None),
                                 'password': user_dict['password']})
        db.session.commit()

        for user_dict in parsed_users:
            user = user_dict['user']
            client.post('/login', data=json.dumps({'username': user.username, 'password': user_dict['password']}),
                        content_type='application/json')
            files_dict = user_dict['files']

            def create_file(f_dict, parent_id=None):
                data = {
                    'file': (BytesIO(b'This is a content'), f_dict['name'])
                }
                if parent_id is not None:
                    data['parent_id'] = parent_id
                client.post('/files', data=data)

            def create_folder(f_dict, parent_id=None):
                data = {
                    'name': f_dict['name']
                }
                if parent_id is not None:
                    data['parent_id'] = parent_id
                rv = client.post('/folders', data=json.dumps(data), content_type='application/json')
                content = json.loads(rv.data)
                f_id = content['content']['id']
                if f_dict.get('children', None) is not None:
                    for child in f_dict['children']:
                        if child['type'] == 'file':
                            create_file(child, f_id)
                        elif child['type'] == 'folder':
                            create_folder(child, f_id)

            if files_dict is not None:
                for file_dict in files_dict:
                    if file_dict['type'] == 'file':
                        create_file(file_dict)
                    elif file_dict['type'] == 'folder':
                        create_folder(file_dict)
