"""
Security utilities for authentication and authorization.

Provides:
    - JWT token generation and validation
    - Password hashing and verification (bcrypt)
    - Role-based access control (RBAC) helpers
"""

from datetime import datetime, timedelta
from typing import Optional, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.schemas import UserRole


# Password hashing context (bcrypt with cost factor 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = get_password_hash("SecurePass123")
        >>> verify_password("SecurePass123", hashed)
        True
        >>> verify_password("WrongPass", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Uses bcrypt with cost factor 12 for security.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Example:
        >>> hashed = get_password_hash("MySecurePassword123")
        >>> len(hashed) > 50
        True
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject of the token (usually user ID or username)
        expires_delta: Optional custom expiration time delta
        additional_claims: Optional additional claims to include in token

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token(subject="user123", additional_claims={"role": "ADMIN"})
        >>> len(token) > 100
        True
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
    }

    # Add any additional claims
    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Decoded token payload if valid, None if invalid

    Example:
        >>> token = create_access_token(subject="user123")
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        'user123'
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def check_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """
    Check if user has required role permission.

    Role hierarchy (highest to lowest):
        ADMIN > MANAGER > OPERATOR

    Args:
        user_role: User's current role
        required_role: Required role for the operation

    Returns:
        True if user has permission, False otherwise

    Example:
        >>> check_permission(UserRole.ADMIN, UserRole.MANAGER)
        True
        >>> check_permission(UserRole.OPERATOR, UserRole.ADMIN)
        False
    """
    role_hierarchy = {
        UserRole.OPERATOR: 1,
        UserRole.MANAGER: 2,
        UserRole.ADMIN: 3,
    }

    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)


def has_admin_permission(user_role: UserRole) -> bool:
    """
    Check if user has admin permissions.

    Args:
        user_role: User's role

    Returns:
        True if user is ADMIN, False otherwise
    """
    return user_role == UserRole.ADMIN


def has_manager_permission(user_role: UserRole) -> bool:
    """
    Check if user has manager or higher permissions.

    Args:
        user_role: User's role

    Returns:
        True if user is MANAGER or ADMIN, False otherwise
    """
    return user_role in (UserRole.MANAGER, UserRole.ADMIN)
