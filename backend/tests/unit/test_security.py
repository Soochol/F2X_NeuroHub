"""
Unit tests for app/core/security.py module.

Tests:
    - Password hashing and verification (bcrypt)
    - JWT token generation and validation
    - Token expiration handling
    - Role-based permission checks
    - Additional claims in JWT
"""

import pytest
from datetime import timedelta, datetime
from jose import jwt

from app.core import security
from app.schemas import UserRole
from app.config import settings


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_password_hash_creates_valid_hash(self):
        """Test that password hashing produces a valid bcrypt hash."""
        password = "SecurePassword123!"
        hashed = security.get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # Hash should not equal plain password
        assert hashed.startswith("$2b$")  # Bcrypt hash format

    def test_password_verification_succeeds_with_correct_password(self):
        """Test that correct password verifies successfully."""
        password = "CorrectPassword123!"
        hashed = security.get_password_hash(password)

        assert security.verify_password(password, hashed) is True

    def test_password_verification_fails_with_wrong_password(self):
        """Test that incorrect password fails verification."""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = security.get_password_hash(password)

        assert security.verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "SamePassword123!"
        hash1 = security.get_password_hash(password)
        hash2 = security.get_password_hash(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2
        # But both should verify the password
        assert security.verify_password(password, hash1) is True
        assert security.verify_password(password, hash2) is True

    def test_empty_password_handling(self):
        """Test behavior with empty password."""
        assert security.verify_password("", "") is False
        assert security.verify_password("password", "") is False
        assert security.verify_password("", "hashed") is False


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token_with_subject(self):
        """Test creating JWT token with subject (user ID)."""
        subject = "user123"
        token = security.create_access_token(subject=subject)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long

    def test_create_access_token_with_int_subject(self):
        """Test creating JWT token with integer subject (user ID)."""
        subject = 12345
        token = security.create_access_token(subject=subject)

        payload = security.decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(subject)  # Subject is string

    def test_decode_access_token_returns_valid_payload(self):
        """Test decoding a valid JWT token returns correct payload."""
        subject = "user456"
        token = security.create_access_token(subject=subject)

        payload = security.decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == subject
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at time

    def test_token_contains_additional_claims(self):
        """Test that additional claims are included in token."""
        subject = "user789"
        additional_claims = {
            "role": "ADMIN",
            "username": "admin_user",
            "department": "IT"
        }
        token = security.create_access_token(
            subject=subject,
            additional_claims=additional_claims
        )

        payload = security.decode_access_token(token)

        assert payload is not None
        assert payload["role"] == "ADMIN"
        assert payload["username"] == "admin_user"
        assert payload["department"] == "IT"

    def test_token_expiration_with_custom_delta(self):
        """Test token expiration with custom time delta."""
        subject = "user999"
        expires_delta = timedelta(minutes=15)
        token = security.create_access_token(
            subject=subject,
            expires_delta=expires_delta
        )

        payload = security.decode_access_token(token)

        assert payload is not None
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]

        # Expiration should be ~15 minutes after issued
        exp_diff = exp_timestamp - iat_timestamp
        assert 14 * 60 < exp_diff < 16 * 60  # Between 14-16 minutes

    def test_token_expiration_with_default_delta(self):
        """Test token expiration with default time delta from settings."""
        subject = "user111"
        token = security.create_access_token(subject=subject)

        payload = security.decode_access_token(token)

        assert payload is not None
        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]

        # Default expiration from settings
        expected_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        exp_diff_minutes = (exp_timestamp - iat_timestamp) / 60

        # Allow 1 minute tolerance for execution time
        assert expected_minutes - 1 < exp_diff_minutes < expected_minutes + 1

    def test_decode_invalid_token_returns_none(self):
        """Test that decoding invalid token returns None."""
        invalid_token = "invalid.jwt.token"
        payload = security.decode_access_token(invalid_token)

        assert payload is None

    def test_decode_malformed_token_returns_none(self):
        """Test that decoding malformed token returns None."""
        malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"
        payload = security.decode_access_token(malformed_token)

        assert payload is None

    def test_decode_token_with_wrong_secret_returns_none(self):
        """Test that token signed with different secret is rejected."""
        subject = "user222"
        # Create token with different secret
        wrong_secret_token = jwt.encode(
            {"sub": subject, "exp": datetime.utcnow() + timedelta(minutes=30)},
            "wrong_secret_key",
            algorithm=settings.ALGORITHM
        )

        payload = security.decode_access_token(wrong_secret_token)

        assert payload is None

    def test_expired_token_returns_none(self):
        """Test that expired token is rejected."""
        subject = "user333"
        # Create token that expires immediately
        expired_token = security.create_access_token(
            subject=subject,
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )

        payload = security.decode_access_token(expired_token)

        assert payload is None


