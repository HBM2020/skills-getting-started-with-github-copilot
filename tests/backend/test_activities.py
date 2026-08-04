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


def test_signup_activity_not_found():
    # Arrange
    unknown_activity = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_activity_full_capacity():
    # Arrange — fill Chess Club (max 12) to capacity
    activity_name = "Chess Club"
    max_participants = activities[activity_name]["max_participants"]
    while len(activities[activity_name]["participants"]) < max_participants:
        activities[activity_name]["participants"].append(
            f"filler{len(activities[activity_name]['participants'])}@mergington.edu"
        )

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "latecomer@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_successful_signup():
    # Arrange
    activity_name = "Drama Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]
