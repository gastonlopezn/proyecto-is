from flask import g

from myapp.extensions import db
from myapp.models import RoleType, User
from myapp.services.auth import (
    admin_required,
    hash_password,
    login_required,
    role_required,
)


def create_user(
    email: str,
    password: str,
    role: RoleType,
    name: str = "Test User",
) -> User:
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        balance=0.0,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def register_protected_routes(app) -> None:
    @app.get("/_test/protected")
    @login_required
    def protected_route():
        return {"user": g.user.email, "role": g.user.role.value}

    @app.get("/_test/admin-only")
    @admin_required
    def admin_only_route():
        return {"area": "admin"}

    @app.get("/_test/polyuser-only")
    @role_required(RoleType.POLYUSER)
    def polyuser_only_route():
        return {"area": "polyuser"}

    @app.get("/_test/any-role")
    @role_required(RoleType.ADMIN, RoleType.POLYUSER)
    def any_role_route():
        return {"role": g.user.role.value}


def test_login_page_renders(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert b"Login" in response.data
    assert b'name="email"' in response.data
    assert b'name="password"' in response.data


def test_login_valid_admin_and_polyuser_sets_role_in_session(client):
    create_user("admin@example.com", "admin-pass", RoleType.ADMIN, "Ada Admin")
    create_user("poly@example.com", "poly-pass", RoleType.POLYUSER, "Pablo User")

    admin_res = client.post(
        "/login",
        data={"email": "ADMIN@example.com", "password": "admin-pass"},
    )
    assert admin_res.status_code == 302
    with client.session_transaction() as sess:
        assert sess["user_role"] == RoleType.ADMIN.value

    users_page = client.get("/users/")
    assert b"Ada Admin (ADMIN)" in users_page.data

    poly_res = client.post(
        "/login",
        data={"email": "poly@example.com", "password": "poly-pass"},
    )
    assert poly_res.status_code == 302
    with client.session_transaction() as sess:
        assert sess["user_role"] == RoleType.POLYUSER.value


def test_login_invalid_credentials_returns_401_and_clear_error(client):
    create_user("user@example.com", "correct-pass", RoleType.POLYUSER)

    wrong_password = client.post(
        "/login",
        data={"email": "user@example.com", "password": "wrong-pass"},
    )
    assert wrong_password.status_code == 401
    assert b"Invalid email or password." in wrong_password.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess

    unknown_email = client.post(
        "/login",
        data={"email": "ghost@example.com", "password": "correct-pass"},
    )
    assert unknown_email.status_code == 401
    assert b"Invalid email or password." in unknown_email.data

    empty_fields = client.post("/login", data={"email": "", "password": ""})
    assert empty_fields.status_code == 401
    assert b"Invalid email or password." in empty_fields.data


def test_logout_clears_session(client):
    create_user("user@example.com", "secret", RoleType.POLYUSER)
    client.post("/login", data={"email": "user@example.com", "password": "secret"})

    response = client.post("/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user_role" not in sess


def test_rbac_distinguishes_admin_and_polyuser(app, client):
    register_protected_routes(app)
    create_user("admin@example.com", "admin-pass", RoleType.ADMIN)
    create_user("poly@example.com", "poly-pass", RoleType.POLYUSER)

    # Unauthenticated user is redirected to /login.
    anon_protected = client.get("/_test/protected")
    assert anon_protected.status_code == 302
    assert "/login" in anon_protected.headers["Location"]

    anon_admin = client.get("/_test/admin-only")
    assert anon_admin.status_code == 302
    assert "/login" in anon_admin.headers["Location"]

    # PolyUser can access general and PolyUser routes, but gets 403 on Admin routes.
    client.post("/login", data={"email": "poly@example.com", "password": "poly-pass"})
    assert client.get("/_test/protected").status_code == 200
    assert client.get("/_test/polyuser-only").status_code == 200
    assert client.get("/_test/any-role").status_code == 200
    assert client.get("/_test/admin-only").status_code == 403

    # Admin can access general and Admin routes, but gets 403 on PolyUser-only routes.
    client.post("/login", data={"email": "admin@example.com", "password": "admin-pass"})
    assert client.get("/_test/protected").status_code == 200
    assert client.get("/_test/admin-only").status_code == 200
    assert client.get("/_test/any-role").status_code == 200
    assert client.get("/_test/polyuser-only").status_code == 403


def test_login_respects_safe_next_url_and_ignores_external_url(app, client):
    register_protected_routes(app)
    create_user("admin@example.com", "admin-pass", RoleType.ADMIN)

    safe_res = client.post(
        "/login",
        data={
            "email": "admin@example.com",
            "password": "admin-pass",
            "next": "/_test/admin-only",
        },
    )
    assert safe_res.status_code == 302
    assert safe_res.headers["Location"].endswith("/_test/admin-only")

    unsafe_res = client.post(
        "/login",
        data={
            "email": "admin@example.com",
            "password": "admin-pass",
            "next": "//evil.example.com/phish",
        },
    )
    assert unsafe_res.status_code == 302
    assert unsafe_res.headers["Location"].endswith("/users/")
