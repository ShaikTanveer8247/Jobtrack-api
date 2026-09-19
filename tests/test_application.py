from app.models import Application, User
from datetime import datetime

def test_user_cannot_access_another_users_application(
    client,
    db_session,
):
    other_user = User(
        id=2,
        email="other@example.com",
        password_hash="test-password",
    )

    db_session.add(other_user)
    db_session.commit()

    other_application = Application(
        user_id=2,
        company="Private Company",
        role="Private Backend Intern",
        status="Applied",
    )

    db_session.add(other_application)
    db_session.commit()
    db_session.refresh(other_application)

    response = client.get(
        f"/api/v1/applications/{other_application.id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"
    
def test_create_application(client):
    response = client.post(
        "/api/v1/applications/",
        json={
            "company": "Test Company",
            "role": "Backend Intern",
            "status": "Applied",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company"] == "Test Company"
    assert data["role"] == "Backend Intern"
    assert data["status"] == "Applied"

def test_get_applications(client):
    response = client.post(
        "/api/v1/applications/",
        json={
            "company": "Google",
            "role": "Python Backend Intern",
            "status": "Applied",
        },
    )

    assert response.status_code == 201

    response = client.get("/api/v1/applications")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["company"] == "Google"
    assert data[0]["status"] == "Applied"


def test_duplicate_application(client):
    application = {
        "company": "Microsoft",
        "role": "Backend Developer Intern",
        "status": "Applied",
    }

    first_response = client.post(
        "/api/v1/applications/",
        json=application,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/applications/",
        json=application,
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "An application for this company and role already exists for this user"
    )

def test_application_status_history(client):
    create_response = client.post(
        "/api/v1/applications/",
        json={
            "company": "Google",
            "role": "Python Backend Intern",
            "status": "Applied",
        },
    )

    assert create_response.status_code == 201

    application_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/v1/applications/{application_id}",
        json={
            "status": "Interview",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Interview"

    history_response = client.get(
        f"/api/v1/applications/{application_id}/history"
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["old_status"] is None
    assert history[0]["new_status"] == "Applied"

    assert history[1]["old_status"] == "Applied"
    assert history[1]["new_status"] == "Interview"

def test_user_cannot_update_another_users_application(
    client,
    db_session,
):
    other_user = User(
        id=2,
        email="other@example.com",
        password_hash="test-password",
    )

    db_session.add(other_user)
    db_session.commit()

    other_application = Application(
        user_id=2,
        company="Private Company",
        role="Private Backend Intern",
        status="Applied",
    )

    db_session.add(other_application)
    db_session.commit()
    db_session.refresh(other_application)

    response = client.put(
        f"/api/v1/applications/{other_application.id}",
        json={
            "status": "Interview",
        },
    )

    assert response.status_code == 404

def test_delete_application(client):
    create_response = client.post(
        "/api/v1/applications/",
        json={
            "company": "Delete Test",
            "role": "Backend Intern",
            "status": "Applied",
        },
    )

    application_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/applications/{application_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Application deleted successfully",
        "id": application_id,
    }

def test_delete_interview(client, db_session):
    application = Application(
        user_id=1,
        company="Delete Interview Test",
        role="Backend Intern",
        status="Interview",
    )

    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)

    create_response = client.post(
        "/api/v1/interviews/",
        json={
            "application_id": application.id,
            "round": "Technical",
            "interview_date": "2026-09-25T10:30:00",
            "notes": "Delete test",
            "result": "Pending",
        },
    )

    interview_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/interviews/{interview_id}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Interview deleted successfully",
        "id": interview_id,
    }