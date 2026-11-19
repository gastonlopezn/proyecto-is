from myapp.extensions import db
from myapp.models.question_tag import question_tag


class Tag(db.Model):
    __tablename__ = "tag"

    title = db.Column(db.String, primary_key=True)

    questions = db.relationship(
        "Question",
        secondary=question_tag,
        back_populates="tags",
    )

    def __repr__(self):
        return f"<Tag {self.title}>"
