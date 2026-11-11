import uuid
from datetime import UTC, datetime

from myapp.extensions import db
from myapp.models.state_type import StateType


class Question(db.Model):
    __tablename__ = "question"

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

    def __repr__(self) -> str:
        return f"<Question {self.title!r} (State: {self.state.value})>"
