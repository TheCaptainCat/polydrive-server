from polydrive.services import db
from polydrive.models import Version


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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    versions = db.relationship('Version', lazy='subquery', backref=db.backref('file', lazy=True))
    children = db.relationship('File', lazy='subquery', backref=db.backref('parent', lazy=True))

    @property
    def real_name(self):
        return f'{self.name}.{self.extension}'

    @property
    def last_version(self):
        return max(self.versions, key=lambda version: version.created)

    @property
    def serialized(self):
        return {
            'id': self.id,
            'name': self.name,
            'extension': self.extension,
            'mime': self.mime
        }

    @property
    def deep(self):
        json = self.serialized
        json['version'] = [v.serialized for v in self.versions]
        json['children'] = [f.deep for f in self.children]
        return json

    @staticmethod
    def create(name, extension, owner, buffer):
        mime = buffer.content_type
        file = File(name=name, extension=extension, mime=mime, owner=owner)
        file.versions.append(Version.create(file, buffer))
        db.session.add(file)
        return file

    @staticmethod
    def add_version(file, buffer):
        version = Version.create(file, buffer)
        file.versions.append(version)
        return version

    @staticmethod
    def delete(file):
        for version in file.versions:
            Version.delete(version)
        db.session.delete(file)
