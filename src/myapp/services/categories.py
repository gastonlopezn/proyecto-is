from myapp.extensions import db
from myapp.models import Category

INITIAL_CATEGORIES = [
    "Política",
    "Deportes",
    "Economía",
    "Cripto",
    "Tecnología",
    "Ciencia",
    "Entretenimiento",
    "Clima",
]


def seed_categories(titles=INITIAL_CATEGORIES):
    """Crea las categorías que todavía no existen. Es idempotente.

    Devuelve la lista de títulos que se crearon en esta ejecución.
    """
    existing = set(db.session.scalars(db.select(Category.title)).all())
    created = []
    for title in titles:
        if title not in existing:
            db.session.add(Category(title=title))
            existing.add(title)
            created.append(title)
    db.session.commit()
    return created


def get_all_categories():
    """Categorías ordenadas por título, para usar en el formulario de preguntas."""
    return db.session.scalars(db.select(Category).order_by(Category.title)).all()
