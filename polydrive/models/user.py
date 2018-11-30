from polydrive.services import db, bcrypt


class User(db.Model):
    """
    The user model.

    Represents a user entity.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)

    @property
    def is_authenticated(self):
        """
        If the user is authenticated, always True.

        :return: True
        """
        return True

    @property
    def is_active(self):
        """
        If the user is active.
        //TODO: determine the conditions when the user is active

        :return: if the user is active
        """
        return True

    @property
    def is_anonymous(self):
        """
        If the user is anonymous, always False.

        :return: False
        """
        return False

    def get_id(self):
        """
        Return the unicode id.

        :return: the user id in unicode format
        """
        return str(self.id)

    @property
    def serialized(self):
        """
        Returns the object in JSON format.

        :return: a key-value dictionary
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

    @staticmethod
    def create(username, password, email):
        user = User(username=username, password=bcrypt.generate_password_hash(password), email=email)
        db.session.add(user)
        db.session.commit()
        return user
