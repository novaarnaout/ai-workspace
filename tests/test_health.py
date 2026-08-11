from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_users_requires_authentication():
    response = client.get("/users/")

    assert response.status_code == 401


def test_login():
    response = client.post(
        "/auth/login",
        json={
            "email": "password-test@example.com",
            "name": "Password Test",
            "password": "Test123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_authenticated_users():
    login_response = client.post(
        "/auth/login",
        json={
            "email": "password-test@example.com",
            "name": "Password Test",
            "password": "Test123!",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)