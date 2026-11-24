import pytest

from myapp import create_app
from myapp.config import TestingConfig
from myapp.extensions import db
from myapp.models import Category, Question, Response, Tag


@pytest.fixture
def app():
    # La configuración de test se pasa a create_app() para que Flask-SQLAlchemy
    # cree el engine contra SQLite en memoria. Si se cambia la URI después de
    # create_app(), el engine ya quedó apuntando a la base de desarrollo.
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def category(app):
    category = Category(title="Cripto")
    db.session.add(category)
    db.session.commit()
    return category


@pytest.fixture
def question(category):
    question = Question(
        title="¿Alcanzará Bitcoin los 200.000 dólares antes de fin de 2026?",
        body="Se resuelve con el precio de cierre en CoinMarketCap al 31/12/2026.",
        source="https://coinmarketcap.com/currencies/bitcoin/",
        category=category,
        tags=[Tag(title="bitcoin")],
        responses=[
            Response(title="Sí", price=0.4),
            Response(title="No", price=0.6),
        ],
    )
    db.session.add(question)
    db.session.commit()
    return question
