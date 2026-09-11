def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst@test.com", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "analyst@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@test.com", "password": "password123", "role": "analyst"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
