from myapp.extensions import db
from myapp.models import Category, Tag


def test_edit_question_form_returns_200_and_prefills_current_values(client, question):
    extra_category = Category(title="Economía")
    question.tags.append(Tag(title="cripto"))
    db.session.add(extra_category)
    db.session.commit()

    response = client.get(f"/questions/{question.id}/edit")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f'action="/questions/{question.id}"' in html
    assert 'method="post"' in html

    # Pre-filled question fields
    assert f'name="title"\n      value="{question.title}"' in html
    assert question.body in html
    assert f'name="date"\n      value="{question.date.strftime("%Y-%m-%d")}"' in html
    assert f'name="source"\n      value="{question.source}"' in html

    # Category select with current category pre-selected
    assert '<select id="category" name="category" required>' in html
    assert 'value="Cripto"\n          selected' in html
    assert 'value="Economía"' in html

    # Tags and responses pre-filled
    assert 'name="tags"' in html
    assert "bitcoin, cripto" in html
    assert 'value="Sí"' in html
    assert 'value="No"' in html


def test_edit_question_form_uses_creation_fields_and_hides_response_internals(
    client, question
):
    response = client.get(f"/questions/{question.id}/edit")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    for field_name in (
        'name="title"',
        'name="body"',
        'name="date"',
        'name="source"',
        'name="category"',
        'name="tags"',
        'name="responses"',
    ):
        assert field_name in html

    assert html.count('name="responses"') >= 2
    assert 'name="price"' not in html
    assert 'name="probability"' not in html
    assert 'name="is_winner"' not in html
    assert 'name="isWinner"' not in html
