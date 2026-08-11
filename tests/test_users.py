import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def login(email: str, password: str):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "name": "Test User",
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_create_user():
    email = unique_email()

    response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Test User",
            "password": "Test123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == email
    assert data["name"] == "Test User"
    assert "id" in data


def test_duplicate_email():
    email = unique_email()

    first_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "First User",
            "password": "Test123!",
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Second User",
            "password": "Test123!",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already exists"


def test_users_requires_authentication():
    response = client.get("/users/")

    assert response.status_code == 401


def test_get_current_user_profile():
    email = unique_email()

    create_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Profile User",
            "password": "Test123!",
        },
    )

    assert create_response.status_code == 200

    user = create_response.json()

    token = login(email, "Test123!")

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user["id"]
    assert data["email"] == email
    assert data["name"] == "Profile User"


def test_get_user_by_id():
    email = unique_email()

    create_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Get User",
            "password": "Test123!",
        },
    )

    assert create_response.status_code == 200

    user = create_response.json()

    token = login(email, "Test123!")

    response = client.get(
        f"/users/{user['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user["id"]
    assert data["email"] == email


def test_get_nonexistent_user():
    email = unique_email()

    create_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Not Found User",
            "password": "Test123!",
        },
    )

    assert create_response.status_code == 200

    token = login(email, "Test123!")

    response = client.get(
        "/users/999999999",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_own_user():
    email = unique_email()

    create_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Old Name",
            "password": "Test123!",
        },
    )

    assert create_response.status_code == 200

    user = create_response.json()

    token = login(email, "Test123!")

    new_email = unique_email()

    response = client.put(
        f"/users/{user['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "New Name",
            "email": new_email,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user["id"]
    assert data["name"] == "New Name"
    assert data["email"] == new_email


def test_cannot_update_another_user():
    email1 = unique_email()
    email2 = unique_email()

    user1_response = client.post(
        "/users/",
        json={
            "email": email1,
            "name": "User One",
            "password": "Test123!",
        },
    )

    user2_response = client.post(
        "/users/",
        json={
            "email": email2,
            "name": "User Two",
            "password": "Test123!",
        },
    )

    assert user1_response.status_code == 200
    assert user2_response.status_code == 200

    user1 = user1_response.json()
    user2 = user2_response.json()

    token = login(email1, "Test123!")

    response = client.put(
        f"/users/{user2['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Hacked Name",
            "email": unique_email(),
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only update your own account"


def test_delete_own_user():
    email = unique_email()

    create_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "Delete User",
            "password": "Test123!",
        },
    )

    assert create_response.status_code == 200

    user = create_response.json()

    token = login(email, "Test123!")

    response = client.delete(
        f"/users/{user['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_cannot_delete_another_user():
    email1 = unique_email()
    email2 = unique_email()

    user1_response = client.post(
        "/users/",
        json={
            "email": email1,
            "name": "Delete User One",
            "password": "Test123!",
        },
    )

    user2_response = client.post(
        "/users/",
        json={
            "email": email2,
            "name": "Delete User Two",
            "password": "Test123!",
        },
    )

    assert user1_response.status_code == 200
    assert user2_response.status_code == 200

    user1 = user1_response.json()
    user2 = user2_response.json()

    token = login(email1, "Test123!")

    response = client.delete(
        f"/users/{user2['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only delete your own account"


def test_authenticated_users():
    email = unique_email()

    create_response = client.post(
        "/users/",
        json={
            "email": email,
            "name": "List User",
            "password": "Test123!",
        },
    )

    assert create_response.status_code == 200

    token = login(email, "Test123!")

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)