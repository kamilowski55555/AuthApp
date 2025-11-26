"""
Integration tests for the /login endpoint
"""
import pytest
from fastapi.testclient import TestClient


class TestLoginEndpoint:

    def test_successful_login_with_admin(self, client, admin_user):
        # Given: An admin user exists in the resources

        # When: Logging in with valid admin credentials
        response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )

        # Then: Login should succeed and return a valid JWT token
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_successful_login_with_regular_user(self, client, regular_user):
        # Given: A regular user exists in the resources

        # When: Logging in with valid user credentials
        response = client.post(
            "/login",
            json={"username": "user", "password": "user123"}
        )

        # Then: Login should succeed and return a valid JWT token
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_with_invalid_username(self, client):
        # Given: No user exists with the given username

        # When: Attempting to login with non-existent username
        response = client.post(
            "/login",
            json={"username": "nonexistent", "password": "password123"}
        )

        # Then: Login should fail with 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_with_invalid_password(self, client, admin_user):
        # Given: An admin user exists in the resources

        # When: Attempting to login with incorrect password
        response = client.post(
            "/login",
            json={"username": "admin", "password": "wrongpassword"}
        )

        # Then: Login should fail with 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_with_missing_username(self, client):
        # Given: Login request data without username field

        # When: Attempting to login with missing username
        response = client.post(
            "/login",
            json={"password": "admin123"}
        )

        # Then: Request should fail with 422 validation error
        assert response.status_code == 422

    def test_login_with_missing_password(self, client):
        # Given: Login request data without password field

        # When: Attempting to login with missing password
        response = client.post(
            "/login",
            json={"username": "admin"}
        )

        # Then: Request should fail with 422 validation error
        assert response.status_code == 422

    def test_login_with_empty_credentials(self, client):
        # Given: Login request with empty username and password

        # When: Attempting to login with empty credentials
        response = client.post(
            "/login",
            json={"username": "", "password": ""}
        )

        # Then: Login should fail with 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
