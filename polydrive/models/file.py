from polydrive.config import db
from polydrive.models import Version


users_files = db.Table('users_files',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                       db.Column('file_id', db.Integer, db.ForeignKey('files.id'), primary_key=True),
                       db.Column('role', db.Text, nullable=False))


class File(db.Model):
    """
    The file model.

    Represents a file or folder entity.
    """
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    extension = db.Column(db.Text, nullable=True)
    mime = db.Column(db.Text, nullable=True)
    type = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('files.id'))

    versions = db.relationship('Version', lazy='subquery', backref=db.backref('file', lazy=True))
    parent = db.relationship('File', remote_side=[id], lazy=True, backref=db.backref('children', lazy='subquery'))
    viewers = db.relationship('User', secondary=users_files, lazy='subquery', backref=db.backref('viewing', lazy=True))

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
            'mime': self.mime,
            'type': self.type
        }

    @property
    def deep(self):
        json = self.serialized
        if self.type == file_type.file:
            json['version'] = [v.serialized for v in self.versions]
        if self.type == file_type.folder:
            json['children'] = [f.deep for f in self.children]
        json['viewers'] = [u.serialize for u in self.viewers]
        return json

    @staticmethod
    def create(name, extension, owner, parent, buffer):
        mime = buffer.content_type
        file = File(name=name, extension=extension, mime=mime, parent=parent, owner=owner, type=file_type.file)
        file.versions.append(Version.create(file, buffer))
        db.session.add(file)
        return file

    @staticmethod
    def create_folder(name, owner, parent):
        folder = File(name=name, owner=owner, parent=parent, type=file_type.folder)
        db.session.add(folder)
        return folder

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


class FileType:
    @property
    def file(self):
        return 'file'

    @property
    def folder(self):
        return 'folder'


file_type = FileType()


class Role:
    @property
    def edit(self):
        return 'edit'

    @property
    def view(self):
        return 'view'


role = Role()
