import uuid
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from myapp.extensions import db
from myapp.models import Category, Question, Response, StateType


def test_question_initial_state_is_open_before_commit():
    question = Question(
        title="¿Lloverá mañana en Río Cuarto?",
        body="Se verifica con el SMN.",
    )

    assert question.state == StateType.OPEN
    assert "State: OPEN" in repr(question)


def test_question_persists_attributes_and_defaults(app):
    category = Category(title="Economía")
    question = Question(
        title="¿Bajará la inflación en 2026?",
        body="Basado en el índice oficial publicado a fin de año.",
        source="https://www.indec.gob.ar",
        category=category,
    )

    db.session.add(question)
    db.session.commit()

    saved = db.session.get(Question, question.id)
    assert saved is not None
    assert isinstance(saved.id, uuid.UUID)
    assert saved.title == "¿Bajará la inflación en 2026?"
    assert saved.body == "Basado en el índice oficial publicado a fin de año."
    assert saved.source == "https://www.indec.gob.ar"
    assert isinstance(saved.date, datetime)
    assert saved.state == StateType.OPEN


def test_question_source_is_optional_and_state_can_close(app):
    category = Category(title="Deportes")
    question = Question(
        title="¿Argentina gana el próximo partido?",
        body="Resultado en los 90 minutos reglamentarios.",
        category=category,
    )
    db.session.add(question)
    db.session.commit()

    assert question.source is None

    question.state = StateType.CLOSED
    db.session.commit()

    refreshed = db.session.get(Question, question.id)
    assert refreshed.state == StateType.CLOSED
    assert "State: CLOSED" in repr(refreshed)


def test_question_has_enough_responses_boundary(app):
    category = Category(title="Tecnología")
    question = Question(
        title="¿Saldrá Python 3.15 en 2026?",
        body="Versión final publicada en python.org.",
        category=category,
    )
    assert not question.has_enough_responses()

    question.responses.append(Response(title="Sí", price=0.7))
    assert not question.has_enough_responses()

    question.responses.append(Response(title="No", price=0.3))
    assert question.has_enough_responses()


def test_question_requires_category(app):
    question = Question(
        title="Pregunta sin categoría",
        body="No debería poder persistirse sin categoría.",
    )
    db.session.add(question)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()
