from polydrive.config import db
from polydrive.models import Resource


class Role(db.Model):
    """
    The link between a resource and a user.
    """
    __tablename__ = 'roles'

    res_id = db.Column(db.Integer, db.ForeignKey('resources.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    type = db.Column(db.Text, nullable=False)

    @property
    def serialized(self):
        return {
            'type': self.type
        }

    @property
    def deep(self):
        json = self.serialized
        json['user'] = self.user.serialized
        return json

    @staticmethod
    def delete(role):
        db.session.delete(role)

    @staticmethod
    def link(res, user, r_type):
        existing = Role.query.filter_by(res_id=res.id, user_id=user.id).first()
        if existing is not None:
            existing.type = r_type
            for r in res.children:
                Role.unlink_deep(r, user, r_type)
            return existing
        existing = Resource.get_rights(res, user)
        if existing is None or (existing.type == role_type.view and r_type == role_type.edit):
            role = Role(resource=res, user=user, type=r_type)
            db.session.add(role)
            for r in res.children:
                Role.unlink_deep(r, user, r_type)
            return role
        return None

    @staticmethod
    def unlink(res, user):
        role = Role.query.filter_by(res_id=res.id, user_id=user.id).first()
        if role is not None:
            Role.delete(role)

    @staticmethod
    def unlink_deep(res, user, r_type):
        role = Role.query.filter_by(res_id=res.id, user_id=user.id).first()
        if role is not None and (r_type == role_type.edit or r_type == role_type.view == role.type):
            Role.delete(role)
        for r in res.children:
            Role.unlink_deep(r, user, r_type)


class RoleType:
    def values(self):
        return [self.view, self.edit]

    @property
    def edit(self):
        return 'edit'

    @property
    def view(self):
        return 'view'


role_type = RoleType()
