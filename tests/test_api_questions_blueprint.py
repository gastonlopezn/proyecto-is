from flask import abort


def test_api_questions_blueprint_is_registered_with_prefix(app):
    assert "api_questions" in app.blueprints
    assert app.blueprints["api_questions"].url_prefix == "/api/questions"


def test_api_404_returns_json_while_web_404_returns_html(client):
    api_response = client.get("/api/questions/non-existent")
    assert api_response.status_code == 404
    assert api_response.is_json
    assert "error" in api_response.get_json()

    web_response = client.get("/questions/non-existent")
    assert web_response.status_code == 404
    assert not web_response.is_json
    assert b"404" in web_response.data


def test_api_400_returns_json(app, client):
    @app.get("/api/_test_bad_request")
    def trigger_bad_request():
        abort(400, description="Invalid API payload.")

    response = client.get("/api/_test_bad_request")
    assert response.status_code == 400
    assert response.is_json
    assert response.get_json() == {"error": "Invalid API payload."}


def test_api_405_returns_json(app, client):
    @app.get("/api/_test_get_only")
    def get_only():
        return {"ok": True}

    response = client.post("/api/_test_get_only")
    assert response.status_code == 405
    assert response.is_json
    assert "error" in response.get_json()
