import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from myapp.extensions import db
from myapp.models import Category, Question, Response, StateType, Tag


class QuestionValidationError(ValueError):
    """Error de validación de dominio para creación o actualización de preguntas."""

    def __init__(self, field_errors: dict[str, str]):
        self.field_errors = field_errors
        self.errors = list(field_errors.values())
        super().__init__("; ".join(self.errors))


def parse_question_id(question_id: str | uuid.UUID) -> uuid.UUID | None:
    """Convierte un string o UUID en uuid.UUID, o devuelve None si es inválido."""
    if isinstance(question_id, uuid.UUID):
        return question_id
    try:
        return uuid.UUID(str(question_id))
    except (ValueError, TypeError):
        return None


def _parse_date(raw_date: Any) -> datetime | None:
    if isinstance(raw_date, datetime):
        return raw_date if raw_date.tzinfo else raw_date.replace(tzinfo=UTC)
    if not isinstance(raw_date, str):
        return None

    value = raw_date.strip()
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
    except ValueError:
        pass

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _normalize_tags(raw_tags: Any) -> list[str] | None:
    if raw_tags is None:
        return []
    if isinstance(raw_tags, str):
        return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    if isinstance(raw_tags, list):
        titles: list[str] = []
        for item in raw_tags:
            if not isinstance(item, str):
                return None
            cleaned = item.strip()
            if cleaned:
                titles.append(cleaned)
        return titles
    return None


def _normalize_responses(raw_responses: Any) -> list[str] | None:
    if not isinstance(raw_responses, list):
        return None
    titles: list[str] = []
    for item in raw_responses:
        if isinstance(item, str):
            cleaned = item.strip()
        elif isinstance(item, Mapping) and isinstance(item.get("title"), str):
            cleaned = item["title"].strip()
        else:
            return None
        if cleaned:
            titles.append(cleaned)
    return titles


def validate_question_data(
    data: Mapping[str, Any],
    *,
    partial: bool = False,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Valida datos de entrada para crear o actualizar una Question.

    Soporta payloads de formularios HTML y payloads JSON (incluyendo PATCH parcial).
    """
    field_errors: dict[str, str] = {}
    payload: dict[str, Any] = {}

    if not partial or "title" in data:
        raw_title = data.get("title")
        title = raw_title.strip() if isinstance(raw_title, str) else ""
        if not title:
            field_errors["title"] = "Title is required."
        else:
            payload["title"] = title

    if not partial or "body" in data:
        raw_body = data.get("body")
        body = raw_body.strip() if isinstance(raw_body, str) else ""
        if not body:
            field_errors["body"] = "Body is required."
        else:
            payload["body"] = body

    if not partial or "date" in data:
        raw_date = data.get("date")
        if raw_date is None or (isinstance(raw_date, str) and not raw_date.strip()):
            field_errors["date"] = "Date is required."
        else:
            parsed_date = _parse_date(raw_date)
            if parsed_date is None:
                field_errors["date"] = "Invalid date format."
            else:
                payload["date"] = parsed_date

    if not partial or "source" in data:
        raw_source = data.get("source")
        if raw_source is None:
            payload["source"] = None
        elif isinstance(raw_source, str):
            payload["source"] = raw_source.strip() or None
        else:
            field_errors["source"] = "Source must be a string."

    if not partial or "category" in data:
        raw_category = data.get("category")
        category_title = raw_category.strip() if isinstance(raw_category, str) else ""
        category = db.session.get(Category, category_title) if category_title else None
        if not category_title:
            field_errors["category"] = "Category is required."
        elif category is None:
            field_errors["category"] = "Selected category does not exist."
        else:
            payload["category"] = category

    if not partial or "tags" in data:
        tag_titles = _normalize_tags(data.get("tags"))
        if tag_titles is None:
            field_errors["tags"] = "Tags must be a list of strings."
        else:
            payload["tag_titles"] = tag_titles

    if not partial or "responses" in data:
        response_titles = _normalize_responses(data.get("responses"))
        if response_titles is None or len(response_titles) < Question.MIN_RESPONSES:
            field_errors["responses"] = "At least two responses are required."
        else:
            payload["response_titles"] = response_titles

    return payload, field_errors


def resolve_tags(tag_titles: list[str]) -> list[Tag]:
    """Busca tags existentes o crea los faltantes evitando duplicados."""
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


def list_questions(
    *,
    category: str | None = None,
    state: str | StateType | None = None,
) -> list[Question]:
    """Devuelve la lista de preguntas con filtros opcionales por categoría y estado."""
    stmt = db.select(Question)

    if category is not None and category.strip():
        stmt = stmt.where(Question.category_title == category.strip())

    if state is not None:
        if isinstance(state, StateType):
            parsed_state = state
        elif isinstance(state, str):
            try:
                parsed_state = StateType(state.strip().upper())
            except ValueError as exc:
                raise QuestionValidationError(
                    {"state": "Invalid state. Expected OPEN or CLOSED."}
                ) from exc
        else:
            raise QuestionValidationError(
                {"state": "Invalid state. Expected OPEN or CLOSED."}
            )
        stmt = stmt.where(Question.state == parsed_state)

    return list(db.session.scalars(stmt).all())


def get_question(question_id: str | uuid.UUID) -> Question | None:
    """Devuelve la pregunta correspondiente al UUID o None si no existe o es inválido."""
    parsed_id = parse_question_id(question_id)
    if parsed_id is None:
        return None
    return db.session.get(Question, parsed_id)


def create_question(data: Mapping[str, Any]) -> Question:
    """Valida y persiste una nueva pregunta con sus tags y respuestas."""
    payload, field_errors = validate_question_data(data, partial=False)
    if field_errors:
        raise QuestionValidationError(field_errors)

    question = Question(
        title=payload["title"],
        body=payload["body"],
        date=payload["date"],
        source=payload["source"],
        category=payload["category"],
        tags=resolve_tags(payload["tag_titles"]),
        responses=[Response(title=title) for title in payload["response_titles"]],
    )
    db.session.add(question)
    db.session.commit()
    return question


def update_question(
    question: Question,
    data: Mapping[str, Any],
    *,
    partial: bool = False,
) -> Question:
    """Valida y actualiza una pregunta existente (completa o parcialmente)."""
    payload, field_errors = validate_question_data(data, partial=partial)
    if field_errors:
        raise QuestionValidationError(field_errors)

    if "title" in payload:
        question.title = payload["title"]
    if "body" in payload:
        question.body = payload["body"]
    if "date" in payload:
        question.date = payload["date"]
    if "source" in payload:
        question.source = payload["source"]
    if "category" in payload:
        question.category = payload["category"]
    if "tag_titles" in payload:
        question.tags = resolve_tags(payload["tag_titles"])
    if "response_titles" in payload:
        question.responses = [
            Response(title=title) for title in payload["response_titles"]
        ]

    db.session.commit()
    return question


def delete_question(question: Question) -> None:
    """Elimina una pregunta y sus dependencias en cascada."""
    db.session.delete(question)
    db.session.commit()
