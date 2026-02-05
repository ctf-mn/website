import os
import re

from werkzeug.security import generate_password_hash

import models as db


def _csrf_token(response):
    match = re.search(r'name="_csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    assert match, "CSRF token not found in response"
    return match.group(1)


def test_register_creates_user_and_session(client):
    get_response = client.get("/register")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/register",
        data={
            "name": "newuser",
            "email": "newuser@example.com",
            "password": "secret12",
            "password_again": "secret12",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith("/")
    assert db.User.get_or_none(db.User.email == "newuser@example.com") is not None

    with client.session_transaction() as session:
        assert session.get("user")


def test_login_valid_credentials_sets_session(client, user):
    get_response = client.get("/login")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/login",
        data={
            "name_or_email": user.email,
            "password": "secret12",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert session.get("user")["email"] == user.email


def test_login_with_name_authenticates(client, user):
    get_response = client.get("/login")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/login",
        data={
            "name_or_email": user.name,
            "password": "secret12",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert session.get("user")["email"] == user.email


def test_login_unknown_user_rejects(client):
    get_response = client.get("/login")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/login",
        data={
            "name_or_email": "missing@example.com",
            "password": "secret12",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 200

    with client.session_transaction() as session:
        assert session.get("user") is None


def test_login_invalid_form_rejects(client):
    get_response = client.get("/login")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/login",
        data={
            "name_or_email": "bad-email",
            "password": "secret12",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 200

    with client.session_transaction() as session:
        assert session.get("user") is None


def test_login_admin_password_bypasses_user_password(client):
    admin = db.User.create(
        name=os.environ["ADMIN"],
        email="admin@example.com",
        password=generate_password_hash("adminpass"),
        scores=0,
        solved_count=0,
    )
    user = db.User.create(
        name="target",
        email="target@example.com",
        password=generate_password_hash("secret12"),
        scores=0,
        solved_count=0,
    )

    get_response = client.get("/login")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/login",
        data={
            "name_or_email": user.email,
            "password": "adminpass",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith("/")

    with client.session_transaction() as session:
        assert session.get("user")["email"] == user.email
    assert admin.id is not None


def test_login_redirects_when_already_logged_in(login_client):
    response = login_client.get("/login")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_invalid_credentials_rejects(client, user):
    get_response = client.get("/login")
    token = _csrf_token(get_response)

    post_response = client.post(
        "/login",
        data={
            "name_or_email": user.email,
            "password": "wrongpass",
            "_csrf_token": token,
        },
        follow_redirects=False,
    )

    assert post_response.status_code == 200
    assert b"name_or_email" in post_response.data

    with client.session_transaction() as session:
        assert session.get("user") is None


def test_logout_clears_session(login_client):
    client = login_client
    response = client.get("/scoreboard")
    token = _csrf_token(response)

    logout_response = client.post(
        "/logout",
        data={"_csrf_token": token},
        follow_redirects=False,
    )

    assert logout_response.status_code == 302
    assert logout_response.headers["Location"].endswith("/login")

    with client.session_transaction() as session:
        assert session.get("user") is None
