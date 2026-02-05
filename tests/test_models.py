import models as db


def test_user_save_updates_timestamp():
    user = db.User.create(
        name="alice",
        email="alice@example.com",
        password="hash",
        scores=0,
        solved_count=0,
    )
    assert user.updated_at is None
    user.name = "alice2"
    user.save()
    assert user.updated_at is not None


def test_submission_challenge_property():
    user = db.User.create(
        name="bob",
        email="bob@example.com",
        password="hash",
        scores=0,
        solved_count=0,
    )
    challenge = db.Challenge.create(
        title="Test",
        content="Content",
        flag="flag",
        author="author",
        category="web",
        event="ctf-mn",
        score=1000,
        solved_count=0,
    )
    submission = db.Submission.create(
        user_id=user.id,
        challenge_id=challenge.id,
        flag="flag",
        status="CORRECT",
    )
    assert submission.challenge.id == challenge.id


def test_contest_team_member_users():
    user = db.User.create(
        name="carol",
        email="carol@example.com",
        password="hash",
        scores=0,
        solved_count=0,
    )
    team = db.ContestTeam.create(
        contest_id=1,
        title="Team",
        status="ACTIVE",
        members="|carol|",
        service="",
        scores=0,
        solved_count=0,
    )
    members = team.member_users
    assert len(members) == 1
    assert members[0].id == user.id
