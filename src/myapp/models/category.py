from myapp.extensions import db


class Category(db.Model):
    __tablename__ = "category"

    title = db.Column(db.String, primary_key=True)

    # Una categoría agrupa una o más preguntas (lado "1" de la relación).
    questions = db.relationship("Question", back_populates="category")

    def __repr__(self):
        return f"<Category {self.title}>"
