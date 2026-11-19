from myapp.extensions import db
from myapp.models import Category, Question, Response, Tag, question_tag


def make_question(category, tags=()):
    question = Question(
        title="¿Alcanzará Bitcoin los 200.000 dólares en 2026?",
        body="Se resuelve con el precio de cierre del 31/12/2026.",
        category=category,
        tags=list(tags),
        responses=[
            Response(title="Sí", price=0.4),
            Response(title="No", price=0.6),
        ],
    )
    db.session.add(question)
    db.session.commit()
    return question


def test_question_belongs_to_one_category(app):
    category = Category(title="Cripto")
    question = make_question(category)

    assert question.category is category
    assert question.category_title == "Cripto"
    assert category.questions == [question]


def test_question_can_have_zero_or_more_tags(app):
    category = Category(title="Cripto")
    no_tags = make_question(category)
    btc, mercado = Tag(title="bitcoin"), Tag(title="mercados")
    with_tags = make_question(category, tags=[btc, mercado])

    assert no_tags.tags == []
    assert {tag.title for tag in with_tags.tags} == {"bitcoin", "mercados"}
    assert btc.questions == [with_tags]


def test_question_has_responses_and_each_response_belongs_to_it(app):
    question = make_question(Category(title="Cripto"))

    assert len(question.responses) == 2
    assert question.has_enough_responses()
    assert all(response.question is question for response in question.responses)


def test_deleting_question_deletes_responses_and_tag_links(app):
    tag = Tag(title="bitcoin")
    question = make_question(Category(title="Cripto"), tags=[tag])

    db.session.delete(question)
    db.session.commit()

    assert db.session.scalars(db.select(Question)).all() == []
    assert db.session.scalars(db.select(Response)).all() == []
    assert db.session.execute(db.select(question_tag)).all() == []
    # El tag y la categoría siguen existiendo: solo se borra la asociación.
    assert db.session.get(Tag, "bitcoin") is not None
    assert db.session.get(Category, "Cripto") is not None
