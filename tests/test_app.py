from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "new.student@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {participant_email} for {activity_name}"}
    assert participant_email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    participant_email = activities[activity_name]["participants"][0]
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": participant_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    participant_email = activities[activity_name]["participants"][0]
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_activity}/participants", params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "missing@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{encoded_activity}/participants", params={"email": participant_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
