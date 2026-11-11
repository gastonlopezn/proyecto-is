from flask import Blueprint, render_template

from myapp.extensions import db
from myapp.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("/")
def index():
    users = db.session.scalars(db.select(User)).all()
    return render_template(
        "users/index.html",
        users=users,
    )

