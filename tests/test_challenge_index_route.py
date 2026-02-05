import web


def test_challenge_index_redirects():
    client = web.app.test_client()
    response = client.get("/challenge")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/challenge/list")
