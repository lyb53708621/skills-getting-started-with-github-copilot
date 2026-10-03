import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(app_module.activities))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert activities["Soccer Team"]["participants"] == []
    assert activities["Soccer Team"]["max_participants"] == 18


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@mergington.edu for Soccer Team"
    }
    assert "student@mergington.edu" in client.get("/activities").json()["Soccer Team"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    signup_url = "/activities/Soccer Team/signup"
    params = {"email": "student@mergington.edu"}

    assert client.post(signup_url, params=params).status_code == 200
    response = client.post(signup_url, params=params)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert client.get("/activities").json()["Soccer Team"]["participants"].count(params["email"]) == 1


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_unregisters_participant(client):
    signup_url = "/activities/Soccer Team/signup"
    params = {"email": "student@mergington.edu"}
    client.post(signup_url, params=params)

    response = client.delete(signup_url, params=params)

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@mergington.edu from Soccer Team"
    }
    assert "student@mergington.edu" not in client.get("/activities").json()["Soccer Team"]["participants"]


def test_delete_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Soccer Team/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"