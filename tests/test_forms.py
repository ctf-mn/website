import models as db
from blueprints import auth


def test_register_form_valid():
    form = auth.RegisterForm(
        {
            "name": "user1",
            "email": "user1@example.com",
            "password": "secret12",
            "password_again": "secret12",
        }
    )
    assert form.is_valid()


def test_register_form_duplicate_name():
    db.User.create(
        name="taken",
        email="taken@example.com",
        password="hash",
        scores=0,
        solved_count=0,
    )
    form = auth.RegisterForm(
        {
            "name": "taken",
            "email": "new@example.com",
            "password": "secret12",
            "password_again": "secret12",
        }
    )
    assert not form.is_valid()
    assert "name" in form.error


def test_register_form_password_mismatch():
    form = auth.RegisterForm(
        {
            "name": "user2",
            "email": "user2@example.com",
            "password": "secret12",
            "password_again": "secret13",
        }
    )
    assert not form.is_valid()
    assert "password_again" in form.error


def test_login_form_rejects_bad_email():
    form = auth.LoginForm({"name_or_email": "bad@email"})
    assert not form.is_valid()
    assert "name_or_email" in form.error


def test_login_form_rejects_bad_name():
    form = auth.LoginForm({"name_or_email": "bad name"})
    assert not form.is_valid()
    assert "name_or_email" in form.error
