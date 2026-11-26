import uuid

import pytest

from myapp.extensions import db
from myapp.models import Category, Question, Response, StateType, Tag, question_tag
from myapp.services.questions import (
    QuestionValidationError,
    create_question,
    delete_question,
    get_question,
    list_questions,
    update_question,
)


def _valid_payload(category_title: str = "Cripto") -> dict:
    return {
        "title": "¿Superará Bitcoin los 200.000 USD en 2026?",
        "body": "Precio de cierre al 31/12/2026.",
        "date": "2026-12-31",
        "source": "https://coinmarketcap.com",
        "category": category_title,
        "tags": ["bitcoin", "mercados"],
        "responses": ["Sí", "No"],
    }


def test_list_questions_supports_category_and_state_filters(app, question):
    sports = Category(title="Deportes")
    closed_question = Question(
        title="¿Ganó Argentina el último amistoso?",
        body="Resultado oficial.",
        category=sports,
        state=StateType.CLOSED,
        responses=[Response(title="Sí"), Response(title="No")],
    )
    db.session.add_all([sports, closed_question])
    db.session.commit()

    assert len(list_questions()) == 2
    assert list_questions(category="Cripto") == [question]
    assert list_questions(state="OPEN") == [question]
    assert list_questions(state="closed") == [closed_question]
    assert list_questions(category="Deportes", state=StateType.CLOSED) == [
        closed_question
    ]
    assert list_questions(category="Cripto", state="CLOSED") == []

    with pytest.raises(QuestionValidationError) as exc_info:
        list_questions(state="PENDING")
    assert "state" in exc_info.value.field_errors


def test_get_question_handles_valid_missing_and_malformed_ids(app, question):
    assert get_question(question.id) is question
    assert get_question(str(question.id)) is question
    assert get_question(uuid.uuid4()) is None
    assert get_question("not-a-uuid") is None


def test_create_question_persists_question_tags_and_responses(app, category):
    created = create_question(_valid_payload(category.title))

    assert created.id is not None
    assert created.state == StateType.OPEN
    assert created.category_title == "Cripto"
    assert {tag.title for tag in created.tags} == {"bitcoin", "mercados"}
    assert [r.title for r in created.responses] == ["Sí", "No"]


def test_create_question_raises_validation_error_on_invalid_data(app, category):
    with pytest.raises(QuestionValidationError) as exc_info:
        create_question(
            {
                "title": "",
                "body": "   ",
                "date": "31/12/2026",
                "category": "Inexistente",
                "responses": ["Solo una"],
            }
        )

    errors = exc_info.value.field_errors
    assert errors["title"] == "Title is required."
    assert errors["body"] == "Body is required."
    assert errors["date"] == "Invalid date format."
    assert errors["category"] == "Selected category does not exist."
    assert errors["responses"] == "At least two responses are required."
    assert db.session.scalars(db.select(Question)).all() == []


def test_update_question_supports_partial_and_full_updates(app, question):
    updated = update_question(
        question,
        {"title": "Título actualizado parcialmente", "tags": ["cripto", "btc"]},
        partial=True,
    )

    assert updated.title == "Título actualizado parcialmente"
    assert updated.body == question.body
    assert {tag.title for tag in updated.tags} == {"cripto", "btc"}
    assert len(updated.responses) == 2

    with pytest.raises(QuestionValidationError):
        update_question(question, {"responses": ["Solo una"]}, partial=True)

    db.session.expire_all()
    refreshed = db.session.get(Question, question.id)
    assert len(refreshed.responses) == 2


def test_delete_question_removes_question_responses_and_tag_links(app, question):
    question_id = question.id
    delete_question(question)

    assert db.session.get(Question, question_id) is None
    assert db.session.scalars(db.select(Response)).all() == []
    assert db.session.execute(db.select(question_tag)).all() == []
    assert db.session.get(Tag, "bitcoin") is not None
