from myapp.extensions import db
from myapp.models import Category, Question, Response, StateType


def test_read_questions_list_when_empty(client):
    response = client.get("/questions/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "<h1>Questions</h1>" in html
    assert "No questions yet." in html


def test_read_questions_list_with_multiple_questions(client, question):
    sports_category = Category(title="Deportes")
    second_question = Question(
        title="¿Ganará Argentina la próxima Copa América?",
        body="Se define según el resultado oficial de CONMEBOL.",
        category=sports_category,
        state=StateType.CLOSED,
        responses=[
            Response(title="Sí", price=0.55),
            Response(title="No", price=0.45),
        ],
    )
    db.session.add_all([sports_category, second_question])
    db.session.commit()

    response = client.get("/questions/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "No questions yet." not in html

    for item in (question, second_question):
        assert item.title in html
        assert item.category_title in html
        assert item.date.strftime("%Y-%m-%d") in html
        assert item.state.value in html
        assert f'href="/questions/{item.id}"' in html
