import uuid
from datetime import UTC, datetime

from myapp.extensions import db
from myapp.models.question_tag import question_tag
from myapp.models.state_type import StateType


class Question(db.Model):
    __tablename__ = "question"

    # Mínimo de respuestas que debe tener una pregunta (multiplicidad 2..* en el UML).
    MIN_RESPONSES = 2

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    source = db.Column(db.String(500), nullable=True)
    state = db.Column(
        db.Enum(
            StateType,
            name="state_type",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=StateType.OPEN,
    )

    # Cada pregunta pertenece a exactamente una categoría.
    category_title = db.Column(
        db.String,
        db.ForeignKey("category.title"),
        nullable=False,
    )
    category = db.relationship("Category", back_populates="questions")

    # Cero o más tags, a través de la tabla de asociación question_tag.
    # Al borrar la pregunta, SQLAlchemy elimina sus filas en question_tag.
    tags = db.relationship(
        "Tag",
        secondary=question_tag,
        back_populates="questions",
    )

    # Dos o más respuestas; se borran junto con la pregunta.
    responses = db.relationship(
        "Response",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        kwargs.setdefault("state", StateType.OPEN)
        super().__init__(**kwargs)

    def has_enough_responses(self) -> bool:
        return len(self.responses) >= self.MIN_RESPONSES

    def __repr__(self) -> str:
        state_value = self.state.value if self.state is not None else None
        return f"<Question {self.title!r} (State: {state_value})>"
