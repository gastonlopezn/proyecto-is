from datetime import UTC

from myapp.models import Question, Response


def serialize_response(response: Response) -> dict:
    """Serializa una respuesta a un diccionario JSON estándar."""
    return {
        "id": str(response.id),
        "title": response.title,
        "price": response.price,
        "probability": response.probability,
        "is_winner": response.is_winner,
    }


def serialize_question(question: Question) -> dict:
    """Serializa una pregunta (incluyendo sus respuestas y tags) a un diccionario JSON estándar."""
    category_val = question.category_title
    if not category_val and question.category:
        category_val = question.category.title

    state_val = question.state
    if hasattr(state_val, "value"):
        state_val = state_val.value
    elif state_val is not None:
        state_val = str(state_val)

    date_val = question.date
    if hasattr(date_val, "isoformat"):
        if date_val.tzinfo is None:
            date_val = date_val.replace(tzinfo=UTC)
        date_val = date_val.isoformat()

    tags_list = []
    if question.tags:
        for tag in question.tags:
            tag_str = tag.title if hasattr(tag, "title") else str(tag)
            tags_list.append(tag_str)

    responses_list = []
    if question.responses:
        for resp in question.responses:
            responses_list.append(serialize_response(resp))

    return {
        "id": str(question.id),
        "title": question.title,
        "body": question.body,
        "date": date_val,
        "source": question.source,
        "state": state_val,
        "category": category_val,
        "tags": tags_list,
        "responses": responses_list,
    }
