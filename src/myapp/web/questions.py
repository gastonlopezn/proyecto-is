import uuid

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from myapp.models import Question
from myapp.services.categories import get_all_categories
from myapp.services.questions import (
    QuestionValidationError,
    create_question,
    delete_question,
    get_question,
    list_questions,
    update_question,
)

questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


def get_question_or_404(question_id: str | uuid.UUID) -> Question:
    """Busca una pregunta por UUID o aborta con 404 si no existe o el ID es inválido."""
    question = get_question(question_id)
    if question is None:
        abort(404)
    return question


def _extract_form_data(form) -> dict[str, object]:
    """Extrae y normaliza los campos del formulario HTML para enviarlos al servicio."""
    raw_responses = form.getlist("responses")
    return {
        "title": form.get("title", "").strip(),
        "body": form.get("body", "").strip(),
        "date": form.get("date", "").strip(),
        "source": form.get("source", "").strip(),
        "category": form.get("category", "").strip(),
        "tags": form.get("tags", "").strip(),
        "responses": [r.strip() for r in raw_responses] or ["", ""],
    }


@questions_bp.app_errorhandler(404)
def not_found_error(_error):
    return render_template("errors/404.html"), 404


@questions_bp.get("/")
def index():
    questions = list_questions()
    return render_template(
        "questions/index.html",
        questions=questions,
    )


@questions_bp.get("/new")
def new():
    categories = get_all_categories()
    return render_template(
        "questions/new.html",
        question=None,
        categories=categories,
    )


@questions_bp.post("")
@questions_bp.post("/")
def create():
    form_data = _extract_form_data(request.form)
    try:
        question = create_question(form_data)
    except QuestionValidationError as exc:
        return (
            render_template(
                "questions/new.html",
                question=None,
                categories=get_all_categories(),
                form_data=form_data,
                errors=exc.errors,
                field_errors=exc.field_errors,
            ),
            400,
        )

    flash("Question created successfully.", "success")
    return redirect(url_for("questions.detail", question_id=question.id))


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
    categories = get_all_categories()
    return render_template(
        "questions/edit.html",
        question=question,
        categories=categories,
    )


@questions_bp.post("/<question_id>")
def update(question_id: str):
    question = get_question_or_404(question_id)
    form_data = _extract_form_data(request.form)
    try:
        update_question(question, form_data)
    except QuestionValidationError as exc:
        return (
            render_template(
                "questions/edit.html",
                question=question,
                categories=get_all_categories(),
                form_data=form_data,
                errors=exc.errors,
                field_errors=exc.field_errors,
            ),
            400,
        )

    flash("Question updated successfully.", "success")
    return redirect(url_for("questions.detail", question_id=question.id))


@questions_bp.post("/<question_id>/delete")
def delete(question_id: str):
    question = get_question_or_404(question_id)
    delete_question(question)
    flash("Question deleted successfully.", "success")
    return redirect(url_for("questions.index"))
