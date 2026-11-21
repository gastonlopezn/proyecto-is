from flask import Blueprint, render_template

from myapp.extensions import db
from myapp.models.question import Question

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


@questions_bp.get("/")
def index():
    questions = db.session.scalars(db.select(Question)).all()
    return render_template(
        "questions/index.html",
        questions=questions,
    )
