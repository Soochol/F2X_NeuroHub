"""
Integration tests for users API endpoints (app/api/v1/users.py).

Tests:
    - GET /api/v1/users/ (list users with pagination and filters)
    - GET /api/v1/users/{id}
    - GET /api/v1/users/username/{username}
    - GET /api/v1/users/email/{email}
    - GET /api/v1/users/role/{role}
    - POST /api/v1/users/ (create user)
    - PUT /api/v1/users/{id} (update user)
    - DELETE /api/v1/users/{id}
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, UserRole


class TestListUsers:
    """Test GET /api/v1/users/ endpoint."""

    def test_list_all_users(
        self,
        client: TestClient,
        db: Session,
        test_admin_user: User,
        test_manager_user: User,
        test_operator_user: User
    ):
        """Test listing all users."""
        response = client.get("/api/v1/users/")

        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 3  # At least our test users

    def test_list_users_with_pagination(self, client: TestClient, db: Session):
        """Test user listing with pagination."""
        response = client.get("/api/v1/users/?skip=0&limit=2")

        assert response.status_code == 200
        users = response.json()
        assert len(users) <= 2

    def test_list_users_filter_by_role(
        self,
        client: TestClient,
        test_admin_user: User,
        test_operator_user: User
    ):
        """Test filtering users by role."""
        response = client.get("/api/v1/users/?role=ADMIN")

        assert response.status_code == 200
        users = response.json()
        assert all(u["role"] == "ADMIN" for u in users)
        assert any(u["id"] == test_admin_user.id for u in users)

    def test_list_users_filter_by_active_status(
        self,
        client: TestClient,
        test_inactive_user: User
    ):
        """Test filtering users by active status."""
        # Get active users
        active_response = client.get("/api/v1/users/?is_active=true")
        assert active_response.status_code == 200
        active_users = active_response.json()
        assert all(u["is_active"] for u in active_users)

        # Get inactive users
        inactive_response = client.get("/api/v1/users/?is_active=false")
        assert inactive_response.status_code == 200
        inactive_users = inactive_response.json()
        assert not any(u["is_active"] for u in inactive_users)
        assert any(u["id"] == test_inactive_user.id for u in inactive_users)


class TestGetUserById:
    """Test GET /api/v1/users/{id} endpoint."""

    def test_get_user_by_id_success(self, client: TestClient, test_admin_user: User):
        """Test retrieving user by valid ID."""
        response = client.get(f"/api/v1/users/{test_admin_user.id}")

        assert response.status_code == 200
        user = response.json()
        assert user["id"] == test_admin_user.id
        assert user["username"] == test_admin_user.username
        assert user["email"] == test_admin_user.email
        assert "password_hash" not in user  # Password should not be exposed

    def test_get_user_by_id_not_found(self, client: TestClient):
        """Test retrieving nonexistent user returns 404."""
        response = client.get("/api/v1/users/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetUserByUsername:
    """Test GET /api/v1/users/username/{username} endpoint."""

    def test_get_user_by_username_success(self, client: TestClient, test_manager_user: User):
        """Test retrieving user by username."""
        response = client.get(f"/api/v1/users/username/{test_manager_user.username}")

        assert response.status_code == 200
        user = response.json()
        assert user["username"] == test_manager_user.username
        assert user["id"] == test_manager_user.id

    def test_get_user_by_username_not_found(self, client: TestClient):
        """Test retrieving user by nonexistent username returns 404."""
        response = client.get("/api/v1/users/username/nonexistent_user")

        assert response.status_code == 404


class TestGetUserByEmail:
    """Test GET /api/v1/users/email/{email} endpoint."""

    def test_get_user_by_email_success(self, client: TestClient, test_operator_user: User):
        """Test retrieving user by email."""
        response = client.get(f"/api/v1/users/email/{test_operator_user.email}")

        assert response.status_code == 200
        user = response.json()
        assert user["email"] == test_operator_user.email
        assert user["id"] == test_operator_user.id

    def test_get_user_by_email_not_found(self, client: TestClient):
        """Test retrieving user by nonexistent email returns 404."""
        response = client.get("/api/v1/users/email/nonexistent@test.com")

        assert response.status_code == 404


class TestGetUsersByRole:
    """Test GET /api/v1/users/role/{role} endpoint."""

    def test_get_users_by_role_admin(self, client: TestClient, test_admin_user: User):
        """Test getting users with ADMIN role."""
        response = client.get("/api/v1/users/role/ADMIN")

        assert response.status_code == 200
        users = response.json()
        assert all(u["role"] == "ADMIN" for u in users)
        assert any(u["id"] == test_admin_user.id for u in users)

    def test_get_users_by_role_manager(self, client: TestClient, test_manager_user: User):
        """Test getting users with MANAGER role."""
        response = client.get("/api/v1/users/role/MANAGER")

        assert response.status_code == 200
        users = response.json()
        assert all(u["role"] == "MANAGER" for u in users)

    def test_get_users_by_role_operator(self, client: TestClient, test_operator_user: User):
        """Test getting users with OPERATOR role."""
        response = client.get("/api/v1/users/role/OPERATOR")

        assert response.status_code == 200
        users = response.json()
        assert all(u["role"] == "OPERATOR" for u in users)

    def test_get_users_by_role_with_pagination(self, client: TestClient):
        """Test pagination in role-based user listing."""
        response = client.get("/api/v1/users/role/OPERATOR?skip=0&limit=2")

        assert response.status_code == 200
        users = response.json()
        assert len(users) <= 2


class TestCreateUser:
    """Test POST /api/v1/users/ endpoint."""

    def test_create_user_with_valid_data(self, client: TestClient):
        """Test creating a new user with valid data."""
        user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "NewUserPass123!",
            "full_name": "New User",
            "role": "OPERATOR",
            "department": "Manufacturing",
            "is_active": True,
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 201
        created_user = response.json()
        assert created_user["username"] == "newuser"
        assert created_user["email"] == "newuser@test.com"
        assert created_user["role"] == "OPERATOR"
        assert "password" not in created_user  # Password should not be returned
        assert "id" in created_user

    def test_create_user_with_duplicate_username(
        self,
        client: TestClient,
        test_admin_user: User
    ):
        """Test creating user with duplicate username fails."""
        user_data = {
            "username": "test_admin",  # Duplicate
            "email": "unique@test.com",
            "password": "Password123!",
            "full_name": "Duplicate Username",
            "role": "OPERATOR",
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_create_user_with_duplicate_email(
        self,
        client: TestClient,
        test_admin_user: User
    ):
        """Test creating user with duplicate email fails."""
        user_data = {
            "username": "uniqueuser",
            "email": "admin@test.com",  # Duplicate
            "password": "Password123!",
            "full_name": "Duplicate Email",
            "role": "OPERATOR",
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_create_admin_user(self, client: TestClient):
        """Test creating user with ADMIN role."""
        user_data = {
            "username": "newadmin",
            "email": "newadmin@test.com",
            "password": "AdminPass123!",
            "full_name": "New Admin",
            "role": "ADMIN",
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 201
        assert response.json()["role"] == "ADMIN"


class TestUpdateUser:
    """Test PUT /api/v1/users/{id} endpoint."""

    def test_update_user_full_name(self, client: TestClient, test_operator_user: User):
        """Test updating user's full name."""
        update_data = {"full_name": "Updated Full Name"}

        response = client.put(
            f"/api/v1/users/{test_operator_user.id}",
            json=update_data
        )

        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["full_name"] == "Updated Full Name"
        assert updated_user["username"] == test_operator_user.username  # Unchanged

    def test_update_user_department(self, client: TestClient, test_operator_user: User):
        """Test updating user's department."""
        update_data = {"department": "Quality Assurance"}

        response = client.put(
            f"/api/v1/users/{test_operator_user.id}",
            json=update_data
        )

        assert response.status_code == 200
        assert response.json()["department"] == "Quality Assurance"

    def test_update_user_role(self, client: TestClient, test_operator_user: User):
        """Test updating user's role."""
        update_data = {"role": "MANAGER"}

        response = client.put(
            f"/api/v1/users/{test_operator_user.id}",
            json=update_data
        )

        assert response.status_code == 200
        assert response.json()["role"] == "MANAGER"

    def test_update_user_is_active(self, client: TestClient, test_operator_user: User):
        """Test deactivating user account."""
        update_data = {"is_active": False}

        response = client.put(
            f"/api/v1/users/{test_operator_user.id}",
            json=update_data
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_update_nonexistent_user(self, client: TestClient):
        """Test updating nonexistent user returns 404."""
        update_data = {"full_name": "Test"}

        response = client.put("/api/v1/users/99999", json=update_data)

        assert response.status_code == 404

    def test_update_username_to_existing(
        self,
        client: TestClient,
        test_operator_user: User,
        test_admin_user: User
    ):
        """Test updating username to existing one fails."""
        update_data = {"username": "test_admin"}  # Existing username

        response = client.put(
            f"/api/v1/users/{test_operator_user.id}",
            json=update_data
        )

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()


class TestDeleteUser:
    """Test DELETE /api/v1/users/{id} endpoint."""

    def test_delete_existing_user(self, client: TestClient, db: Session):
        """Test deleting an existing user."""
        # Create user to delete
        from app.crud import user as user_crud
        from app.schemas import UserCreate

        user_data = UserCreate(
            username="to_delete",
            email="delete@test.com",
            password="Password123!",
            full_name="Delete Me",
            role=UserRole.OPERATOR,
        )
        user = user_crud.create(db, user_in=user_data)
        db.commit()

        # Delete user
        response = client.delete(f"/api/v1/users/{user.id}")

        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(f"/api/v1/users/{user.id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_user(self, client: TestClient):
        """Test deleting nonexistent user returns 404."""
        response = client.delete("/api/v1/users/99999")

        assert response.status_code == 404


class TestUsersWorkflow:
    """Integration tests for complete user management workflows."""

    def test_complete_user_lifecycle(self, client: TestClient):
        """Test complete user lifecycle: create -> read -> update -> delete."""
        # Create user
        create_data = {
            "username": "lifecycle_user",
            "email": "lifecycle@test.com",
            "password": "Password123!",
            "full_name": "Lifecycle User",
            "role": "OPERATOR",
        }
        create_response = client.post("/api/v1/users/", json=create_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Read user
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["username"] == "lifecycle_user"

        # Update user
        update_data = {"full_name": "Updated Lifecycle User", "role": "MANAGER"}
        update_response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["full_name"] == "Updated Lifecycle User"
        assert update_response.json()["role"] == "MANAGER"

        # Delete user
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        final_get = client.get(f"/api/v1/users/{user_id}")
        assert final_get.status_code == 404

    @pytest.mark.parametrize("role", ["ADMIN", "MANAGER", "OPERATOR"])
    def test_create_users_with_all_roles(self, client: TestClient, role: str):
        """Test creating users with all possible roles."""
        user_data = {
            "username": f"test_{role.lower()}",
            "email": f"{role.lower()}@role.test",
            "password": "Password123!",
            "full_name": f"Test {role}",
            "role": role,
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 201
        assert response.json()["role"] == role
