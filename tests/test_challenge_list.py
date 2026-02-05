import models as db


def test_challenge_list_filters_by_category(login_client, challenge_pair):
    client = login_client

    response = client.get("/challenge/list?category=web")

    assert response.status_code == 200
    assert b"Web One" in response.data
    assert b"Crypto One" not in response.data


def test_challenge_list_filters_by_event(login_client, challenge_pair):
    client = login_client

    response = client.get("/challenge/list?event=must-2024")

    assert response.status_code == 200
    assert b"Crypto One" in response.data
    assert b"Web One" not in response.data


def test_challenge_list_filters_by_status_solved(login_client, user, challenge_pair):
    client = login_client
    web_challenge, crypto_challenge = challenge_pair
    db.Submission.create(
        user_id=user.id,
        challenge_id=web_challenge.id,
        flag="flag",
        status="CORRECT",
    )

    response = client.get("/challenge/list?status=solved")

    assert response.status_code == 200
    assert b"Web One" in response.data
    assert b"Crypto One" not in response.data


def test_challenge_list_filters_by_status_not_solved(login_client, user, challenge_pair):
    client = login_client
    web_challenge, crypto_challenge = challenge_pair
    db.Submission.create(
        user_id=user.id,
        challenge_id=web_challenge.id,
        flag="flag",
        status="CORRECT",
    )

    response = client.get("/challenge/list?status=not-solved")

    assert response.status_code == 200
    assert b"Crypto One" in response.data
    assert b"Web One" not in response.data


def test_challenge_list_invalid_category_404(login_client):
    client = login_client

    response = client.get("/challenge/list?category=unknown")

    assert response.status_code == 404


def test_challenge_list_invalid_event_404(login_client):
    client = login_client

    response = client.get("/challenge/list?event=unknown")

    assert response.status_code == 404
