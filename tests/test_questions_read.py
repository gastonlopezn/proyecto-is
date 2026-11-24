import uuid

from myapp.extensions import db
from myapp.models import Category, Question, Response, StateType, Tag


def test_read_questions_list_when_empty(client):
    response = client.get("/questions/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<h1>Questions</h1>" in html
    assert "No questions yet." in html


def test_read_questions_list_with_multiple_questions(client, question):
    sports_category = Category(title="Deportes")
    second_question = Question(
        title="¿Ganará Argentina la próxima Copa América?",
        body="Se define según el resultado oficial de CONMEBOL.",
        category=sports_category,
        state=StateType.CLOSED,
        responses=[
            Response(title="Sí", price=0.55),
            Response(title="No", price=0.45),
        ],
    )
    db.session.add_all([sports_category, second_question])
    db.session.commit()

    response = client.get("/questions/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No questions yet." not in html

    for item in (question, second_question):
        assert item.title in html
        assert item.category_title in html
        assert item.date.strftime("%Y-%m-%d") in html
        assert item.state.value in html
        assert f'href="/questions/{item.id}"' in html


def test_read_question_detail_displays_attributes_tags_and_responses(
    client, question
):
    question.tags.append(Tag(title="mercados"))
    db.session.commit()

    response = client.get(f"/questions/{question.id}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f"<h1>{question.title}</h1>" in html
    assert question.body in html
    assert f"Category: {question.category_title}" in html
    assert f"State: {question.state.value}" in html
    assert f"Source: {question.source}" in html
    assert "<li>bitcoin</li>" in html
    assert "<li>mercados</li>" in html
    assert "<li>Sí (0.4)</li>" in html
    assert "<li>No (0.6)</li>" in html


def test_read_question_detail_without_optional_source_or_tags(client, category):
    minimal_question = Question(
        title="¿Superará el oro los 3.500 USD en 2026?",
        body="Precio spot al cierre del año.",
        category=category,
        responses=[
            Response(title="Sí", price=0.5),
            Response(title="No", price=0.5),
        ],
    )
    db.session.add(minimal_question)
    db.session.commit()

    response = client.get(f"/questions/{minimal_question.id}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert minimal_question.title in html
    assert minimal_question.body in html
    assert "Source:" not in html


def test_read_question_detail_returns_404_when_not_found(client):
    missing_uuid = uuid.uuid4()
    missing_response = client.get(f"/questions/{missing_uuid}")
    assert missing_response.status_code == 404
    assert b"404" in missing_response.data

    invalid_id_response = client.get("/questions/not-a-valid-uuid")
    assert invalid_id_response.status_code == 404
    assert b"404" in invalid_id_response.data
