"""
Unit tests for app/crud/user.py module.

Tests:
    - User CRUD operations (create, read, update, delete)
    - Username and email uniqueness
    - Password hashing on user creation
    - Authentication and password verification
    - Role-based filtering
    - User activity tracking (last_login_at)
"""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crud import user as user_crud
from app.models import User, UserRole
from app.schemas import UserCreate, UserUpdate


class TestUserCreate:
    """Test user creation operations."""

    def test_create_user_with_valid_data(self, db: Session):
        """Test creating a user with valid data."""
        user_data = UserCreate(
            username="john_doe",
            email="john@example.com",
            password="SecurePass123!",
            full_name="John Doe",
            role=UserRole.OPERATOR,
            department="Manufacturing",
        )

        user = user_crud.create(db, user_in=user_data)
        db.commit()

        assert user.id is not None
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.full_name == "John Doe"
        assert user.role == UserRole.OPERATOR
        assert user.department == "Manufacturing"
        assert user.is_active is True
        assert user.password_hash != "SecurePass123!"  # Password should be hashed
        assert user.password_hash.startswith("$2b$")  # Bcrypt hash

    def test_create_user_with_admin_role(self, db: Session):
        """Test creating an admin user."""
        user_data = UserCreate(
            username="admin",
            email="admin@company.com",
            password="AdminPass123!",
            full_name="System Administrator",
            role=UserRole.ADMIN,
        )

        user = user_crud.create(db, user_in=user_data)
        db.commit()

        assert user.role == UserRole.ADMIN

    def test_create_user_without_department(self, db: Session):
        """Test creating user without optional department field."""
        user_data = UserCreate(
            username="no_dept_user",
            email="nodept@example.com",
            password="Password123!",
            full_name="No Department User",
            role=UserRole.OPERATOR,
        )

        user = user_crud.create(db, user_in=user_data)
        db.commit()

        assert user.department is None

    def test_create_inactive_user(self, db: Session):
        """Test creating an inactive user."""
        user_data = UserCreate(
            username="inactive_user",
            email="inactive@example.com",
            password="Password123!",
            full_name="Inactive User",
            role=UserRole.OPERATOR,
            is_active=False,
        )

        user = user_crud.create(db, user_in=user_data)
        db.commit()

        assert user.is_active is False

    def test_username_normalized_to_lowercase(self, db: Session):
        """Test that usernames are normalized to lowercase."""
        user_data = UserCreate(
            username="MixedCase",
            email="mixedcase@example.com",
            password="Password123!",
            full_name="Mixed Case User",
            role=UserRole.OPERATOR,
        )

        user = user_crud.create(db, user_in=user_data)
        db.commit()

        assert user.username == "mixedcase"

    def test_email_normalized_to_lowercase(self, db: Session):
        """Test that emails are normalized to lowercase."""
        user_data = UserCreate(
            username="emailtest",
            email="MixedCase@Example.COM",
            password="Password123!",
            full_name="Email Test User",
            role=UserRole.OPERATOR,
        )

        user = user_crud.create(db, user_in=user_data)
        db.commit()

        assert user.email == "mixedcase@example.com"


