def test_users_page(client):
    response = client.get("/users/")

    assert response.status_code == 200
    assert b"Users" in response.data

