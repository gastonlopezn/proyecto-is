def test_questions_blueprint_is_registered_with_prefix(app):
    assert "questions" in app.blueprints
    assert app.blueprints["questions"].url_prefix == "/questions"


def test_base_template_includes_questions_navigation_link(client):
    response = client.get("/users/")

    assert response.status_code == 200
    assert b'href="/questions/"' in response.data
    assert b"Questions" in response.data


def test_questions_index_route_starts_and_responds_ok(client):
    response = client.get("/questions/")

    assert response.status_code == 200
    assert b"<h1>Questions</h1>" in response.data
