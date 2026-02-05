from datetime import datetime, timedelta, timezone

import models as db
import web


def test_activity_lists_submissions():
    user = db.User.create(
        name="active",
        email="active@example.com",
        password="hash",
        scores=0,
        solved_count=0,
    )
    challenge = db.Challenge.create(
        title="Activity Challenge",
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
    response = client.get("/activity")

    assert response.status_code == 200
    assert b"Activity Challenge" in response.data
    assert b"active" in response.data
