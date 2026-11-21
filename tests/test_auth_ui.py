from myapp.extensions import db
from myapp.models import RoleType, User
from myapp.services.auth import hash_password


def _create_user(email: str, password: str, role: RoleType = RoleType.POLYUSER) -> User:
    user = User(
        name="UX Tester",
        email=email,
        password_hash=hash_password(password),
        balance=0.0,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_login_page_renders_modern_ui_assets_and_accessibility_controls(client):
    response = client.get("/login")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "css/auth.css" in html
    assert "js/auth.js" in html
    assert 'class="auth-card"' in html
    assert 'autocomplete="email"' in html
    assert 'autocomplete="current-password"' in html
    assert "data-toggle-password" in html
    assert 'aria-label="Show password"' in html
    assert 'href="/users/register"' in html


def test_login_error_sets_aria_invalid_and_preserves_email(client):
    response = client.post(
        "/login",
        data={"email": "wrong@example.com", "password": "bad-password"},
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 401
    assert 'role="alert"' in html
    assert "Invalid email or password." in html
    assert 'aria-invalid="true"' in html
    assert 'value="wrong@example.com"' in html


def test_logout_displays_confirmation_banner_on_login_page(client):
    _create_user("ux@example.com", "secret123")
    client.post("/login", data={"email": "ux@example.com", "password": "secret123"})

    response = client.post("/logout", follow_redirects=True)
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "You have been signed out successfully." in html
    assert "auth-alert--success" in html


def test_authenticated_user_sees_signed_in_notice_on_login_page(client):
    _create_user("ux@example.com", "secret123", role=RoleType.ADMIN)
    client.post("/login", data={"email": "ux@example.com", "password": "secret123"})

    response = client.get("/login")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "auth-alert--info" in html
    assert "UX Tester" in html
    assert "ADMIN" in html
