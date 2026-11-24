import uuid
from datetime import UTC, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from myapp.extensions import db
from myapp.models import Category, Question, Response, Tag
from myapp.services.categories import get_all_categories

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


def _parse_and_validate_question_form(form):
    """Extrae y valida los campos del formulario de creación/edición de pregunta."""
    title = form.get("title", "").strip()
    body = form.get("body", "").strip()
    date_raw = form.get("date", "").strip()
    source = form.get("source", "").strip()
    category_title = form.get("category", "").strip()
    tags_raw = form.get("tags", "").strip()
    raw_responses = form.getlist("responses")
    clean_responses = [r.strip() for r in raw_responses if r.strip()]

    form_data = {
        "title": title,
        "body": body,
        "date": date_raw,
        "source": source,
        "category": category_title,
        "tags": tags_raw,
        "responses": [r.strip() for r in raw_responses] or ["", ""],
    }

    field_errors: dict[str, str] = {}
    parsed_date = None

    if not title:
        field_errors["title"] = "Title is required."
    if not body:
        field_errors["body"] = "Body is required."

    if not date_raw:
        field_errors["date"] = "Date is required."
    else:
        try:
            parsed_date = datetime.strptime(date_raw, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            field_errors["date"] = "Invalid date format."

    category = db.session.get(Category, category_title) if category_title else None
    if not category_title:
        field_errors["category"] = "Category is required."
    elif category is None:
        field_errors["category"] = "Selected category does not exist."

    if len(clean_responses) < Question.MIN_RESPONSES:
        field_errors["responses"] = "At least two responses are required."

    errors = list(field_errors.values())
    tag_titles = [t.strip() for t in tags_raw.split(",") if t.strip()]

    parsed_payload = {
        "title": title,
        "body": body,
        "date": parsed_date,
        "source": source or None,
        "category": category,
        "tag_titles": tag_titles,
        "response_titles": clean_responses,
    }
    return parsed_payload, form_data, errors, field_errors


def _resolve_tags(tag_titles: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    seen: set[str] = set()
    for title in tag_titles:
        if title in seen:
            continue
        seen.add(title)
        tag = db.session.get(Tag, title)
        if tag is None:
            tag = Tag(title=title)
            db.session.add(tag)
        tags.append(tag)
    return tags


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
    payload, form_data, errors, field_errors = _parse_and_validate_question_form(
        request.form
    )
    if errors:
        return (
            render_template(
                "questions/new.html",
                question=None,
                categories=get_all_categories(),
                form_data=form_data,
                errors=errors,
                field_errors=field_errors,
            ),
            400,
        )

    question = Question(
        title=payload["title"],
        body=payload["body"],
        date=payload["date"],
        source=payload["source"],
        category=payload["category"],
        tags=_resolve_tags(payload["tag_titles"]),
        responses=[Response(title=title) for title in payload["response_titles"]],
    )
    db.session.add(question)
    db.session.commit()
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
    payload, form_data, errors, field_errors = _parse_and_validate_question_form(
        request.form
    )
    if errors:
        return (
            render_template(
                "questions/edit.html",
                question=question,
                categories=get_all_categories(),
                form_data=form_data,
                errors=errors,
                field_errors=field_errors,
            ),
            400,
        )

    question.title = payload["title"]
    question.body = payload["body"]
    question.date = payload["date"]
    question.source = payload["source"]
    question.category = payload["category"]
    question.tags = _resolve_tags(payload["tag_titles"])
    question.responses = [Response(title=title) for title in payload["response_titles"]]
    db.session.commit()
    flash("Question updated successfully.", "success")
    return redirect(url_for("questions.detail", question_id=question.id))


@questions_bp.post("/<question_id>/delete")
def delete(question_id: str):
    question = get_question_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "success")
    return redirect(url_for("questions.index"))
