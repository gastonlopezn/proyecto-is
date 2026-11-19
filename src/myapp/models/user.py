from myapp.extensions import db
from myapp.models import prediction_author
from myapp.models.role_type import RoleType
from werkzeug.security import check_password_hash, generate_password_hash


class User(prediction_author, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    role = db.Column(db.Enum(RoleType), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

