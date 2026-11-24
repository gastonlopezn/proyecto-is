import uuid

from myapp.extensions import db
from myapp.models import Category, Question


def valid_update_data(category_title):
    return {
        "title": "¿Alcanzará Bitcoin los 250.000 dólares antes de fin de 2026?",
        "body": "Nuevo umbral, mismo criterio de resolución.",
        "date": "2026-12-31",
        "source": "https://www.coingecko.com/es/monedas/bitcoin",
        "category": category_title,
        "tags": "bitcoin, mercados",
        "responses": ["Sí", "No", "No se sabe"],
    }


def snapshot(question):
    db.session.expire_all()
    stored = db.session.get(Question, question.id)
    return {
        "title": stored.title,
        "body": stored.body,
        "date": stored.date,
        "source": stored.source,
        "category": stored.category_title,
        "tags": sorted(tag.title for tag in stored.tags),
        "responses": sorted(response.title for response in stored.responses),
    }


def test_valid_update_saves_changes_and_redirects_to_detail(client, question):
    db.session.add(Category(title="Economía"))
    db.session.commit()

    response = client.post(
        f"/questions/{question.id}", data=valid_update_data("Economía")
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(f"/questions/{question.id}")

    stored = snapshot(question)
    assert (
        stored["title"]
        == "¿Alcanzará Bitcoin los 250.000 dólares antes de fin de 2026?"
    )
    assert stored["body"] == "Nuevo umbral, mismo criterio de resolución."
    assert stored["date"].strftime("%Y-%m-%d") == "2026-12-31"
    assert stored["source"] == "https://www.coingecko.com/es/monedas/bitcoin"
    assert stored["category"] == "Economía"
    assert stored["tags"] == ["bitcoin", "mercados"]
    assert stored["responses"] == ["No", "No se sabe", "Sí"]


def test_valid_update_does_not_create_a_new_question(client, question):
    client.post(f"/questions/{question.id}", data=valid_update_data("Cripto"))

    count = db.session.scalar(db.select(db.func.count()).select_from(Question))
    assert count == 1


def test_update_with_missing_title_keeps_stored_data(client, question):
    before = snapshot(question)
    data = valid_update_data("Cripto") | {"title": ""}

    response = client.post(f"/questions/{question.id}", data=data)

    assert response.status_code == 400
    assert "Title is required." in response.get_data(as_text=True)
    assert snapshot(question) == before


def test_update_with_invalid_date_keeps_stored_data(client, question):
    before = snapshot(question)
    data = valid_update_data("Cripto") | {"date": "31/12/2026"}

    response = client.post(f"/questions/{question.id}", data=data)

    assert response.status_code == 400
    assert "Invalid date format." in response.get_data(as_text=True)
    assert snapshot(question) == before


def test_update_with_fewer_than_two_responses_keeps_stored_data(client, question):
    before = snapshot(question)
    data = valid_update_data("Cripto") | {"responses": ["Sí", ""]}

    response = client.post(f"/questions/{question.id}", data=data)

    assert response.status_code == 400
    assert "At least two responses are required." in response.get_data(as_text=True)
    assert snapshot(question) == before


def test_update_with_unknown_category_keeps_stored_data(client, question):
    before = snapshot(question)
    data = valid_update_data("Categoría inexistente")

    response = client.post(f"/questions/{question.id}", data=data)

    assert response.status_code == 400
    assert snapshot(question) == before


def test_invalid_update_shows_form_again_with_entered_values(client, question):
    data = valid_update_data("Cripto") | {"title": ""}

    html = client.post(f"/questions/{question.id}", data=data).get_data(as_text=True)

    assert "Nuevo umbral, mismo criterio de resolución." in html
    assert "No se sabe" in html


def test_update_non_existent_question_returns_404(client, category):
    response = client.post(
        f"/questions/{uuid.uuid4()}", data=valid_update_data(category.title)
    )

    assert response.status_code == 404
    assert db.session.scalars(db.select(Question)).all() == []


def test_update_with_malformed_id_returns_404(client, category):
    response = client.post(
        "/questions/not-a-uuid", data=valid_update_data(category.title)
    )

    assert response.status_code == 404
