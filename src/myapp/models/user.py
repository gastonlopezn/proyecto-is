from myapp.extensions import db
from myapp.models import prediction_author
from myapp.models.role_type import RoleType


class User(prediction_author, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    role = db.Column(db.Enum(RoleType), nullable=False, default='user')

    def __repr__(self): 
        return f"<User {self.email}>"

