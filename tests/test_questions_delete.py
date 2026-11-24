from myapp.extensions import db
from myapp.models import Category, Question, Response, Tag, question_tag


def test_delete_question_removes_it_from_database_and_list_view(client, question):
    question_id = question.id
    question_title = question.title

    response = client.post(f"/questions/{question_id}/delete")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/questions/")

    db.session.expire_all()
    assert db.session.get(Question, question_id) is None

    list_html = client.get("/questions/").get_data(as_text=True)
    assert question_title not in list_html
    assert "No questions yet." in list_html

    detail_response = client.get(f"/questions/{question_id}")
    assert detail_response.status_code == 404


def test_delete_question_removes_related_responses_and_tag_associations_only(
    client, question
):
    shared_tag = db.session.get(Tag, "bitcoin")
    extra_tag = Tag(title="mercados")
    question.tags.append(extra_tag)

    other_question = Question(
        title="¿Superará Ethereum los 10.000 USD en 2026?",
        body="Precio de cierre anual.",
        category=question.category,
        tags=[shared_tag],
        responses=[
            Response(title="Sí", price=0.35),
            Response(title="No", price=0.65),
        ],
    )
    db.session.add(other_question)
    db.session.commit()

    deleted_id = question.id
    deleted_response_ids = [r.id for r in question.responses]
    kept_id = other_question.id
    kept_response_ids = [r.id for r in other_question.responses]

    response = client.post(f"/questions/{deleted_id}/delete")
    assert response.status_code == 302

    db.session.expire_all()
    assert db.session.get(Question, deleted_id) is None
    for resp_id in deleted_response_ids:
        assert db.session.get(Response, resp_id) is None

    remaining_links = db.session.execute(db.select(question_tag)).all()
    assert remaining_links == [(kept_id, "bitcoin")]

    # Las entidades Tag y Category y la otra pregunta con sus respuestas permanecen intactas.
    assert db.session.get(Tag, "bitcoin") is not None
    assert db.session.get(Tag, "mercados") is not None
    assert db.session.get(Category, "Cripto") is not None
    assert db.session.get(Question, kept_id) is not None
    for resp_id in kept_response_ids:
        assert db.session.get(Response, resp_id) is not None
