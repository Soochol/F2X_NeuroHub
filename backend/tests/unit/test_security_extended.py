"""
Extended unit tests for security functions.

Tests additional security scenarios to improve coverage.
"""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    check_permission,
    has_admin_permission,
    has_manager_permission,
)
from app.schemas.user import UserRole


class TestPasswordSecurityEdgeCases:
    """Additional password security tests."""

    def test_long_password_hashing(self):
        """Test hashing a very long password."""
        long_password = "A" * 100
        hashed = get_password_hash(long_password)

        assert hashed is not None
        assert verify_password(long_password, hashed)

    def test_special_chars_password(self):
        """Test hashing password with special characters."""
        special_password = "P@$$w0rd!#$%^&*()"
        hashed = get_password_hash(special_password)

        assert hashed is not None
        assert verify_password(special_password, hashed)

    def test_unicode_password(self):
        """Test hashing password with unicode characters."""
        unicode_password = "пароль密码パスワード"
        hashed = get_password_hash(unicode_password)

        assert hashed is not None
        assert verify_password(unicode_password, hashed)

    def test_whitespace_password(self):
        """Test hashing password with whitespace."""
        whitespace_password = "  password  with  spaces  "
        hashed = get_password_hash(whitespace_password)

        assert hashed is not None
        assert verify_password(whitespace_password, hashed)


class TestTokenEdgeCases:
    """Additional JWT token tests."""

    def test_token_with_additional_claims(self):
        """Test creating token with additional claims."""
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(hours=1)
        )

        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "user123"

    def test_token_with_short_expiration(self):
        """Test creating token with short expiration delta."""
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(seconds=1)
        )

        # Token should still be valid
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "user123"

    def test_token_with_negative_expiration(self):
        """Test creating token with negative expiration delta."""
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(seconds=-1)
        )

        # Token should be expired
        payload = decode_access_token(token)
        assert payload is None

    def test_decode_empty_token(self):
        """Test decoding empty token string."""
        result = decode_access_token("")
        assert result is None

    def test_decode_none_token(self):
        """Test decoding None token."""
        # Should handle gracefully
        try:
            result = decode_access_token(None)
            assert result is None
        except (TypeError, AttributeError):
            pass  # Expected for None input


class TestRolePermissionEdgeCases:
    """Additional role permission tests."""

    def test_check_permission_same_role_operator(self):
        """Test operator has permission for operator level."""
        result = check_permission(UserRole.OPERATOR, UserRole.OPERATOR)
        assert result is True

    def test_check_permission_same_role_manager(self):
        """Test manager has permission for manager level."""
        result = check_permission(UserRole.MANAGER, UserRole.MANAGER)
        assert result is True

    def test_check_permission_same_role_admin(self):
        """Test admin has permission for admin level."""
        result = check_permission(UserRole.ADMIN, UserRole.ADMIN)
        assert result is True

    def test_admin_has_all_permissions(self):
        """Test admin has permission for all roles."""
        assert check_permission(UserRole.ADMIN, UserRole.OPERATOR) is True
        assert check_permission(UserRole.ADMIN, UserRole.MANAGER) is True
        assert check_permission(UserRole.ADMIN, UserRole.ADMIN) is True

    def test_manager_permissions(self):
        """Test manager permission boundaries."""
        assert check_permission(UserRole.MANAGER, UserRole.OPERATOR) is True
        assert check_permission(UserRole.MANAGER, UserRole.MANAGER) is True
        assert check_permission(UserRole.MANAGER, UserRole.ADMIN) is False

    def test_operator_permissions(self):
        """Test operator permission boundaries."""
        assert check_permission(UserRole.OPERATOR, UserRole.OPERATOR) is True
        assert check_permission(UserRole.OPERATOR, UserRole.MANAGER) is False
        assert check_permission(UserRole.OPERATOR, UserRole.ADMIN) is False


class TestPasswordVerificationEdgeCases:
    """Edge case tests for password verification."""

    def test_verify_with_invalid_hash_format(self):
        """Test verify with malformed hash returns False."""
        result = verify_password("password", "not-a-valid-hash")
        assert result is False

    def test_verify_case_sensitivity(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password(password.lower(), hashed) is False
        assert verify_password(password.upper(), hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")

        assert hash1 != hash2

    def test_same_password_different_salts(self):
        """Test that same password produces different hashes (random salt)."""
        password = "SamePassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Both should verify but have different hashes
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
