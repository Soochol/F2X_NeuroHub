"""
Extended unit tests for User CRUD operations.

Tests password hashing, authentication, and edge cases
to improve coverage on app/crud/user.py.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.crud.user import (
    get_password_hash,
    verify_password,
    get,
    get_by_username,
    get_by_email,
    authenticate,
    is_active,
    update_last_login,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_returns_hash(self):
        """Test that get_password_hash returns a bcrypt hash."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_get_password_hash_empty_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_password_hash("")

        assert "Password cannot be empty" in str(exc_info.value)

    def test_get_password_hash_none_raises_error(self):
        """Test that None password raises ValueError."""
        with pytest.raises(ValueError):
            get_password_hash(None)

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "CorrectPassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "CorrectPassword"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty_plain(self):
        """Test verify_password with empty plain password returns False."""
        hashed = get_password_hash("SomePassword")

        assert verify_password("", hashed) is False

    def test_verify_password_empty_hash(self):
        """Test verify_password with empty hash returns False."""
        assert verify_password("SomePassword", "") is False

    def test_verify_password_both_empty(self):
        """Test verify_password with both empty returns False."""
        assert verify_password("", "") is False

    def test_verify_password_none_plain(self):
        """Test verify_password with None plain password returns False."""
        hashed = get_password_hash("SomePassword")
        assert verify_password(None, hashed) is False

    def test_verify_password_none_hash(self):
        """Test verify_password with None hash returns False."""
        assert verify_password("SomePassword", None) is False


class TestUserGet:
    """Tests for get user functions."""

    def test_get_existing_user(self):
        """Test getting an existing user by ID."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_db.query().filter().first.return_value = mock_user

        result = get(mock_db, user_id=1)

        assert result is not None
        assert result.id == 1

    def test_get_nonexistent_user(self):
        """Test getting non-existent user returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = get(mock_db, user_id=999)

        assert result is None

    def test_get_by_username_existing(self):
        """Test getting user by username."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_db.query().filter().first.return_value = mock_user

        result = get_by_username(mock_db, username="testuser")

        assert result is not None
        assert result.username == "testuser"

    def test_get_by_username_nonexistent(self):
        """Test getting non-existent username returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = get_by_username(mock_db, username="nonexistent")

        assert result is None

    def test_get_by_email_existing(self):
        """Test getting user by email."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_db.query().filter().first.return_value = mock_user

        result = get_by_email(mock_db, email="test@example.com")

        assert result is not None
        assert result.email == "test@example.com"

    def test_get_by_email_nonexistent(self):
        """Test getting non-existent email returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = get_by_email(mock_db, email="nonexistent@example.com")

        assert result is None


class TestAuthentication:
    """Tests for authentication function."""

    def test_authenticate_valid_credentials(self):
        """Test authentication with valid credentials."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.username = "testuser"
        password = "TestPassword123"
        mock_user.password_hash = get_password_hash(password)

        mock_db.query().filter().first.return_value = mock_user

        result = authenticate(mock_db, username="testuser", password=password)

        assert result is not None
        assert result.username == "testuser"

    def test_authenticate_invalid_username(self):
        """Test authentication with invalid username returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = authenticate(mock_db, username="nonexistent", password="password")

        assert result is None

    def test_authenticate_invalid_password(self):
        """Test authentication with wrong password returns None."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_user.password_hash = get_password_hash("CorrectPassword")

        mock_db.query().filter().first.return_value = mock_user

        result = authenticate(mock_db, username="testuser", password="WrongPassword")

        assert result is None


class TestIsActive:
    """Tests for is_active function."""

    def test_is_active_true(self):
        """Test is_active returns True for active user."""
        mock_user = MagicMock()
        mock_user.is_active = True

        result = is_active(mock_user)

        assert result is True

    def test_is_active_false(self):
        """Test is_active returns False for inactive user."""
        mock_user = MagicMock()
        mock_user.is_active = False

        result = is_active(mock_user)

        assert result is False


class TestUpdateLastLogin:
    """Tests for update_last_login function."""

    def test_update_last_login_nonexistent_user(self):
        """Test updating last login for non-existent user returns None."""
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None

        result = update_last_login(mock_db, user_id=999)

        assert result is None
