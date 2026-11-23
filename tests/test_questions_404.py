import uuid


def test_get_question_detail_returns_404_when_id_does_not_exist(client):
    missing_uuid = uuid.uuid4()
    response = client.get(f"/questions/{missing_uuid}")
    assert response.status_code == 404
    assert b"404" in response.data

    invalid_id_response = client.get("/questions/non-existent-id")
    assert invalid_id_response.status_code == 404


def test_get_question_edit_returns_404_when_id_does_not_exist(client):
    missing_uuid = uuid.uuid4()
    response = client.get(f"/questions/{missing_uuid}/edit")
    assert response.status_code == 404
    assert b"404" in response.data

    invalid_id_response = client.get("/questions/999/edit")
    assert invalid_id_response.status_code == 404


def test_post_question_update_returns_404_when_id_does_not_exist(client):
    missing_uuid = uuid.uuid4()
    response = client.post(
        f"/questions/{missing_uuid}",
        data={"title": "Updated", "body": "Body"},
    )
    assert response.status_code == 404

    invalid_id_response = client.post(
        "/questions/999",
        data={"title": "Updated", "body": "Body"},
    )
    assert invalid_id_response.status_code == 404


def test_post_question_delete_returns_404_when_id_does_not_exist(client):
    missing_uuid = uuid.uuid4()
    response = client.post(f"/questions/{missing_uuid}/delete")
    assert response.status_code == 404

    invalid_id_response = client.post("/questions/999/delete")
    assert invalid_id_response.status_code == 404
