from datetime import datetime, timedelta, timezone

import models as db
import web


def test_user_profile_shows_solved_challenges():
    user = db.User.create(
        name="profile",
        email="profile@example.com",
        password="hash",
        scores=0,
        solved_count=0,
    )
    challenge = db.Challenge.create(
        title="Profile Challenge",
        content="Content",
        flag="flag",
        author="author",
        category="web",
        event="ctf-mn",
        score=1000,
        solved_count=0,
    )
    db.Submission.create(
        user_id=user.id,
        challenge_id=challenge.id,
        flag="flag",
        status="CORRECT",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1),
    )

    client = web.app.test_client()
    response = client.get(f"/user/{user.name}")

    assert response.status_code == 200
    assert b"Profile Challenge" in response.data
    assert b"profile" in response.data