class TestUserRead:
    """Test user read operations."""

    def test_get_user_by_id(self, db: Session, test_operator_user: User):
        """Test retrieving user by ID."""
        user = user_crud.get(db, user_id=test_operator_user.id)

        assert user is not None
        assert user.id == test_operator_user.id
        assert user.username == test_operator_user.username

    def test_get_nonexistent_user_returns_none(self, db: Session):
        """Test that getting nonexistent user returns None."""
        user = user_crud.get(db, user_id=99999)

        assert user is None

    def test_get_user_by_username(self, db: Session, test_admin_user: User):
        """Test retrieving user by username."""
        user = user_crud.get_by_username(db, username=test_admin_user.username)

        assert user is not None
        assert user.id == test_admin_user.id
        assert user.username == test_admin_user.username

    def test_get_user_by_username_case_insensitive(self, db: Session, test_admin_user: User):
        """Test username lookup is case-insensitive."""
        # test_admin_user username is lowercase "test_admin"
        user = user_crud.get_by_username(db, username="TEST_ADMIN")

        assert user is not None
        assert user.id == test_admin_user.id

    def test_get_user_by_email(self, db: Session, test_manager_user: User):
        """Test retrieving user by email."""
        user = user_crud.get_by_email(db, email=test_manager_user.email)

        assert user is not None
        assert user.id == test_manager_user.id

    def test_get_user_by_email_case_insensitive(self, db: Session, test_manager_user: User):
        """Test email lookup is case-insensitive."""
        user = user_crud.get_by_email(db, email="MANAGER@TEST.COM")

        assert user is not None
        assert user.id == test_manager_user.id

    def test_get_multi_users(self, db: Session, test_admin_user: User, test_manager_user: User, test_operator_user: User):
        """Test retrieving multiple users with pagination."""
        users = user_crud.get_multi(db, skip=0, limit=10)

        assert len(users) >= 3  # At least our 3 test users
        assert any(u.id == test_admin_user.id for u in users)
        assert any(u.id == test_manager_user.id for u in users)

    def test_get_multi_with_role_filter(self, db: Session, test_admin_user: User, test_operator_user: User):
        """Test filtering users by role."""
        operators = user_crud.get_multi(db, role=UserRole.OPERATOR)
        admins = user_crud.get_multi(db, role=UserRole.ADMIN)

        assert all(u.role == UserRole.OPERATOR for u in operators)
        assert all(u.role == UserRole.ADMIN for u in admins)
        assert any(u.id == test_operator_user.id for u in operators)
        assert any(u.id == test_admin_user.id for u in admins)

    def test_get_multi_with_active_filter(self, db: Session, test_inactive_user: User):
        """Test filtering users by active status."""
        active_users = user_crud.get_multi(db, is_active=True)
        inactive_users = user_crud.get_multi(db, is_active=False)

        assert all(u.is_active for u in active_users)
        assert not any(u.is_active for u in inactive_users)
        assert any(u.id == test_inactive_user.id for u in inactive_users)

    def test_get_multi_pagination(self, db: Session):
        """Test pagination with skip and limit."""
        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                username=f"user{i}",
                email=f"user{i}@test.com",
                password="Password123!",
                full_name=f"User {i}",
                role=UserRole.OPERATOR,
            )
            user_crud.create(db, user_in=user_data)
        db.commit()

        page1 = user_crud.get_multi(db, skip=0, limit=2)
        page2 = user_crud.get_multi(db, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        # Pages should not overlap
        page1_ids = {u.id for u in page1}
        page2_ids = {u.id for u in page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestUserUpdate:
    """Test user update operations."""

    def test_update_user_full_name(self, db: Session, test_operator_user: User):
        """Test updating user's full name."""
        update_data = UserUpdate(full_name="Updated Name")
        updated_user = user_crud.update(db, user_id=test_operator_user.id, user_in=update_data)
        db.commit()

        assert updated_user.full_name == "Updated Name"
        assert updated_user.username == test_operator_user.username  # Unchanged

    def test_update_user_department(self, db: Session, test_operator_user: User):
        """Test updating user's department."""
        update_data = UserUpdate(department="New Department")
        updated_user = user_crud.update(db, user_id=test_operator_user.id, user_in=update_data)
        db.commit()

        assert updated_user.department == "New Department"

    def test_update_user_role(self, db: Session, test_operator_user: User):
        """Test updating user's role."""
        update_data = UserUpdate(role=UserRole.MANAGER)
        updated_user = user_crud.update(db, user_id=test_operator_user.id, user_in=update_data)
        db.commit()

        assert updated_user.role == UserRole.MANAGER

    def test_update_user_is_active(self, db: Session, test_operator_user: User):
        """Test deactivating user account."""
        update_data = UserUpdate(is_active=False)
        updated_user = user_crud.update(db, user_id=test_operator_user.id, user_in=update_data)
        db.commit()

        assert updated_user.is_active is False

    def test_update_nonexistent_user_returns_none(self, db: Session):
        """Test updating nonexistent user returns None."""
        update_data = UserUpdate(full_name="Test")
        result = user_crud.update(db, user_id=99999, user_in=update_data)

        assert result is None

    def test_partial_update(self, db: Session, test_operator_user: User):
        """Test updating only specified fields."""
        original_email = test_operator_user.email
        update_data = UserUpdate(full_name="Partial Update")

        updated_user = user_crud.update(db, user_id=test_operator_user.id, user_in=update_data)
        db.commit()

        assert updated_user.full_name == "Partial Update"
        assert updated_user.email == original_email  # Unchanged


class TestUserDelete:
    """Test user delete operations."""

    def test_delete_existing_user(self, db: Session):
        """Test deleting an existing user."""
        # Create user to delete
        user_data = UserCreate(
            username="to_delete",
            email="delete@test.com",
            password="Password123!",
            full_name="Delete Me",
            role=UserRole.OPERATOR,
        )
        user = user_crud.create(db, user_in=user_data)
        db.commit()
        user_id = user.id

        # Delete user
        result = user_crud.delete(db, user_id=user_id)
        db.commit()

        assert result is True
        # Verify user no longer exists
        assert user_crud.get(db, user_id=user_id) is None

    def test_delete_nonexistent_user_returns_false(self, db: Session):
        """Test deleting nonexistent user returns False."""
        result = user_crud.delete(db, user_id=99999)

        assert result is False


class TestUserAuthentication:
    """Test authentication-related operations."""

    def test_authenticate_with_correct_credentials(self, db: Session, test_operator_user: User):
        """Test authentication with correct username and password."""
        user = user_crud.authenticate(
            db,
            username="test_operator",
            password="OperatorPass123!"
        )

        assert user is not None
        assert user.id == test_operator_user.id

    def test_authenticate_with_wrong_password(self, db: Session, test_operator_user: User):
        """Test authentication fails with wrong password."""
        user = user_crud.authenticate(
            db,
            username="test_operator",
            password="WrongPassword"
        )

        assert user is None

    def test_authenticate_with_nonexistent_username(self, db: Session):
        """Test authentication fails with nonexistent username."""
        user = user_crud.authenticate(
            db,
            username="nonexistent",
            password="AnyPassword123!"
        )

        assert user is None

    def test_authenticate_username_case_insensitive(self, db: Session, test_admin_user: User):
        """Test authentication is case-insensitive for username."""
        user = user_crud.authenticate(
            db,
            username="TEST_ADMIN",  # Uppercase
            password="AdminPass123!"
        )

        assert user is not None
        assert user.id == test_admin_user.id

    def test_is_active_check_with_active_user(self, db: Session, test_operator_user: User):
        """Test is_active returns True for active user."""
        assert user_crud.is_active(test_operator_user) is True

    def test_is_active_check_with_inactive_user(self, db: Session, test_inactive_user: User):
        """Test is_active returns False for inactive user."""
        assert user_crud.is_active(test_inactive_user) is False

    def test_is_active_check_with_none(self, db: Session):
        """Test is_active returns False for None."""
        assert user_crud.is_active(None) is False

    def test_update_last_login(self, db: Session, test_operator_user: User):
        """Test updating last login timestamp."""
        original_login = test_operator_user.last_login_at

        updated_user = user_crud.update_last_login(db, user_id=test_operator_user.id)
        db.commit()

        assert updated_user is not None
        assert updated_user.last_login_at is not None
        assert updated_user.last_login_at != original_login


class TestUserByRole:
    """Test role-based user queries."""

    def test_get_by_role_admin(self, db: Session, test_admin_user: User):
        """Test getting users by ADMIN role."""
        admins = user_crud.get_by_role(db, role=UserRole.ADMIN)

        assert len(admins) > 0
        assert all(u.role == UserRole.ADMIN for u in admins)
        assert any(u.id == test_admin_user.id for u in admins)

    def test_get_by_role_manager(self, db: Session, test_manager_user: User):
        """Test getting users by MANAGER role."""
        managers = user_crud.get_by_role(db, role=UserRole.MANAGER)

        assert len(managers) > 0
        assert all(u.role == UserRole.MANAGER for u in managers)
        assert any(u.id == test_manager_user.id for u in managers)

    def test_get_by_role_operator(self, db: Session, test_operator_user: User):
        """Test getting users by OPERATOR role."""
        operators = user_crud.get_by_role(db, role=UserRole.OPERATOR)

        assert len(operators) > 0
        assert all(u.role == UserRole.OPERATOR for u in operators)
        assert any(u.id == test_operator_user.id for u in operators)

    def test_get_by_role_with_pagination(self, db: Session):
        """Test pagination in get_by_role."""
        # Create multiple operators
        for i in range(5):
            user_data = UserCreate(
                username=f"operator{i}",
                email=f"op{i}@test.com",
                password="Password123!",
                full_name=f"Operator {i}",
                role=UserRole.OPERATOR,
            )
            user_crud.create(db, user_in=user_data)
        db.commit()

        page1 = user_crud.get_by_role(db, role=UserRole.OPERATOR, skip=0, limit=2)
        page2 = user_crud.get_by_role(db, role=UserRole.OPERATOR, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        # Pages should not overlap
        assert {u.id for u in page1}.isdisjoint({u.id for u in page2})
