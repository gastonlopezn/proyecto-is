import pytest

from myapp.extensions import db
from myapp.models import Category, Position, Question, Response, RoleType, User


def make_user(email: str = "trader@example.com", name: str = "Trader") -> User:
    user = User(
        name=name,
        email=email,
        password="hashed-password",
        balance=1000.0,
        role=RoleType.POLYUSER,
    )
    db.session.add(user)
    db.session.commit()
    return user


def make_responses() -> tuple[Response, Response]:
    category = Category(title="Cripto")
    yes_response = Response(title="Sí", price=0.4)
    no_response = Response(title="No", price=0.6)
    question = Question(
        title="¿Alcanzará Bitcoin los 200.000 dólares en 2026?",
        body="Precio de cierre del 31/12/2026.",
        category=category,
        responses=[yes_response, no_response],
    )
    db.session.add(question)
    db.session.commit()
    return yes_response, no_response


def test_position_persists_attributes_and_links_user_and_response(app):
    user = make_user()
    yes_response, _ = make_responses()

    position = Position(
        user=user,
        response=yes_response,
        quantity=10.5,
        purchase_price=0.42,
    )
    db.session.add(position)
    db.session.commit()

    saved = db.session.get(Position, position.id)
    assert saved is not None
    assert saved.quantity == 10.5
    assert saved.purchase_price == 0.42
    assert saved.user is user
    assert saved.response is yes_response
    assert user.positions == [saved]
    assert yes_response.positions == [saved]
    assert "quantity=10.5" in repr(saved)


def test_position_supports_zero_to_many_on_both_ends(app):
    alice = make_user("alice@example.com", "Alice")
    bob = make_user("bob@example.com", "Bob")
    yes_response, no_response = make_responses()

    assert alice.positions == []
    assert yes_response.positions == []

    p1 = Position(user=alice, response=yes_response, quantity=5.0, purchase_price=0.4)
    p2 = Position(user=alice, response=no_response, quantity=3.0, purchase_price=0.6)
    p3 = Position(user=bob, response=yes_response, quantity=8.0, purchase_price=0.45)

    db.session.add_all([p1, p2, p3])
    db.session.commit()

    assert len(alice.positions) == 2
    assert len(bob.positions) == 1
    assert len(yes_response.positions) == 2
    assert len(no_response.positions) == 1


def test_position_allows_zero_quantity(app):
    user = make_user()
    yes_response, _ = make_responses()

    position = Position(
        user=user,
        response=yes_response,
        quantity=0.0,
        purchase_price=0.5,
    )
    db.session.add(position)
    db.session.commit()

    assert position.quantity == 0.0


def test_position_rejects_negative_quantity_on_create_and_update(app):
    user = make_user()
    yes_response, _ = make_responses()

    with pytest.raises(ValueError, match="negative"):
        Position(
            user=user,
            response=yes_response,
            quantity=-1.0,
            purchase_price=0.4,
        )

    position = Position(
        user=user,
        response=yes_response,
        quantity=5.0,
        purchase_price=0.4,
    )
    db.session.add(position)
    db.session.commit()

    with pytest.raises(ValueError, match="negative"):
        position.quantity = -0.01


def test_deleting_user_or_response_cascades_positions(app):
    user = make_user()
    yes_response, no_response = make_responses()

    p1 = Position(user=user, response=yes_response, quantity=4.0, purchase_price=0.4)
    p2 = Position(user=user, response=no_response, quantity=2.0, purchase_price=0.6)
    db.session.add_all([p1, p2])
    db.session.commit()

    db.session.delete(yes_response)
    db.session.commit()
    assert db.session.get(Position, p1.id) is None
    assert db.session.get(Position, p2.id) is not None

    db.session.delete(user)
    db.session.commit()
    assert db.session.scalars(db.select(Position)).all() == []
    assert db.session.get(Response, no_response.id) is not None
