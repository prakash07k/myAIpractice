from urllib.parse import quote
import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    # Keep a deep copy of the activities and restore after each test to avoid cross-test pollution
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    email = "tester@example.com"

    # Ensure the email is not already registered
    assert email not in activities[activity]["participants"]

    # Signup should succeed
    signup_url = f"/activities/{quote(activity)}/signup"
    resp = client.post(signup_url, params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail with 400
    resp_dup = client.post(signup_url, params={"email": email})
    assert resp_dup.status_code == 400

    # Unregister should succeed
    unregister_url = f"/activities/{quote(activity)}/unregister"
    resp_un = client.post(unregister_url, params={"email": email})
    assert resp_un.status_code == 200
    assert email not in activities[activity]["participants"]

    # Unregistering again should return 400
    resp_un_again = client.post(unregister_url, params={"email": email})
    assert resp_un_again.status_code == 400


def test_signup_missing_activity():
    client = TestClient(app)
    resp = client.post("/activities/DoesNotExist/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
