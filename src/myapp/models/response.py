import uuid

from myapp.extensions import db


class Response(db.Model):
    __tablename__ = "response"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    probability = db.Column(db.Float, nullable=False, default=0.0)
    is_winner = db.Column(db.Boolean, nullable=False, default=False)

    # Cada respuesta pertenece a exactamente una pregunta.
    question_id = db.Column(
        db.Uuid,
        db.ForeignKey("question.id", ondelete="CASCADE"),
        nullable=False,
    )
    question = db.relationship("Question", back_populates="responses")
    positions = db.relationship(
        "Position",
        back_populates="response",
        cascade="all, delete-orphan",
    )

    def calculate_probability(self):
        pass

    def __repr__(self) -> str:
        return f"<Response {self.title!r}>"
