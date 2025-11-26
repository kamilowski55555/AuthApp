"""
Integration tests for the /users endpoint
"""
import pytest
from fastapi.testclient import TestClient


class TestUsersEndpoint:

    def test_get_users_with_valid_token(self, client, admin_user, admin_token):
        # Given: An admin user with valid authentication token

        # When: Requesting all users list
        response = client.get(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Then: Should return list of all users
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["username"] == "admin"
        assert data[0]["email"] == "admin@test.com"
        assert "ROLE_ADMIN" in data[0]["roles"]

    def test_get_users_without_token(self, client, admin_user):
        # Given: No authentication token provided

        # When: Requesting all users list
        response = client.get("/users")

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] == "Authorization header missing"

    def test_get_users_with_invalid_token(self, client, admin_user):
        # Given: An invalid authentication token

        # When: Requesting all users list with invalid token
        response = client.get(
            "/users",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_get_users_with_malformed_header(self, client, admin_user):
        # Given: A malformed Authorization header

        # When: Requesting all users list with malformed header
        response = client.get(
            "/users",
            headers={"Authorization": "InvalidFormat token123"}
        )

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    def test_create_user_with_admin_permission(self, client, admin_user, admin_token):
        # Given: An admin user with valid token and new user data
        new_user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "newpass123",
            "roles": ["ROLE_USER"]
        }

        # When: Creating a new user with admin permissions
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=new_user_data
        )

        # Then: User should be created successfully
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert data["roles"] == ["ROLE_USER"]
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_create_user_without_admin_permission(self, client, admin_user, regular_user, user_token):
        # Given: A regular user without admin role
        new_user_data = {
            "username": "unauthorized",
            "email": "unauthorized@test.com",
            "password": "pass123",
            "roles": ["ROLE_USER"]
        }

        # When: Attempting to create a user without admin permissions
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {user_token}"},
            json=new_user_data
        )

        # Then: Should fail with 403 Forbidden
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"

    def test_create_user_without_token(self, client):
        # Given: No authentication token provided
        new_user_data = {
            "username": "noauth",
            "email": "noauth@test.com",
            "password": "pass123",
            "roles": ["ROLE_USER"]
        }

        # When: Attempting to create a user without token
        response = client.post("/users", json=new_user_data)

        # Then: Should fail with 401 Unauthorized
        assert response.status_code == 401
        assert response.json()["detail"] == "Authorization header missing"

    def test_create_user_with_duplicate_username(self, client, admin_user, admin_token):
        # Given: An admin user and an existing username in resources
        duplicate_user_data = {
            "username": "admin",
            "email": "different@test.com",
            "password": "pass123",
            "roles": ["ROLE_USER"]
        }

        # When: Attempting to create user with duplicate username
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=duplicate_user_data
        )

        # Then: Should fail with 400 Bad Request
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already exists"

    def test_create_user_with_duplicate_email(self, client, admin_user, admin_token):
        # Given: An admin user and an existing email in resources
        duplicate_email_data = {
            "username": "differentuser",
            "email": "admin@test.com",
            "password": "pass123",
            "roles": ["ROLE_USER"]
        }

        # When: Attempting to create user with duplicate email
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=duplicate_email_data
        )

        # Then: Should fail with 400 Bad Request
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already exists"

    def test_create_user_with_missing_fields(self, client, admin_token):
        # Given: Incomplete user data without required fields
        incomplete_data = {
            "username": "incomplete"
        }

        # When: Attempting to create user with missing required fields
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=incomplete_data
        )

        # Then: Should fail with 422 validation error
        assert response.status_code == 422

    def test_create_user_with_empty_roles(self, client, admin_user, admin_token):
        # Given: User data with empty roles list
        user_data = {
            "username": "noroles",
            "email": "noroles@test.com",
            "password": "pass123",
            "roles": []
        }

        # When: Creating user with empty roles
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=user_data
        )

        # Then: User should be created with empty roles
        assert response.status_code == 200
        data = response.json()
        assert data["roles"] == []

    def test_create_user_without_roles_field(self, client, admin_user, admin_token):
        # Given: User data without roles field
        user_data = {
            "username": "defaultroles",
            "email": "defaultroles@test.com",
            "password": "pass123"
        }

        # When: Creating user without specifying roles
        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=user_data
        )

        # Then: User should be created with default empty roles
        assert response.status_code == 200
        data = response.json()
        assert data["roles"] == []
