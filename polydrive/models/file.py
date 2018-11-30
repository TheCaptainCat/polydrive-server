import os
import random
import string

from polydrive import app
from polydrive.services import db


class File(db.Model):
    """
    The file model.

    Represents a file or folder entity.
    """
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    extension = db.Column(db.String(10), nullable=True)
    mime = db.Column(db.String(255), nullable=False)
    random_string = db.Column(db.String(100), nullable=False, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def real_path(self):
        return os.path.join(app.config['UPLOAD_FOLDER'], self.random_string)

    @property
    def real_name(self):
        return f'{self.name}.{self.extension}'

    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'extension': self.extension,
            'mime': self.mime
        }

    @staticmethod
    def create(name, extension, mime, owner):
        random_string = None
        while random_string is None or File.query.filter_by(random_string=random_string).first() is not None:
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))
        file = File(name=name, extension=extension, mime=mime, owner=owner, random_string=random_string)
        db.session.add(file)
        db.session.commit()
        return file
