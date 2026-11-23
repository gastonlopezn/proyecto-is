from myapp.extensions import db
from myapp.models import Question


def test_base_template_renders_flash_messages(client):
    with client.session_transaction() as sess:
        sess["_flashes"] = [("success", "Custom flash notification")]

    response = client.get("/questions/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'class="flashes"' in html
    assert "Custom flash notification" in html


def test_flash_messages_shown_after_create_update_and_delete(client, category):
    # 1. Create a question
    create_res = client.post(
        "/questions",
        data={
            "title": "¿Ganará Argentina el Mundial 2026?",
            "body": "Resultado final de la Copa del Mundo FIFA 2026.",
            "date": "2026-07-19",
            "source": "https://www.fifa.com",
            "category": category.title,
            "tags": "futbol, mundial",
            "responses": ["Sí", "No"],
        },
        follow_redirects=True,
    )
    create_html = create_res.get_data(as_text=True)
    assert create_res.status_code == 200
    assert "Question created successfully." in create_html

    created = db.session.scalars(db.select(Question)).first()
    assert created is not None

    # 2. Update the question
    update_res = client.post(
        f"/questions/{created.id}",
        data={
            "title": "¿Llegará Argentina a la final del Mundial 2026?",
            "body": "Actualizado con nuevo criterio.",
            "date": "2026-07-19",
            "source": "https://www.fifa.com",
            "category": category.title,
            "tags": "futbol",
            "responses": ["Sí", "No"],
        },
        follow_redirects=True,
    )
    update_html = update_res.get_data(as_text=True)
    assert update_res.status_code == 200
    assert "Question updated successfully." in update_html
    assert "¿Llegará Argentina a la final del Mundial 2026?" in update_html

    # 3. Delete the question
    delete_res = client.post(
        f"/questions/{created.id}/delete",
        follow_redirects=True,
    )
    delete_html = delete_res.get_data(as_text=True)
    assert delete_res.status_code == 200
    assert "Question deleted successfully." in delete_html
    assert db.session.get(Question, created.id) is None


def test_validation_errors_shown_on_invalid_create_and_nothing_saved(client, category):
    response = client.post(
        "/questions",
        data={
            "title": "",
            "body": "",
            "date": "not-a-date",
            "source": "https://example.com",
            "category": "",
            "tags": "cripto",
            "responses": ["Solo una"],
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 400
    assert 'class="errors"' in html
    assert 'class="field-error"' in html
    assert "Title is required." in html
    assert "Body is required." in html
    assert "Invalid date format." in html
    assert "Category is required." in html
    assert "At least two responses are required." in html
    assert 'value="https://example.com"' in html
    assert 'value="Solo una"' in html
    assert db.session.scalars(db.select(Question)).all() == []


def test_validation_errors_shown_on_invalid_update_and_data_unchanged(
    client, question
):
    original_title = question.title

    response = client.post(
        f"/questions/{question.id}",
        data={
            "title": "",
            "body": "Body editado pero inválido por falta de título",
            "date": "fecha-invalida",
            "source": "",
            "category": "CategoríaInexistente",
            "tags": "",
            "responses": ["Única respuesta"],
        },
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 400
    assert 'class="errors"' in html
    assert 'class="field-error"' in html
    assert "Title is required." in html
    assert "Invalid date format." in html
    assert "Selected category does not exist." in html
    assert "At least two responses are required." in html

    db.session.expire_all()
    unchanged = db.session.get(Question, question.id)
    assert unchanged.title == original_title
