"""
Tests for the Mergington High School Activities API.
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_dict():
    response = client.get("/activities")
    data = response.json()
    assert isinstance(data, dict)


def test_get_activities_contains_known_activity():
    response = client.get("/activities")
    data = response.json()
    assert "Chess Club" in data


def test_get_activities_has_required_fields():
    response = client.get("/activities")
    data = response.json()
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new_student@mergington.edu"},
    )
    assert response.status_code == 200
    assert "new_student@mergington.edu" in response.json()["message"]


def test_signup_adds_participant_to_activity():
    email = "new_student@mergington.edu"
    client.post("/activities/Chess Club/signup", params={"email": email})
    assert email in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert response.status_code == 404


def test_signup_already_registered():
    email = activities["Chess Club"]["participants"][0]
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    email = activities["Chess Club"]["participants"][0]
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    email = activities["Chess Club"]["participants"][0]
    client.delete("/activities/Chess Club/signup", params={"email": email})
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent Activity/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_not_signed_up():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "notregistered@mergington.edu"},
    )
    assert response.status_code == 400
