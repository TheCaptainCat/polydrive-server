from polydrive.services import db


class File(db.Model):
    """
    The file model.

    Represents a file or folder entity.
    """
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    extension = db.Column(db.String(10), unique=True, nullable=True)
    mime = db.Column(db.String(255), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
