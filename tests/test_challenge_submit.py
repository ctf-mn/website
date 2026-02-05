from datetime import UTC, datetime, timedelta

import models as db


def _post_flag(client, challenge_id, flag):
    response = client.get(f"/challenge/{challenge_id}")
    html = response.get_data(as_text=True)
    start = html.find('name="_csrf_token"')
    token = html[start:].split('value="', 1)[1].split('"', 1)[0]
    return client.post(
        f"/challenge/{challenge_id}",
        data={"action": "flag", "flag": flag, "_csrf_token": token},
    )


def test_submit_incorrect_creates_submission_only(login_client, user, challenge):
    client = login_client

    response = _post_flag(client, challenge.id, "WRONG")

    assert response.status_code == 200
    submission = db.Submission.get_or_none(db.Submission.user_id == user.id)
    assert submission is not None
    assert submission.status == "INCORRECT"

    challenge_db = db.Challenge.get_by_id(challenge.id)
    user_db = db.User.get_by_id(user.id)
    assert challenge_db.solved_count == 0
    assert user_db.solved_count == 0
    assert user_db.scores == 0


def test_submit_correct_updates_scores_and_counts(login_client, user, challenge):
    client = login_client

    response = _post_flag(client, challenge.id, "FLAG{correct}")

    assert response.status_code == 200
    submission = db.Submission.get_or_none(db.Submission.user_id == user.id)
    assert submission is not None
    assert submission.status == "CORRECT"

    challenge_db = db.Challenge.get_by_id(challenge.id)
    user_db = db.User.get_by_id(user.id)
    assert challenge_db.solved_count == 1
    assert user_db.solved_count == 1
    assert user_db.scores == challenge_db.score


def test_submit_bruteforce_returns_wait_and_no_new_submission(login_client, user, challenge):
    db.Submission.create(
        user_id=user.id,
        challenge_id=challenge.id,
        flag="WRONG",
        status="INCORRECT",
        created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=10),
    )
    client = login_client

    response = _post_flag(client, challenge.id, "WRONG")

    assert response.status_code == 200
    assert b"Brute force attempt" in response.data
    assert db.Submission.select().where(db.Submission.user_id == user.id).count() == 1


def test_submit_already_solved_redirects_and_no_new_submission(login_client, user, challenge):
    db.Submission.create(
        user_id=user.id,
        challenge_id=challenge.id,
        flag="FLAG{correct}",
        status="CORRECT",
    )
    client = login_client

    response = _post_flag(client, challenge.id, "FLAG{correct}")

    assert response.status_code == 302
    assert db.Submission.select().where(db.Submission.user_id == user.id).count() == 1


def test_submit_correct_updates_previous_solver_score(login_client, user, challenge):
    previous = db.User.create(
        name="previous",
        email="previous@example.com",
        password="hash",
        scores=challenge.score,
        solved_count=1,
    )
    db.Submission.create(
        user_id=previous.id,
        challenge_id=challenge.id,
        flag=challenge.flag,
        status="CORRECT",
    )
    challenge.solved_count = 1
    challenge.save()

    client = login_client
    response = _post_flag(client, challenge.id, challenge.flag)

    assert response.status_code == 200

    challenge_db = db.Challenge.get_by_id(challenge.id)
    current_user = db.User.get_by_id(user.id)
    previous_user = db.User.get_by_id(previous.id)
    assert challenge_db.solved_count == 2
    assert challenge_db.score == 999
    assert current_user.scores == 999
    assert previous_user.scores == 999
