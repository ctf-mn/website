import os

import models as db


def test_api_challenge_rejects_bad_key(client):
    response = client.post("/api/challenge", data={"key": "bad"})

    assert response.status_code == 404


def test_api_challenge_invalid_event_returns_error(client):
    response = client.post(
        "/api/challenge",
        data={
            "key": os.environ["API_CHALLENGE_KEY"],
            "id": "1",
            "name": "Test",
            "description": "Desc",
            "author": "author",
            "event": "unknown-event",
            "category": "web",
            "flag": "FLAG{test}",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["error"] == "Unregistered event: unknown-event"


def test_api_challenge_creates_challenge(client):
    response = client.post(
        "/api/challenge",
        data={
            "key": os.environ["API_CHALLENGE_KEY"],
            "id": "42",
            "name": "API Challenge",
            "description": "Desc",
            "author": "author",
            "event": "ctf-mn",
            "category": "web",
            "flag": "FLAG{test}",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["new"]["name"] == "API Challenge"

    challenge = db.Challenge.get_by_id(42)
    assert challenge.title == "API Challenge"
    assert challenge.event == "ctf-mn"
    assert challenge.category == "web"
