def test_register_user(auth_client):
    response = auth_client.post(
        "/users/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_user_registration(auth_client):
    user = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
    }

    first_response = auth_client.post(
        "/users/register",
        json=user,
    )

    assert first_response.status_code == 201

    second_response = auth_client.post(
        "/users/register",
        json=user,
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "A user with this email already exists"
    )


def test_login_user(auth_client):
    auth_client.post(
        "/users/register",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )

    response = auth_client.post(
        "/users/login",
        data={
            "username": "login@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_login(auth_client):
    response = auth_client.post(
        "/users/login",
        data={
            "username": "missing@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_protected_route_requires_authentication(auth_client):
    response = auth_client.get("/applications")

    assert response.status_code == 401


def test_authenticated_user_can_access_protected_route(auth_client):
    auth_client.post(
        "/users/register",
        json={
            "email": "protected@example.com",
            "password": "securepassword123",
        },
    )

    login_response = auth_client.post(
        "/users/login",
        data={
            "username": "protected@example.com",
            "password": "securepassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = auth_client.get(
        "/applications",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200