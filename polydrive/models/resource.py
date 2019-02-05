from polydrive.config import db
from polydrive.models import Version


class Resource(db.Model):
    """
    The resource model.

    Represents a file or folder.
    """
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    extension = db.Column(db.Text, nullable=True)
    mime = db.Column(db.Text, nullable=True)
    type = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=True)

    versions = db.relationship('Version', lazy='subquery', backref=db.backref('file', lazy=True))
    parent = db.relationship('Resource', remote_side=[id], lazy=True,
                             backref=db.backref('children', lazy='subquery'))
    roles = db.relationship('Role', lazy='subquery', backref=db.backref('resource', lazy=True))

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
        json['owner'] = self.owner.serialized
        if self.type == resource_type.file:
            json['versions'] = [v.serialized for v in self.versions]
        if self.type == resource_type.folder:
            json['children'] = [f.deep for f in self.children]
        json['roles'] = [r.deep for r in self.roles]
        return json

    @staticmethod
    def create(name, extension, owner, parent, buffer):
        mime = buffer.content_type
        file = Resource(name=name, extension=extension, mime=mime, parent=parent, owner=owner,
                        type=resource_type.file)
        file.versions.append(Version.create(file, buffer))
        db.session.add(file)
        return file

    @staticmethod
    def update(res, **kwargs):
        if 'name' in kwargs:
            res.name = kwargs['name']
        if 'extension' in kwargs:
            res.extension = kwargs['extension']
        if 'parent' in kwargs:
            res.parent = kwargs['parent']

    @staticmethod
    def create_folder(name, owner, parent):
        folder = Resource(name=name, owner=owner, parent=parent, type=resource_type.folder)
        db.session.add(folder)
        return folder

    @staticmethod
    def add_version(res, buffer):
        version = Version.create(res, buffer)
        res.versions.append(version)
        return version

    @staticmethod
    def delete(res):
        if res.type == resource_type.file:
            for version in res.versions:
                Version.delete(version)
        if res.type == resource_type.folder:
            for child in res.children:
                Resource.delete(child)
        db.session.delete(res)

    @staticmethod
    def get_rights(res, user):
        for role in res.roles:
            if role.user_id == user.id:
                return role
        if res.parent is not None:
            return Resource.get_rights(res.parent, user)
        return None


class ResourceType:
    @property
    def file(self):
        return 'file'

    @property
    def folder(self):
        return 'folder'

    def __contains__(self, item):
        return item in ['file', 'folder']


resource_type = ResourceType()
