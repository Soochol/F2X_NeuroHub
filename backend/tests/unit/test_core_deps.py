"""
Unit tests for Core Dependencies (authentication and authorization).

Tests the FastAPI dependency injection utilities including database sessions,
JWT authentication, and role-based access control.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from jose import JWTError

from app.core.deps import (
    get_db,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_manager_user,
    check_role_permission,
)
from app.schemas import UserRole


class TestGetDb:
    """Tests for get_db() database session dependency."""

    def test_get_db_yields_session(self):
        """Test that get_db yields a database session."""
        with patch('app.core.deps.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            # Act
            gen = get_db()
            session = next(gen)

            # Assert
            assert session == mock_session

    def test_get_db_closes_session_on_completion(self):
        """Test that get_db closes session after use."""
        with patch('app.core.deps.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            # Act
            gen = get_db()
            next(gen)
            try:
                next(gen)
            except StopIteration:
                pass

            # Assert
            mock_session.close.assert_called_once()

    def test_get_db_closes_session_on_exception(self):
        """Test that get_db closes session even when exception occurs."""
        with patch('app.core.deps.SessionLocal') as mock_session_local:
            mock_session = MagicMock()
            mock_session_local.return_value = mock_session

            # Act
            gen = get_db()
            next(gen)
            gen.close()

            # Assert
            mock_session.close.assert_called_once()


class TestGetCurrentUser:
    """Tests for get_current_user() authentication dependency."""

    def test_missing_token_raises_401(self):
        """Test that missing token raises 401 Unauthorized."""
        mock_db = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(db=mock_db, token=None)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_invalid_token_raises_401(self):
        """Test that invalid token raises 401 Unauthorized."""
        mock_db = MagicMock()

        with patch('app.core.deps.security.decode_access_token') as mock_decode:
            mock_decode.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(db=mock_db, token="invalid_token")

            assert exc_info.value.status_code == 401

    def test_token_without_sub_raises_401(self):
        """Test that token without 'sub' claim raises 401."""
        mock_db = MagicMock()

        with patch('app.core.deps.security.decode_access_token') as mock_decode:
            mock_decode.return_value = {"exp": 123456}  # No 'sub' field

            with pytest.raises(HTTPException) as exc_info:
                get_current_user(db=mock_db, token="token_without_sub")

            assert exc_info.value.status_code == 401

    def test_invalid_user_id_raises_401(self):
        """Test that non-integer user ID raises 401."""
        mock_db = MagicMock()

        with patch('app.core.deps.security.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "not_an_integer"}

            with patch('app.core.deps.user_crud.get') as mock_get:
                mock_get.side_effect = ValueError("invalid literal")

                with pytest.raises(HTTPException) as exc_info:
                    get_current_user(db=mock_db, token="valid_token")

                assert exc_info.value.status_code == 401

    def test_user_not_found_raises_404(self):
        """Test that non-existent user raises 404 Not Found."""
        mock_db = MagicMock()

        with patch('app.core.deps.security.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "123"}

            with patch('app.core.deps.user_crud.get') as mock_get:
                mock_get.return_value = None

                with pytest.raises(HTTPException) as exc_info:
                    get_current_user(db=mock_db, token="valid_token")

                assert exc_info.value.status_code == 404
                assert "User not found" in exc_info.value.detail

    def test_valid_token_returns_user(self):
        """Test that valid token returns user object."""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 123

        with patch('app.core.deps.security.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "123"}

            with patch('app.core.deps.user_crud.get') as mock_get:
                mock_get.return_value = mock_user

                result = get_current_user(db=mock_db, token="valid_token")

                assert result == mock_user
                mock_get.assert_called_once_with(mock_db, user_id=123)


class TestGetCurrentActiveUser:
    """Tests for get_current_active_user() dependency."""

    def test_active_user_returns_user(self):
        """Test that active user is returned successfully."""
        mock_user = MagicMock()
        mock_user.is_active = True

        result = get_current_active_user(current_user=mock_user)

        assert result == mock_user

    def test_inactive_user_raises_400(self):
        """Test that inactive user raises 400 Bad Request."""
        mock_user = MagicMock()
        mock_user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(current_user=mock_user)

        assert exc_info.value.status_code == 400
        assert "Inactive user account" in exc_info.value.detail


class TestGetCurrentAdminUser:
    """Tests for get_current_admin_user() dependency."""

    def test_admin_user_returns_user(self):
        """Test that admin user is returned successfully."""
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        with patch('app.core.deps.security.has_admin_permission') as mock_check:
            mock_check.return_value = True

            result = get_current_admin_user(current_user=mock_user)

            assert result == mock_user

    def test_non_admin_raises_403(self):
        """Test that non-admin user raises 403 Forbidden."""
        mock_user = MagicMock()
        mock_user.role = UserRole.OPERATOR

        with patch('app.core.deps.security.has_admin_permission') as mock_check:
            mock_check.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                get_current_admin_user(current_user=mock_user)

            assert exc_info.value.status_code == 403
            assert "Admin privileges required" in exc_info.value.detail

    def test_manager_raises_403(self):
        """Test that manager user raises 403 Forbidden for admin endpoint."""
        mock_user = MagicMock()
        mock_user.role = UserRole.MANAGER

        with patch('app.core.deps.security.has_admin_permission') as mock_check:
            mock_check.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                get_current_admin_user(current_user=mock_user)

            assert exc_info.value.status_code == 403


class TestGetCurrentManagerUser:
    """Tests for get_current_manager_user() dependency."""

    def test_manager_user_returns_user(self):
        """Test that manager user is returned successfully."""
        mock_user = MagicMock()
        mock_user.role = UserRole.MANAGER

        with patch('app.core.deps.security.has_manager_permission') as mock_check:
            mock_check.return_value = True

            result = get_current_manager_user(current_user=mock_user)

            assert result == mock_user

    def test_admin_can_access_manager_endpoint(self):
        """Test that admin user can access manager-level endpoints."""
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        with patch('app.core.deps.security.has_manager_permission') as mock_check:
            mock_check.return_value = True

            result = get_current_manager_user(current_user=mock_user)

            assert result == mock_user

    def test_operator_raises_403(self):
        """Test that operator user raises 403 Forbidden."""
        mock_user = MagicMock()
        mock_user.role = UserRole.OPERATOR

        with patch('app.core.deps.security.has_manager_permission') as mock_check:
            mock_check.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                get_current_manager_user(current_user=mock_user)

            assert exc_info.value.status_code == 403
            assert "Manager or admin privileges required" in exc_info.value.detail


class TestCheckRolePermission:
    """Tests for check_role_permission() dependency factory."""

    def test_returns_callable(self):
        """Test that check_role_permission returns a callable."""
        result = check_role_permission(UserRole.OPERATOR)

        assert callable(result)

    def test_operator_permission_passes_for_operator(self):
        """Test operator can access operator-level endpoint."""
        mock_user = MagicMock()
        mock_user.role = UserRole.OPERATOR

        with patch('app.core.deps.security.check_permission') as mock_check:
            mock_check.return_value = True

            role_checker = check_role_permission(UserRole.OPERATOR)
            result = role_checker(current_user=mock_user)

            assert result == mock_user

    def test_manager_permission_passes_for_manager(self):
        """Test manager can access manager-level endpoint."""
        mock_user = MagicMock()
        mock_user.role = UserRole.MANAGER

        with patch('app.core.deps.security.check_permission') as mock_check:
            mock_check.return_value = True

            role_checker = check_role_permission(UserRole.MANAGER)
            result = role_checker(current_user=mock_user)

            assert result == mock_user

    def test_admin_permission_passes_for_admin(self):
        """Test admin can access admin-level endpoint."""
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        with patch('app.core.deps.security.check_permission') as mock_check:
            mock_check.return_value = True

            role_checker = check_role_permission(UserRole.ADMIN)
            result = role_checker(current_user=mock_user)

            assert result == mock_user

    def test_insufficient_permission_raises_403(self):
        """Test insufficient permission raises 403 Forbidden."""
        mock_user = MagicMock()
        mock_user.role = UserRole.OPERATOR

        with patch('app.core.deps.security.check_permission') as mock_check:
            mock_check.return_value = False

            role_checker = check_role_permission(UserRole.ADMIN)

            with pytest.raises(HTTPException) as exc_info:
                role_checker(current_user=mock_user)

            assert exc_info.value.status_code == 403
            assert "ADMIN" in exc_info.value.detail

    def test_manager_cannot_access_admin_endpoint(self):
        """Test manager cannot access admin-only endpoint."""
        mock_user = MagicMock()
        mock_user.role = UserRole.MANAGER

        with patch('app.core.deps.security.check_permission') as mock_check:
            mock_check.return_value = False

            role_checker = check_role_permission(UserRole.ADMIN)

            with pytest.raises(HTTPException) as exc_info:
                role_checker(current_user=mock_user)

            assert exc_info.value.status_code == 403

    def test_higher_role_can_access_lower_level(self):
        """Test higher role can access lower permission level."""
        mock_user = MagicMock()
        mock_user.role = UserRole.ADMIN

        with patch('app.core.deps.security.check_permission') as mock_check:
            mock_check.return_value = True

            role_checker = check_role_permission(UserRole.OPERATOR)
            result = role_checker(current_user=mock_user)

            assert result == mock_user
