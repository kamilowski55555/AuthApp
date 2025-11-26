"""
Integration tests for the /user_jwt endpoint (user_details)
"""
import pytest
from fastapi.testclient import TestClient


class TestUserDetailsEndpoint:

    def test_get_user_details_with_valid_token(self, client, admin_user, admin_token):
        # Given: An admin user with valid authentication token

        # When: Requesting user details from JWT
        response = client.get(
            "/user_jwt",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Then: Should return user details from token payload
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert "ROLE_ADMIN" in data["roles"]
        assert "ROLE_USER" in data["roles"]
        assert "iat" in data
        assert "exp" in data

    def test_get_user_details_with_regular_user_token(self, client, regular_user, user_token):
        # Given: A regular user with valid authentication token

        # When: Requesting user details from JWT
        response = client.get(
            "/user_jwt",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        # Then: Should return user details with regular user roles
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "user"
        assert "ROLE_USER" in data["roles"]
        assert "ROLE_ADMIN" not in data["roles"]

    def test_get_user_details_without_token(self, client):
        # Given: No authentication token provided

        # When: Requesting user details without token
        response = client.get("/user_jwt")

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] == "Authorization header missing"

    def test_get_user_details_with_invalid_token(self, client):
        # Given: An invalid authentication token

        # When: Requesting user details with invalid token
        response = client.get(
            "/user_jwt",
            headers={"Authorization": "Bearer invalid_token_abc123"}
        )

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_get_user_details_with_malformed_header(self, client):
        # Given: A malformed Authorization header

        # When: Requesting user details with malformed header
        response = client.get(
            "/user_jwt",
            headers={"Authorization": "NotBearer sometoken"}
        )

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    def test_get_user_details_with_empty_token(self, client):
        # Given: An empty token in Authorization header

        # When: Requesting user details with empty token
        response = client.get(
            "/user_jwt",
            headers={"Authorization": "Bearer "}
        )

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401

    def test_get_user_details_token_contains_correct_claims(self, client, admin_user, admin_token):
        # Given: An admin user with valid authentication token

        # When: Requesting user details from JWT
        response = client.get(
            "/user_jwt",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Then: Response should contain all expected JWT claims
        assert response.status_code == 200
        data = response.json()

        required_fields = ["username", "roles", "iat", "exp"]
        for field in required_fields:
            assert field in data, f"Field '{field}' is missing from response"

        assert isinstance(data["iat"], str)
        assert isinstance(data["exp"], str)
        assert isinstance(data["roles"], list)
