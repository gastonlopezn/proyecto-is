import uuid
from datetime import datetime, UTC
import pytest

from myapp.extensions import db
from myapp.models import Category, Question, Response, StateType, Tag
from myapp.services.serialization import serialize_question, serialize_response


def test_serialize_response():
    resp_id = uuid.uuid4()
    response = Response(
        id=resp_id,
        title="Sí",
        price=0.65,
        probability=0.7,
        is_winner=True,
    )

    data = serialize_response(response)

    assert data == {
        "id": str(resp_id),
        "title": "Sí",
        "price": 0.65,
        "probability": 0.7,
        "is_winner": True,
    }
    assert isinstance(data["id"], str)
    assert isinstance(data["title"], str)
    assert isinstance(data["price"], float)
    assert isinstance(data["probability"], float)
    assert isinstance(data["is_winner"], bool)


def test_serialize_question(app):
    category = Category(title="Economía")
    db.session.add(category)

    q_id = uuid.uuid4()
    dt = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)
    question = Question(
        id=q_id,
        title="¿Inflación menor al 2%?",
        body="Según datos oficiales.",
        date=dt,
        source="https://example.com",
        state=StateType.OPEN,
        category=category,
    )

    tag1 = Tag(title="inflación")
    tag2 = Tag(title="gobierno")
    question.tags.extend([tag1, tag2])

    resp1 = Response(title="Sí", price=0.4, probability=0.5, is_winner=False)
    resp2 = Response(title="No", price=0.6, probability=0.5, is_winner=True)
    question.responses.extend([resp1, resp2])

    db.session.add(question)
    db.session.commit()

    data = serialize_question(question)

    assert data["id"] == str(q_id)
    assert isinstance(data["id"], str)
    assert data["title"] == "¿Inflación menor al 2%?"
    assert data["body"] == "Según datos oficiales."
    assert data["date"] == dt.isoformat()
    assert data["source"] == "https://example.com"
    assert data["state"] == "OPEN"
    assert data["category"] == "Economía"
    assert sorted(data["tags"]) == ["gobierno", "inflación"]
    assert isinstance(data["tags"], list)
    assert all(isinstance(t, str) for t in data["tags"])

    assert isinstance(data["responses"], list)
    assert len(data["responses"]) == 2

    serialized_resp1 = data["responses"][0]
    assert serialized_resp1["id"] == str(resp1.id)
    assert serialized_resp1["title"] == "Sí"
    assert serialized_resp1["price"] == 0.4
    assert serialized_resp1["probability"] == 0.5
    assert serialized_resp1["is_winner"] is False


def test_serialize_question_without_source_or_tags(app):
    category = Category(title="Tecnología")
    db.session.add(category)

    question = Question(
        title="¿Lanzamiento de IA?",
        body="Próximo evento.",
        category=category,
    )
    question.responses.extend([
        Response(title="Sí", price=0.8),
        Response(title="No", price=0.2),
    ])

    db.session.add(question)
    db.session.commit()

    data = serialize_question(question)

    assert data["source"] is None
    assert data["tags"] == []
    assert data["state"] == "OPEN"
    assert len(data["responses"]) == 2
