"""
Authentication API endpoints.

Provides:
    - User login (JWT token generation)
    - Token refresh
    - Current user profile retrieval
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.crud import user as user_crud
from app.crud.user import verify_password
from app.models import User
from app.schemas import UserInDB, UserLogin
from app.config import settings
from app.core.exceptions import (
    UnauthorizedException,
    ValidationException,
)


router = APIRouter()


@router.post("/login", response_model=dict[str, Any])
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login.

    Get an access token for future requests using username and password.

    **Request Body (form-data):**
    - username: User's username
    - password: User's password

    **Response:**
    - access_token: JWT token string
    - token_type: "bearer"
    - expires_in: Token expiration time in seconds

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/login" \\
         -H "Content-Type: application/x-www-form-urlencoded" \\
         -d "username=operator1&password=SecurePass123"
    ```

    **Response:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer",
        "expires_in": 1800
    }
    ```

    Raises:
        UnauthorizedException: Invalid credentials
        ValidationException: Inactive user account
    """
    # Check if user exists first
    user = user_crud.get_by_username(db, username=form_data.username)

    if not user:
        raise UnauthorizedException(
            message="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise UnauthorizedException(
            message="비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise ValidationException(message="Inactive user account")

    # Update last login timestamp
    user_crud.update_last_login(db, user_id=user.id)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={
            "role": user.role.value,
            "username": user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        }
    }


@router.post("/login/json", response_model=dict[str, Any])
def login_json(
    db: Session = Depends(deps.get_db),
    credentials: UserLogin = None,
) -> Any:
    """
    JSON-based login endpoint (alternative to OAuth2 form).

    **Request Body (JSON):**
    ```json
    {
        "username": "operator1",
        "password": "SecurePass123"
    }
    ```

    **Response:**
    Same as /login endpoint

    Raises:
        UnauthorizedException: Invalid credentials
        ValidationException: Inactive user account
    """
    # Check if user exists first
    user = user_crud.get_by_username(db, username=credentials.username)

    if not user:
        raise UnauthorizedException(message="사용자를 찾을 수 없습니다")

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException(message="비밀번호가 올바르지 않습니다")

    if not user.is_active:
        raise ValidationException(message="비활성화된 계정입니다")

    # Update last login timestamp
    user_crud.update_last_login(db, user_id=user.id)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={
            "role": user.role.value,
            "username": user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        }
    }


@router.get("/me", response_model=UserInDB)
def read_current_user(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current authenticated user profile.

    **Headers:**
    - Authorization: Bearer {access_token}

    **Response:**
    Complete user profile (excluding password_hash)

    **Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/auth/me" \\
         -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
    ```

    Raises:
        UnauthorizedException: Missing or invalid token
        ValidationException: Inactive user account
    """
    return current_user


@router.post("/refresh", response_model=dict[str, Any])
def refresh_token(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Refresh access token.

    Get a new access token using an existing valid token.
    Useful for extending session without re-authentication.

    **Headers:**
    - Authorization: Bearer {access_token}

    **Response:**
    New access token with refreshed expiration time

    Raises:
        UnauthorizedException: Missing or invalid token
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=current_user.id,
        expires_delta=access_token_expires,
        additional_claims={
            "role": current_user.role.value,
            "username": current_user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Logout current user.

    Note: Since we're using stateless JWT tokens, logout is handled
    client-side by discarding the token. This endpoint is provided
    for API consistency and future enhancements (e.g., token blacklisting).

    **Headers:**
    - Authorization: Bearer {access_token}

    **Response:**
    Logout confirmation message

    **Client Implementation:**
    After calling this endpoint, the client should delete the stored token.
    """
    return {
        "message": "Successfully logged out",
        "detail": "Please discard your access token"
    }
