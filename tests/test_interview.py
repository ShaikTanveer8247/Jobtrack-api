from app.models import Application, Interview, User

from datetime import datetime, timedelta

from app.models import Application


def test_get_upcoming_interviews(client, db_session):
    application = Application(
        user_id=1,
        company="Amazon",
        role="Backend Intern",
        status="Interview",
    )

    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)

    future_date = datetime.now() + timedelta(days=7)

    create_response = client.post(
        "/api/v1/interviews/",
        json={
            "application_id": application.id,
            "round": "Technical",
            "interview_date": future_date.isoformat(),
            "notes": "Upcoming technical interview",
            "result": "Pending",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/api/v1/interviews/upcoming")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["application_id"] == application.id
    assert data[0]["round"] == "Technical"
    assert data[0]["result"] == "Pending"

def test_create_interview(client, db_session):
    application = Application(
        user_id=1,
        company="Google",
        role="Backend Intern",
        status="Interview",
    )

    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)

    response = client.post(
        "/api/v1/interviews/",
        json={
            "application_id": application.id,
            "round": "Technical",
            "interview_date": "2026-09-25T10:30:00",
            "notes": "Python and FastAPI",
            "result": "Pending",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["application_id"] == application.id
    assert data["round"] == "Technical"
    assert data["result"] == "Pending"


def test_get_interviews(client, db_session):
    application = Application(
        user_id=1,
        company="Microsoft",
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
            "round": "HR",
            "interview_date": "2026-09-30T11:00:00",
            "notes": "HR discussion",
            "result": "Pending",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/api/v1/interviews")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["round"] == "HR"

def test_user_cannot_access_another_users_interview(
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
        role="Backend Intern",
        status="Interview",
    )

    db_session.add(other_application)
    db_session.commit()
    db_session.refresh(other_application)

    other_interview = Interview(
        application_id=other_application.id,
        round="Technical",
        interview_date=datetime(2026, 9, 25, 10, 30),
        notes="Private interview",
        result="Pending",
    )

    db_session.add(other_interview)
    db_session.commit()
    db_session.refresh(other_interview)

    response = client.get(
        f"/api/v1/interviews/{other_interview.id}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"

def test_user_cannot_update_another_users_interview(
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
        role="Backend Intern",
        status="Interview",
    )

    db_session.add(other_application)
    db_session.commit()
    db_session.refresh(other_application)

    other_interview = Interview(
        application_id=other_application.id,
        round="Technical",
        interview_date=datetime(2026, 9, 25, 10, 30),
        notes="Private interview",
        result="Pending",
    )

    db_session.add(other_interview)
    db_session.commit()
    db_session.refresh(other_interview)

    response = client.put(
        f"/api/v1/interviews/{other_interview.id}",
        json={
            "round": "HR",
        },
    )

    assert response.status_code == 404