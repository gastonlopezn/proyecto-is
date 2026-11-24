def test_detail_returns_200_and_uses_detail_template(client, question):
    response = client.get(f"/questions/{question.id}")

    assert response.status_code == 200
    assert f"<title>{question.title}</title>" in response.get_data(as_text=True)


def test_detail_shows_all_question_information(client, question):
    html = client.get(f"/questions/{question.id}").get_data(as_text=True)

    assert question.title in html
    assert question.body in html
    assert question.date.strftime("%Y-%m-%d") in html
    assert question.source in html
    assert question.state.value in html
    assert question.category_title in html
    for tag in question.tags:
        assert tag.title in html
    for response in question.responses:
        assert response.title in html


def test_detail_has_links_to_edit_and_back_to_list(client, question):
    html = client.get(f"/questions/{question.id}").get_data(as_text=True)

    assert f'href="/questions/{question.id}/edit"' in html
    assert 'href="/questions/"' in html
