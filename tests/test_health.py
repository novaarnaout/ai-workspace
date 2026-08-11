import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://postgres:postgres@localhost:5433/ai_workspace"
)

from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import ALGORITHM, SECRET_KEY

client = TestClient(app)


def unique_email():
    return f"auth-test-{uuid.uuid4().hex[:8]}@example.com"


def create_user():
    email = unique_email()
    password = "Test123!"

    response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Auth Test User",
            "password": password,
        },
    )

    assert response.status_code == 200

    return {
        "email": email,
        "password": password,
        "user": response.json(),
    }


def login(email: str, password: str):
    return client.post(
        "/auth/login",
        json={
            "email": email,
            "name": "Auth Test User",
            "password": password,
        },
    )


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_users_requires_authentication():
    response = client.get("/users/")

    assert response.status_code == 401


def test_login():
    user = create_user()

    response = login(
        user["email"],
        user["password"],
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    user = create_user()

    response = login(
        user["email"],
        "WrongPassword123!",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_email():
    response = login(
        unique_email(),
        "Test123!",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_authenticated_users():
    user = create_user()

    login_response = login(
        user["email"],
        user["password"],
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_token():
    response = client.get(
        "/users/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_missing_bearer_token():
    response = client.get(
        "/users/",
        headers={
            "Authorization": "invalid-token",
        },
    )

    assert response.status_code == 401


def test_expired_token():
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401


def test_token_with_invalid_signature():
    invalid_signature_token = jwt.encode(
        {
            "sub": "1",
        },
        "wrong-secret-key",
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {invalid_signature_token}",
        },
    )

    assert response.status_code == 401