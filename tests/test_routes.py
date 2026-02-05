import models as db
import web


def test_scoreboard_renders_users():
    db.User.create(
        name="dave",
        email="dave@example.com",
        password="hash",
        scores=120,
        solved_count=2,
    )
    client = web.app.test_client()
    response = client.get("/scoreboard")
    assert response.status_code == 200
    assert b"dave" in response.data


def test_anonymous_challenge_view():
    challenge = db.Challenge.create(
        title="Test Challenge",
        content="Hello",
        flag="flag",
        author="author",
        category="web",
        event="ctf-mn",
        score=1000,
        solved_count=0,
    )
    client = web.app.test_client()
    response = client.get(f"/challenge/{challenge.id}")
    assert response.status_code == 200
    assert b"Test Challenge" in response.data
