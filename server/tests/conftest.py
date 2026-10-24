import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402
from config import TestConfig  # noqa: E402
from extensions import db  # noqa: E402


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def register(client, username, password="secret123"):
    r = client.post(
        "/signup",
        json={"username": username, "password": password, "password_confirmation": password},
    )
    return r.get_json()["token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}
