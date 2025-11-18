"""
FastAPI router for User entity endpoints.

This module implements RESTful API endpoints for user management including:
    - Standard CRUD operations (GET, POST, PUT, DELETE)
    - User lookup by username or email
    - Current user profile operations
    - Password management
    - Role-based filtering

Security:
    - password_hash is never included in API responses
    - Password changes require current password verification (to be implemented with auth)
    - All responses use UserInDB schema which excludes sensitive fields
    - Input validation via Pydantic schemas

Endpoints:
    GET    /users/              - List all users with pagination
    GET    /users/{id}          - Get user by ID
    GET    /users/username/{username} - Get user by username
    GET    /users/email/{email} - Get user by email
    GET    /users/role/{role}   - Get users by role with pagination
    POST   /users/              - Create new user
    PUT    /users/{id}          - Update user information
    DELETE /users/{id}          - Delete user account
    GET    /users/me            - Get current user (auth required)
    PUT    /users/me            - Update current user profile (auth required)
    PUT    /users/{id}/password - Change user password (admin only)
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models.user import UserRole
from app.schemas.user import (
    UserCreate,
    UserInDB,
    UserUpdate,
)


# Create APIRouter
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    response_model=List[UserInDB],
    summary="List all users",
    description="Retrieve a paginated list of all users with optional filtering by role and active status.",
)
def list_users(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        50,
        ge=1,
        le=1000,
        description="Maximum number of records to return (max: 1000)",
    ),
    role: Optional[UserRole] = Query(
        None,
        description="Filter by user role (ADMIN, MANAGER, OPERATOR)",
    ),
    is_active: Optional[bool] = Query(
        None,
        description="Filter by active status",
    ),
):
    """
    Retrieve a paginated list of users.

    Query parameters allow filtering by role and active status. Results are
    ordered by creation timestamp (newest first).

    Returns:
        List of UserInDB schemas (password_hash excluded)
    """
    try:
        users = crud.user.get_multi(
            db,
            skip=skip,
            limit=limit,
            role=role,
            is_active=is_active,
        )
        return users
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{user_id}",
    response_model=UserInDB,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID.",
)
def get_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="User ID to retrieve"),
):
    """
    Get a user by ID.

    Args:
        user_id: User ID to retrieve

    Returns:
        UserInDB schema for the requested user

    Raises:
        HTTPException 404: User not found
    """
    user = crud.user.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


@router.get(
    "/username/{username}",
    response_model=UserInDB,
    summary="Get user by username",
    description="Retrieve a user by their unique username.",
)
def get_user_by_username(
    *,
    db: Session = Depends(deps.get_db),
    username: str,
):
    """
    Get a user by username.

    Username lookup is case-insensitive.

    Args:
        username: Username to search for

    Returns:
        UserInDB schema for the requested user

    Raises:
        HTTPException 404: User not found
    """
    user = crud.user.get_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found",
        )
    return user


@router.get(
    "/email/{email}",
    response_model=UserInDB,
    summary="Get user by email",
    description="Retrieve a user by their unique email address.",
)
def get_user_by_email(
    *,
    db: Session = Depends(deps.get_db),
    email: str,
):
    """
    Get a user by email address.

    Email lookup is case-insensitive.

    Args:
        email: Email address to search for

    Returns:
        UserInDB schema for the requested user

    Raises:
        HTTPException 404: User not found
    """
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' not found",
        )
    return user


@router.get(
    "/role/{role}",
    response_model=List[UserInDB],
    summary="Get users by role",
    description="Retrieve all users with a specific role with pagination.",
)
def get_users_by_role(
    *,
    db: Session = Depends(deps.get_db),
    role: UserRole = Path(..., description="User role: ADMIN, MANAGER, OPERATOR"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return (max: 1000)",
    ),
):
    """
    Get all users with a specific role.

    Useful for admin operations like sending notifications to all managers
    or generating role-specific reports.

    Args:
        role: UserRole to filter by (ADMIN, MANAGER, OPERATOR)
        skip: Pagination offset
        limit: Maximum records to return

    Returns:
        List of UserInDB schemas with the specified role
    """
    try:
        users = crud.user.get_by_role(
            db,
            role=role,
            skip=skip,
            limit=limit,
        )
        return users
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account with automatic password hashing.",
)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    # current_user: User = Depends(deps.get_current_active_superuser),  # Auth Phase
):
    """
    Create a new user account.

    Creates a new user in the system. Username and email must be unique.
    Password is automatically hashed using bcrypt before storage.

    Security:
        - Password is hashed with bcrypt (cost factor 12) before storage
        - Plain text password is never stored or logged
        - Requires admin privileges (to be enforced with authentication)

    Args:
        user_in: UserCreate schema with user data and password

    Returns:
        Created UserInDB schema (password_hash excluded)

    Raises:
        HTTPException 400: Username or email already registered
        HTTPException 422: Invalid input data
    """
    # Check if username already exists
    existing_user = crud.user.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_user = crud.user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        db_user = crud.user.create(db, user_in=user_in)
        db.commit()
        db.refresh(db_user)
        return db_user
    except (IntegrityError, SQLAlchemyError) as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account",
        )


@router.put(
    "/{user_id}",
    response_model=UserInDB,
    summary="Update user",
    description="Update user information (excluding password).",
)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="ID of user to update"),
    user_in: UserUpdate,
    # current_user: User = Depends(deps.get_current_active_superuser),  # Auth Phase
):
    """
    Update user information.

    Updates the specified user with provided fields. All fields in UserUpdate
    are optional. Password changes are handled via a separate endpoint.

    Args:
        user_id: ID of user to update
        user_in: UserUpdate schema with fields to update

    Returns:
        Updated UserInDB schema

    Raises:
        HTTPException 404: User not found
        HTTPException 400: Username or email already registered
    """
    db_user = crud.user.get(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Check if new username is unique (if being changed)
    if user_in.username and user_in.username.lower() != db_user.username:
        existing_user = crud.user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    # Check if new email is unique (if being changed)
    if user_in.email and user_in.email.lower() != db_user.email:
        existing_user = crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    try:
        db_user = crud.user.update(db, user_id=user_id, user_in=user_in)
        db.commit()
        db.refresh(db_user)
        return db_user
    except (IntegrityError, SQLAlchemyError) as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account from the system.",
)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="ID of user to delete"),
    # current_user: User = Depends(deps.get_current_active_superuser),  # Auth Phase
):
    """
    Delete a user account.

    Removes the user record from the system. This is a hard delete operation.

    Security:
        - Requires admin privileges (to be enforced with authentication)
        - Consider soft deletes (is_active=False) for audit compliance

    Args:
        user_id: ID of user to delete

    Raises:
        HTTPException 404: User not found
    """
    db_user = crud.user.get(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    try:
        success = crud.user.delete(db, user_id=user_id)
        if success:
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user",
        )


# ============================================================================
# Future endpoints (to be implemented with authentication phase)
# ============================================================================

@router.get(
    "/me",
    response_model=UserInDB,
    summary="Get current user",
    description="Retrieve the current authenticated user's profile.",
)
def get_current_user(
    *,
    db: Session = Depends(deps.get_db),
    # current_user: User = Depends(deps.get_current_active_user),  # Auth Phase
):
    """
    Get current user profile.

    Requires authentication. Returns the profile of the currently authenticated user.

    Returns:
        UserInDB schema for current user

    Note:
        Endpoint structure is ready but authentication dependency is not yet implemented.
    """
    # TODO: Implement when authentication is available
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented",
    )


@router.put(
    "/me",
    response_model=UserInDB,
    summary="Update current user profile",
    description="Update the current authenticated user's profile information.",
)
def update_current_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    # current_user: User = Depends(deps.get_current_active_user),  # Auth Phase
):
    """
    Update current user profile.

    Allows users to update their own profile information. Cannot change role
    (requires admin privileges).

    Args:
        user_in: UserUpdate schema with fields to update

    Returns:
        Updated UserInDB schema for current user

    Note:
        Endpoint structure is ready but authentication dependency is not yet implemented.
    """
    # TODO: Implement when authentication is available
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented",
    )


@router.put(
    "/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change user password",
    description="Change a user's password. Admin only.",
)
def change_user_password(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="ID of user whose password to change"),
    old_password: str,
    new_password: str,
    # current_user: User = Depends(deps.get_current_active_user),  # Auth Phase
):
    """
    Change a user's password.

    Allows password reset with verification of current password.
    Requires admin privileges to change another user's password.

    Args:
        user_id: ID of user whose password to change
        old_password: Current password for verification
        new_password: New password (must meet security requirements)

    Raises:
        HTTPException 404: User not found
        HTTPException 401: Current password is incorrect
        HTTPException 422: New password does not meet requirements

    Note:
        Endpoint structure is ready but full authentication and verification
        logic will be implemented in authentication phase.
    """
    # TODO: Implement when authentication is available
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented",
    )
