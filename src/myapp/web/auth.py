from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from myapp.services.auth import (
    authenticate_user,
    get_current_user,
    login_user,
    logout_user,
)

auth_bp = Blueprint("auth", __name__)


def _is_safe_next_url(target: str | None) -> bool:
    return bool(target) and target.startswith("/") and not target.startswith("//")


@auth_bp.before_app_request
def load_logged_in_user() -> None:
    g.user = get_current_user()


@auth_bp.get("/login")
def login():
    next_url = request.args.get("next", "")
    return render_template("auth/login.html", email="", error=None, next_url=next_url)


@auth_bp.post("/login")
def login_submit():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    next_url = request.form.get("next", "")

    user = authenticate_user(email, password)
    if user is None:
        return (
            render_template(
                "auth/login.html",
                email=email,
                error="Invalid email or password.",
                next_url=next_url,
            ),
            401,
        )

    login_user(user)
    if _is_safe_next_url(next_url):
        return redirect(next_url)
    return redirect(url_for("users.index"))


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("You have been signed out successfully.", "success")
    return redirect(url_for("auth.login"))
