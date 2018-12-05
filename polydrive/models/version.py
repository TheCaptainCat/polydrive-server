import os
import random
import string
import datetime

from polydrive import app
from polydrive.services import db


class Version(db.Model):
    """
    The version of a file.

    Represents a file version on the physical disk.
    """
    __tablename__ = 'versions'

    id = db.Column(db.Integer, primary_key=True)
    random_string = db.Column(db.String(100), nullable=False, unique=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    created = db.Column(db.DateTime, nullable=False)

    @property
    def real_path(self):
        return os.path.join(app.config['UPLOAD_FOLDER'], self.random_string)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'created': self.created
        }

    @staticmethod
    def create(file, buffer):
        random_string = None
        while random_string is None or Version.query.filter_by(random_string=random_string).first() is not None:
            random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=100))
        version = Version(random_string=random_string, file=file,
                          created=datetime.datetime.now(tz=datetime.timezone.utc))
        buffer.save(version.real_path)
        db.session.add(version)
        return version

    @staticmethod
    def delete(version):
        os.remove(version.real_path)
        db.session.delete(version)
