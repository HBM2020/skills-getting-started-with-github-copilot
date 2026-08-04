from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_duplicate_signup_is_rejected_case_and_spaces_ignored():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "  MICHAEL@mergington.edu  "},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_empty_email_is_rejected():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email is required"


def test_signup_stores_normalized_email():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "  NewStudent@Mergington.edu "},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert activities["Chess Club"]["participants"][-1] == "newstudent@mergington.edu"
