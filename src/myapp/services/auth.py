from functools import wraps

from flask import abort, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from myapp.extensions import db
from myapp.models import RoleType, User


def hash_password(password: str) -> str:
    """Genera un hash seguro para almacenar la contraseña del usuario."""
    return generate_password_hash(password)


def verify_password(stored_password: str, candidate_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    if not stored_password or not candidate_password:
        return False
    return check_password_hash(stored_password, candidate_password)


def authenticate_user(email: str, password: str) -> User | None:
    """Valida credenciales y devuelve el usuario si son correctas."""
    normalized_email = email.strip().lower()
    if not normalized_email or not password:
        return None

    user = db.session.scalars(
        db.select(User).where(User.email == normalized_email)
    ).first()
    if user is None or not verify_password(user.password, password):
        return None
    return user


def login_user(user: User) -> None:
    """Inicia sesión guardando el id y el rol del usuario en la sesión."""
    session.clear()
    session["user_id"] = user.id
    session["user_role"] = user.role.value
    g.user = user


def logout_user() -> None:
    """Cierra la sesión actual."""
    session.clear()
    g.user = None


def get_current_user() -> User | None:
    """Devuelve el usuario autenticado en la request actual, o None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return db.session.get(User, user_id)


def login_required(view):
    """Restringe una vista a usuarios autenticados."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = getattr(g, "user", None)
        if user is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*allowed_roles: RoleType):
    """Restringe una vista a usuarios autenticados con alguno de los roles indicados."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            user = getattr(g, "user", None)
            if user is None:
                return redirect(url_for("auth.login", next=request.path))
            if user.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


admin_required = role_required(RoleType.ADMIN)
