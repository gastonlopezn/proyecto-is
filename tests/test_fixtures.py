from myapp.extensions import db
from myapp.models import Category, Question, StateType


def test_tests_use_in_memory_sqlite(app):
    assert app.config["TESTING"] is True
    assert db.engine.url.database in (None, "", ":memory:")


def test_database_starts_empty(app):
    assert db.session.scalars(db.select(Category)).all() == []
    assert db.session.scalars(db.select(Question)).all() == []


def test_data_does_not_leak_between_tests_part_1(app):
    db.session.add(Category(title="Temporal"))
    db.session.commit()

    assert db.session.get(Category, "Temporal") is not None


def test_data_does_not_leak_between_tests_part_2(app):
    # Corre después de la parte 1: la tabla tiene que volver a estar vacía.
    assert db.session.get(Category, "Temporal") is None


def test_category_fixture_is_persisted(category):
    assert db.session.get(Category, category.title) is category


def test_question_fixture_is_valid(question, category):
    saved = db.session.get(Question, question.id)

    assert saved is question
    assert saved.category is category
    assert saved.state == StateType.OPEN
    assert saved.has_enough_responses()
    assert [tag.title for tag in saved.tags] == ["bitcoin"]
