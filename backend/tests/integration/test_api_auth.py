"""
Integration tests for authentication API endpoints (app/api/v1/auth.py).

Tests:
    - POST /api/v1/auth/login (OAuth2 form)
    - POST /api/v1/auth/login/json (JSON credentials)
    - GET /api/v1/auth/me (current user)
    - POST /api/v1/auth/refresh (token refresh)
    - POST /api/v1/auth/logout
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


class TestAuthLogin:
    """Test login endpoints."""

    def test_login_with_valid_credentials_oauth2_form(self, client: TestClient, test_admin_user: User):
        """Test successful login with OAuth2 form data."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test_admin",
                "password": "AdminPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["username"] == "test_admin"
        assert data["user"]["role"] == "ADMIN"

    def test_login_with_valid_credentials_json(self, client: TestClient, test_manager_user: User):
        """Test successful login with JSON body."""
        response = client.post(
            "/api/v1/auth/login/json",
            json={
                "username": "test_manager",
                "password": "ManagerPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "test_manager"
        assert data["user"]["role"] == "MANAGER"

    def test_login_with_wrong_password(self, client: TestClient, test_operator_user: User):
        """Test login fails with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test_operator",
                "password": "WrongPassword!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_with_nonexistent_username(self, client: TestClient):
        """Test login fails with nonexistent username."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent_user",
                "password": "AnyPassword123!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_with_inactive_user(self, client: TestClient, test_inactive_user: User):
        """Test login fails for inactive user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test_inactive",
                "password": "InactivePass123!",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user account"

    def test_login_username_case_insensitive(self, client: TestClient, test_admin_user: User):
        """Test login is case-insensitive for username."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "TEST_ADMIN",  # Uppercase
                "password": "AdminPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "test_admin"  # Stored as lowercase

    def test_login_returns_user_info(self, client: TestClient, test_admin_user: User):
        """Test login response includes user information."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test_admin",
                "password": "AdminPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        user_info = data["user"]

        assert user_info["id"] == test_admin_user.id
        assert user_info["username"] == test_admin_user.username
        assert user_info["email"] == test_admin_user.email
        assert user_info["full_name"] == test_admin_user.full_name
        assert user_info["role"] == test_admin_user.role.value
        assert "password" not in user_info  # Password should never be in response


class TestAuthMe:
    """Test current user endpoint."""

    def test_get_current_user_with_valid_token(self, client: TestClient, auth_headers_admin: dict, test_admin_user: User):
        """Test retrieving current user with valid token."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_admin_user.id
        assert data["username"] == test_admin_user.username
        assert data["email"] == test_admin_user.email
        assert data["role"] == "ADMIN"

    def test_get_current_user_without_token(self, client: TestClient):
        """Test /me endpoint fails without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_get_current_user_with_invalid_token(self, client: TestClient):
        """Test /me endpoint fails with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_get_current_user_with_inactive_account(self, client: TestClient, auth_headers_inactive: dict):
        """Test /me endpoint fails for inactive user."""
        response = client.get("/api/v1/auth/me", headers=auth_headers_inactive)

        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user account"

    def test_get_current_user_different_roles(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        auth_headers_manager: dict,
        auth_headers_operator: dict
    ):
        """Test /me endpoint works for all role types."""
        # Admin
        response_admin = client.get("/api/v1/auth/me", headers=auth_headers_admin)
        assert response_admin.status_code == 200
        assert response_admin.json()["role"] == "ADMIN"

        # Manager
        response_manager = client.get("/api/v1/auth/me", headers=auth_headers_manager)
        assert response_manager.status_code == 200
        assert response_manager.json()["role"] == "MANAGER"

        # Operator
        response_operator = client.get("/api/v1/auth/me", headers=auth_headers_operator)
        assert response_operator.status_code == 200
        assert response_operator.json()["role"] == "OPERATOR"


class TestAuthRefresh:
    """Test token refresh endpoint."""

    def test_refresh_token_with_valid_token(self, client: TestClient, auth_headers_admin: dict):
        """Test refreshing token with valid existing token."""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_refresh_token_without_token(self, client: TestClient):
        """Test refresh fails without token."""
        response = client.post("/api/v1/auth/refresh")

        assert response.status_code == 401

    def test_refresh_token_with_invalid_token(self, client: TestClient):
        """Test refresh fails with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_refreshed_token_is_valid(self, client: TestClient, auth_headers_admin: dict):
        """Test that refreshed token can be used for authentication."""
        # Get refreshed token
        refresh_response = client.post("/api/v1/auth/refresh", headers=auth_headers_admin)
        assert refresh_response.status_code == 200

        new_token = refresh_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        # Use refreshed token to access protected endpoint
        me_response = client.get("/api/v1/auth/me", headers=new_headers)
        assert me_response.status_code == 200

    def test_refresh_token_for_different_roles(
        self,
        client: TestClient,
        auth_headers_admin: dict,
        auth_headers_manager: dict,
        auth_headers_operator: dict
    ):
        """Test token refresh works for all roles."""
        for headers in [auth_headers_admin, auth_headers_manager, auth_headers_operator]:
            response = client.post("/api/v1/auth/refresh", headers=headers)
            assert response.status_code == 200
            assert "access_token" in response.json()


class TestAuthLogout:
    """Test logout endpoint."""

    def test_logout_with_valid_token(self, client: TestClient, auth_headers_admin: dict):
        """Test logout with valid token."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers_admin)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower()

    def test_logout_without_token(self, client: TestClient):
        """Test logout fails without token."""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401

    def test_logout_with_invalid_token(self, client: TestClient):
        """Test logout fails with invalid token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


class TestAuthFlow:
    """Integration tests for complete authentication flow."""

    def test_complete_auth_flow(self, client: TestClient, test_admin_user: User):
        """Test complete authentication flow: login -> access protected -> refresh -> logout."""
        # Step 1: Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test_admin",
                "password": "AdminPass123!",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Access protected endpoint
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "test_admin"

        # Step 3: Refresh token
        refresh_response = client.post("/api/v1/auth/refresh", headers=headers)
        assert refresh_response.status_code == 200
        new_token = refresh_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        # Step 4: Use refreshed token
        me_response2 = client.get("/api/v1/auth/me", headers=new_headers)
        assert me_response2.status_code == 200

        # Step 5: Logout
        logout_response = client.post("/api/v1/auth/logout", headers=new_headers)
        assert logout_response.status_code == 200

    def test_multiple_concurrent_logins(self, client: TestClient, test_admin_user: User, test_manager_user: User):
        """Test multiple users can login simultaneously."""
        # Admin login
        admin_login = client.post(
            "/api/v1/auth/login",
            data={"username": "test_admin", "password": "AdminPass123!"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]

        # Manager login
        manager_login = client.post(
            "/api/v1/auth/login",
            data={"username": "test_manager", "password": "ManagerPass123!"},
        )
        assert manager_login.status_code == 200
        manager_token = manager_login.json()["access_token"]

        # Both tokens should be valid and distinct
        assert admin_token != manager_token

        # Both can access /me endpoint
        admin_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        manager_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {manager_token}"}
        )

        assert admin_me.status_code == 200
        assert manager_me.status_code == 200
        assert admin_me.json()["role"] == "ADMIN"
        assert manager_me.json()["role"] == "MANAGER"

    @pytest.mark.parametrize("endpoint", [
        "/api/v1/auth/me",
        "/api/v1/auth/refresh",
        "/api/v1/auth/logout",
    ])
    def test_protected_endpoints_require_auth(self, client: TestClient, endpoint: str):
        """Test that protected endpoints require authentication."""
        response = client.get(endpoint) if endpoint == "/api/v1/auth/me" else client.post(endpoint)
        assert response.status_code == 401
