from myapp.extensions import db
from myapp.models.category import Category
from myapp.services.categories import (
    INITIAL_CATEGORIES,
    get_all_categories,
    seed_categories,
)


def count_categories():
    return db.session.scalar(db.select(db.func.count()).select_from(Category))


def test_seed_loads_initial_categories(app):
    created = seed_categories()

    assert created == INITIAL_CATEGORIES
    assert count_categories() == len(INITIAL_CATEGORIES)


def test_seed_twice_does_not_duplicate(app):
    seed_categories()
    created_again = seed_categories()

    assert created_again == []
    assert count_categories() == len(INITIAL_CATEGORIES)


def test_seed_only_adds_missing_categories(app):
    db.session.add(Category(title="Cripto"))
    db.session.commit()

    created = seed_categories()

    assert "Cripto" not in created
    assert count_categories() == len(INITIAL_CATEGORIES)


def test_get_all_categories_is_sorted(app):
    seed_categories()

    titles = [category.title for category in get_all_categories()]

    assert titles == sorted(INITIAL_CATEGORIES)


def test_seed_categories_cli_command(app):
    runner = app.test_cli_runner()

    first = runner.invoke(args=["seed-categories"])
    second = runner.invoke(args=["seed-categories"])

    assert first.exit_code == 0
    assert "Categorías creadas" in first.output
    assert "ya estaban cargadas" in second.output
    assert count_categories() == len(INITIAL_CATEGORIES)