class TestRolePermissions:
    """Test role-based access control (RBAC) functions."""

    def test_admin_has_admin_permission(self):
        """Test that ADMIN role has admin permission."""
        assert security.has_admin_permission(UserRole.ADMIN) is True

    def test_manager_does_not_have_admin_permission(self):
        """Test that MANAGER role does not have admin permission."""
        assert security.has_admin_permission(UserRole.MANAGER) is False

    def test_operator_does_not_have_admin_permission(self):
        """Test that OPERATOR role does not have admin permission."""
        assert security.has_admin_permission(UserRole.OPERATOR) is False

    def test_admin_has_manager_permission(self):
        """Test that ADMIN role has manager permission."""
        assert security.has_manager_permission(UserRole.ADMIN) is True

    def test_manager_has_manager_permission(self):
        """Test that MANAGER role has manager permission."""
        assert security.has_manager_permission(UserRole.MANAGER) is True

    def test_operator_does_not_have_manager_permission(self):
        """Test that OPERATOR role does not have manager permission."""
        assert security.has_manager_permission(UserRole.OPERATOR) is False

    def test_permission_hierarchy_admin_over_manager(self):
        """Test that ADMIN has permission for MANAGER-required operations."""
        assert security.check_permission(UserRole.ADMIN, UserRole.MANAGER) is True

    def test_permission_hierarchy_admin_over_operator(self):
        """Test that ADMIN has permission for OPERATOR-required operations."""
        assert security.check_permission(UserRole.ADMIN, UserRole.OPERATOR) is True

    def test_permission_hierarchy_manager_over_operator(self):
        """Test that MANAGER has permission for OPERATOR-required operations."""
        assert security.check_permission(UserRole.MANAGER, UserRole.OPERATOR) is True

    def test_permission_hierarchy_manager_under_admin(self):
        """Test that MANAGER does not have ADMIN permissions."""
        assert security.check_permission(UserRole.MANAGER, UserRole.ADMIN) is False

    def test_permission_hierarchy_operator_under_manager(self):
        """Test that OPERATOR does not have MANAGER permissions."""
        assert security.check_permission(UserRole.OPERATOR, UserRole.MANAGER) is False

    def test_permission_hierarchy_operator_under_admin(self):
        """Test that OPERATOR does not have ADMIN permissions."""
        assert security.check_permission(UserRole.OPERATOR, UserRole.ADMIN) is False

    def test_same_role_has_permission(self):
        """Test that same role has permission for itself."""
        assert security.check_permission(UserRole.ADMIN, UserRole.ADMIN) is True
        assert security.check_permission(UserRole.MANAGER, UserRole.MANAGER) is True
        assert security.check_permission(UserRole.OPERATOR, UserRole.OPERATOR) is True


class TestTokenIntegration:
    """Integration tests for token creation and validation flow."""

    def test_create_and_decode_token_roundtrip(self):
        """Test full roundtrip of token creation and decoding."""
        user_id = 12345
        username = "test_user"
        role = "MANAGER"

        # Create token
        token = security.create_access_token(
            subject=user_id,
            additional_claims={
                "username": username,
                "role": role,
            }
        )

        # Decode token
        payload = security.decode_access_token(token)

        # Verify all data
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["username"] == username
        assert payload["role"] == role

    def test_multiple_tokens_for_different_users(self):
        """Test creating multiple tokens for different users."""
        user1_token = security.create_access_token(
            subject=1,
            additional_claims={"username": "user1", "role": "ADMIN"}
        )
        user2_token = security.create_access_token(
            subject=2,
            additional_claims={"username": "user2", "role": "OPERATOR"}
        )

        # Tokens should be different
        assert user1_token != user2_token

        # Both should decode correctly
        payload1 = security.decode_access_token(user1_token)
        payload2 = security.decode_access_token(user2_token)

        assert payload1["sub"] == "1"
        assert payload1["username"] == "user1"
        assert payload2["sub"] == "2"
        assert payload2["username"] == "user2"

    @pytest.mark.parametrize("user_id,role", [
        (1, UserRole.ADMIN),
        (2, UserRole.MANAGER),
        (3, UserRole.OPERATOR),
    ])
    def test_token_creation_for_all_roles(self, user_id, role):
        """Test token creation for all user roles."""
        token = security.create_access_token(
            subject=user_id,
            additional_claims={"role": role.value}
        )

        payload = security.decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["role"] == role.value
