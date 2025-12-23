"""
Authentication API endpoints.

Provides:
    - User login (JWT token generation)
    - Token refresh
    - Current user profile retrieval
"""

from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.crud import user as user_crud
from app.crud.user import verify_password
from app.models import User
from app.schemas import UserInDB, UserLogin, Token, RefreshTokenRequest
from app.config import settings
from app.crud import refresh_token as refresh_token_crud
from app.core.exceptions import (
    UnauthorizedException,
    ValidationException,
    InvalidTokenException,
)


router = APIRouter()


@router.post("/login", response_model=dict[str, Any])
@router.post("/login/", response_model=dict[str, Any], include_in_schema=False)
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

    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = refresh_token_crud.create_refresh_token(
        db, user_id=user.id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_obj.token,
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

    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_obj = refresh_token_crud.create_refresh_token(
        db, user_id=user.id, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_obj.token,
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
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Refresh access token using a refresh token.

    **Request Body:**
    - refresh_token: The refresh token string

    **Response:**
    New access token and same/new refresh token

    Raises:
        InvalidTokenException: If refresh token is invalid or expired
    """
    token_obj = refresh_token_crud.get_refresh_token(db, token=refresh_data.refresh_token)
    
    if not token_obj or not refresh_token_crud.is_refresh_token_valid(token_obj):
        raise InvalidTokenException(message="유효하지 않거나 만료된 리프레시 토큰입니다")

    user = token_obj.user
    if not user.is_active:
        raise ValidationException(message="비활성화된 계정입니다")

    # Create new access token
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
        "refresh_token": token_obj.token,  # Keep same refresh token or could rotate
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
def logout(
    refresh_data: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Logout current user and revoke refresh token.

    **Request Body (Optional):**
    - refresh_token: The refresh token to revoke

    **Response:**
    Logout confirmation message
    """
    if refresh_data:
        refresh_token_crud.revoke_refresh_token(db, token=refresh_data.refresh_token)
    else:
        # Revoke all tokens for this user if no specific token provided
        refresh_token_crud.revoke_all_user_tokens(db, user_id=current_user.id)

    return {
        "message": "Successfully logged out",
        "detail": "Tokens have been revoked"
    }
