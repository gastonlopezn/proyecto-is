from myapp.extensions import db
from myapp.models.prediction_author import PredictionAuthor
from myapp.models.role_type import RoleType
from werkzeug.security import check_password_hash, generate_password_hash


class User(PredictionAuthor, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    role = db.Column(db.Enum(RoleType), nullable=False, default=RoleType.POLYUSER)

    positions = db.relationship(
        "Position",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"