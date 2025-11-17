"""
Dependency injection utilities for FastAPI.

Provides:
    - Database session dependency
    - Authentication dependencies (current user, permissions)
    - Role-based access control (RBAC) dependencies
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.crud import user as user_crud
from app.database import SessionLocal
from app.models import User
from app.schemas import UserRole


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login",
    auto_error=False  # Don't automatically raise 401 for missing token
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        SQLAlchemy session

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        db: Database session
        token: JWT token from Authorization header

    Returns:
        Current user object

    Raises:
        HTTPException 401: If token is missing or invalid
        HTTPException 404: If user not found

    Usage:
        @app.get("/me")
        def read_current_user(current_user: User = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    # Decode token
    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user ID from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    try:
        user = user_crud.get(db, id=int(user_id))
    except ValueError:
        raise credentials_exception

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify account is active.

    Args:
        current_user: Current authenticated user

    Returns:
        Current active user

    Raises:
        HTTPException 400: If user account is inactive

    Usage:
        @app.get("/protected")
        def protected_route(user: User = Depends(get_current_active_user)):
            return {"message": "Access granted"}
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify ADMIN role.

    Args:
        current_user: Current authenticated active user

    Returns:
        Current admin user

    Raises:
        HTTPException 403: If user is not ADMIN

    Usage:
        @app.delete("/users/{id}")
        def delete_user(
            id: int,
            admin: User = Depends(get_current_admin_user)
        ):
            # Only admins can delete users
            return crud.delete(db, id=id)
    """
    if not security.has_admin_permission(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def get_current_manager_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and verify MANAGER or ADMIN role.

    Args:
        current_user: Current authenticated active user

    Returns:
        Current manager or admin user

    Raises:
        HTTPException 403: If user is not MANAGER or ADMIN

    Usage:
        @app.post("/lots/{id}/close")
        def close_lot(
            id: int,
            manager: User = Depends(get_current_manager_user)
        ):
            # Only managers can close LOTs
            return crud.close_lot(db, lot_id=id)
    """
    if not security.has_manager_permission(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin privileges required"
        )
    return current_user


def check_role_permission(required_role: UserRole):
    """
    Dependency factory for custom role-based access control.

    Args:
        required_role: Minimum required role for access

    Returns:
        Dependency function that checks role permission

    Usage:
        @app.post("/lots/")
        def create_lot(
            lot_in: LotCreate,
            user: User = Depends(check_role_permission(UserRole.MANAGER))
        ):
            # Only managers and admins can create LOTs
            return crud.create(db, obj_in=lot_in)
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not security.check_permission(current_user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' or higher required"
            )
        return current_user

    return role_checker
