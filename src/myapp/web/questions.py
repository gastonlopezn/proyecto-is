import uuid

from flask import Blueprint, abort, redirect, render_template, url_for

from myapp.extensions import db
from myapp.models.question import Question

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


def get_question_or_404(question_id: str | uuid.UUID) -> Question:
    """Busca una pregunta por UUID o aborta con 404 si no existe o el ID es inválido."""
    if isinstance(question_id, uuid.UUID):
        parsed_id = question_id
    else:
        try:
            parsed_id = uuid.UUID(str(question_id))
        except (ValueError, TypeError):
            abort(404)

    question = db.session.get(Question, parsed_id)
    if question is None:
        abort(404)
    return question


@questions_bp.app_errorhandler(404)
def not_found_error(_error):
    return render_template("errors/404.html"), 404


@questions_bp.get("/")
def index():
    questions = db.session.scalars(db.select(Question)).all()
    return render_template(
        "questions/index.html",
        questions=questions,
    )


@questions_bp.get("/<question_id>")
def detail(question_id: str):
    question = get_question_or_404(question_id)
    return render_template(
        "questions/detail.html",
        question=question,
    )


@questions_bp.get("/<question_id>/edit")
def edit(question_id: str):
    question = get_question_or_404(question_id)
    return render_template(
        "questions/detail.html",
        question=question,
    )


@questions_bp.post("/<question_id>")
def update(question_id: str):
    question = get_question_or_404(question_id)
    return redirect(url_for("questions.detail", question_id=question.id))


@questions_bp.post("/<question_id>/delete")
def delete(question_id: str):
    question = get_question_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("questions.index"))
