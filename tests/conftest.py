import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

TEST_DB_PATH = Path(__file__).resolve().parent / "test.db"

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("SESSION_KEY", "test-session-key")
os.environ.setdefault("API_CHALLENGE_KEY", "test-api-key")
os.environ.setdefault("ADMIN", "admin")

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

import models as db
import web

MODELS = [
    db.User,
    db.Challenge,
    db.Submission,
    db.Contest,
    db.ContestTeam,
    db.ContestChallenge,
    db.ContestSubmission,
]


@pytest.fixture(autouse=True)
def db_state():
    db.database.connect(reuse_if_open=True)
    db.database.drop_tables(list(reversed(MODELS)), safe=True)
    db.database.create_tables(MODELS)
    yield
    db.database.close()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def contest():
    now = datetime.now(UTC).replace(tzinfo=None)
    return db.Contest.create(
        id=4,
        title="Test Contest",
        status="ACTIVE",
        start_at=now - timedelta(hours=1),
        finish_at=now + timedelta(hours=1),
    )


@pytest.fixture
def user():
    return db.User.create(
        name="user",
        email="user@example.com",
        password=generate_password_hash("secret12"),
        scores=0,
        solved_count=0,
    )


@pytest.fixture
def client():
    return web.app.test_client()


@pytest.fixture
def login_client(contest, user):
    client = web.app.test_client()
    with client.session_transaction() as session:
        session["user"] = {"email": user.email, "logged_in": 0}
    return client


@pytest.fixture
def challenge():
    return db.Challenge.create(
        title="Test Challenge",
        content="Content",
        flag="FLAG{correct}",
        author="author",
        category="web",
        event="ctf-mn",
        score=1000,
        solved_count=0,
    )


@pytest.fixture
def challenge_pair():
    web_challenge = db.Challenge.create(
        title="Web One",
        content="Content",
        flag="flag",
        author="author",
        category="web",
        event="ctf-mn",
        score=1000,
        solved_count=0,
    )
    crypto_challenge = db.Challenge.create(
        title="Crypto One",
        content="Content",
        flag="flag",
        author="author",
        category="crypto",
        event="must-2024",
        score=1000,
        solved_count=0,
    )
    return web_challenge, crypto_challenge
