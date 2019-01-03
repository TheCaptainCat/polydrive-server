from polydrive.config import db


class Role(db.Model):
    """
    The link between a resource and a user.
    """
    __tablename__ = 'roles'

    r_id = db.Column(db.Integer, db.ForeignKey('resources.id'), primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    type = db.Column(db.Text, nullable=False)

    @property
    def serialized(self):
        return {
            'type': self.role
        }

    @property
    def deep(self):
        json = self.serialized
        json['user'] = self.user.serialized
        return json

    @staticmethod
    def link(resource, user, r_type):
        role = Role(resource=resource, user=user, type=r_type)
        db.session.add(role)
        return role


class RoleType:
    @property
    def edit(self):
        return 'edit'

    @property
    def view(self):
        return 'view'


role_type = RoleType()
