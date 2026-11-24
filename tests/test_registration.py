from myapp.extensions import db
from myapp.models.user import User


class TestRegistrationPage:
    def test_register_page_loads(self, client):
        response = client.get("/users/register")

        assert response.status_code == 200
        assert b"Register" in response.data


class TestSuccessfulRegistration:
    def test_redirects_to_users_index(self, client):
        response = client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "securepass",
            },
        )

        assert response.status_code == 302
        assert "/users/" in response.headers["Location"]

    def test_creates_user_in_database(self, app, client):
        client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "securepass",
            },
        )

        with app.app_context():
            user = db.session.scalars(
                db.select(User).filter_by(email="alice@example.com")
            ).first()

            assert user is not None
            assert user.name == "Alice"

    def test_password_is_hashed(self, app, client):
        client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "securepass",
            },
        )

        with app.app_context():
            user = db.session.scalars(
                db.select(User).filter_by(email="alice@example.com")
            ).first()

            assert user.password_hash != "securepass"
            assert user.check_password("securepass")


class TestValidationErrors:
    def test_missing_name(self, client):
        response = client.post(
            "/users/",
            data={
                "name": "",
                "email": "alice@example.com",
                "password": "securepass",
            },
        )

        assert response.status_code == 400
        assert b"Name is required" in response.data

    def test_missing_email(self, client):
        response = client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "",
                "password": "securepass",
            },
        )

        assert response.status_code == 400
        assert b"Email is required" in response.data

    def test_missing_password(self, client):
        response = client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "",
            },
        )

        assert response.status_code == 400
        assert b"Password is required" in response.data

    def test_password_too_short(self, client):
        response = client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 400
        assert b"Password must be at least 8 characters" in response.data

    def test_preserves_name_and_email_on_error(self, client):
        response = client.post(
            "/users/",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "",
            },
        )

        assert b"Alice" in response.data
        assert b"alice@example.com" in response.data


class TestDuplicateEmail:
    def test_duplicate_email_returns_error(self, app, client):
        with app.app_context():
            user = User(name="Alice", email="alice@example.com")
            user.set_password("securepass")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/users/",
            data={
                "name": "Alice2",
                "email": "alice@example.com",
                "password": "securepass2",
            },
        )

        assert response.status_code == 409
        assert b"already exists" in response.data
