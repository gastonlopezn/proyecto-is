from flask import Blueprint, redirect, render_template, request, url_for

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


@users_bp.get("/register")
def register():
    return render_template("users/register.html")


@users_bp.post("/")
@users_bp.post("/register")
def create():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name:
        return (
            render_template(
                "users/register.html",
                error="Name is required",
                name=name,
                email=email,
            ),
            400,
        )

    if not email:
        return (
            render_template(
                "users/register.html",
                error="Email is required",
                name=name,
                email=email,
            ),
            400,
        )

    if not password:
        return (
            render_template(
                "users/register.html",
                error="Password is required",
                name=name,
                email=email,
            ),
            400,
        )

    if len(password) < 8:
        return (
            render_template(
                "users/register.html",
                error="Password must be at least 8 characters",
                name=name,
                email=email,
            ),
            400,
        )

    existing_user = db.session.scalars(
        db.select(User).filter_by(email=email)
    ).first()
    if existing_user:
        return (
            render_template(
                "users/register.html",
                error=f"User with email '{email}' already exists",
                name=name,
                email=email,
            ),
            409,
        )

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("users.index"))
