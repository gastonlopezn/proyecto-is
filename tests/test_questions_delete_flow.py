from myapp.extensions import db
from myapp.models import Question, Response, Tag, question_tag


def test_detail_page_has_delete_button_that_posts(client, question):
    html = client.get(f"/questions/{question.id}").get_data(as_text=True)

    assert f'action="/questions/{question.id}/delete"' in html
    assert 'method="post"' in html
    assert "Delete question" in html


def test_delete_removes_question_responses_and_tag_links(client, question):
    question_id = question.id

    response = client.post(f"/questions/{question_id}/delete")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/questions/")
    db.session.expire_all()
    assert db.session.get(Question, question_id) is None
    assert db.session.scalars(db.select(Response)).all() == []
    assert db.session.execute(db.select(question_tag)).all() == []
    # El tag en sí no se borra: solo su asociación con la pregunta.
    assert db.session.get(Tag, "bitcoin") is not None


def test_get_delete_is_not_allowed(client, question):
    response = client.get(f"/questions/{question.id}/delete")

    assert response.status_code == 405
    assert db.session.get(Question, question.id) is not None
