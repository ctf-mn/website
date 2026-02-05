import web


def test_index_redirects_to_challenge_list():
    client = web.app.test_client()
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/challenge/list")
