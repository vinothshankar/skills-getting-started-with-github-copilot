from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    path = "/"

    response = client.get(path, follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_list_activities_returns_seed_data(client):
    path = "/activities"

    response = client.get(path)

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_unknown_activity_returns_404(client):
    path = "/activities/Unknown Activity/signup?email=test@example.com"

    response = client.post(path)

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client):
    path = "/activities/Chess Club/signup?email=michael@mergington.edu"

    response = client.post(path)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_unknown_participant_returns_404(client):
    path = "/activities/Chess Club/participants/not_found@mergington.edu"

    response = client.delete(path)

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_and_remove_participant_flow(client):
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    remove_response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert remove_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]
