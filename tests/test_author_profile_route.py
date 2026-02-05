import models as db
import web


def test_author_profile_lists_challenges():
    challenge = db.Challenge.create(
        title="Author Challenge",
        content="Content",
        flag="flag",
        author="author1",
        category="web",
        event="ctf-mn",
        score=1000,
        solved_count=0,
    )

    client = web.app.test_client()
    response = client.get("/author/author1")

    assert response.status_code == 200
    assert b"Author Challenge" in response.data


def test_author_profile_404_for_unknown_author():
    client = web.app.test_client()
    response = client.get("/author/unknown")

    assert response.status_code == 404
