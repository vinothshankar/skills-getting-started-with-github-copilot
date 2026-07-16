from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_and_remove_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert duplicate_response.status_code == 400
    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]
