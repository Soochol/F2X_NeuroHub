"""
Dependency injection utilities for FastAPI.

Provides:
    - Database session dependency
    - Authentication dependencies (current user, permissions)
    - Role-based access control (RBAC) dependencies
    - Hybrid authentication (JWT + API Key for stations)
"""

from dataclasses import dataclass
from typing import AsyncGenerator, Generator, Optional, Union

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core import security
from app.core.exceptions import (
    InvalidTokenException,
    UserNotFoundException,
    ValidationException,
    InsufficientPermissionsException,
)
from app.crud import user as user_crud
from app.database import SessionLocal, AsyncSessionLocal
from app.models import User
from app.schemas import UserRole


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login",
    auto_error=False  # Don't automatically raise 401 for missing token
)


# ============================================================
# Station API Key Authentication
# ============================================================

@dataclass
class StationAuth:
    """
    Station authentication context.

    Returned when a station authenticates via API Key instead of user JWT.
    """
    station_id: str
    auth_type: str = "api_key"

    @property
    def is_station(self) -> bool:
        return True


def get_api_key_header(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """
    Extract X-API-Key header from request.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        API key string or None if not provided
    """
    return x_api_key


def verify_station_api_key(api_key: str) -> StationAuth:
    """
    Verify station API key and return station context.

    API keys are JWT tokens with:
    - Long expiration (configured via STATION_API_KEY_EXPIRE_DAYS)
    - station_id claim
    - type: "station" claim

    Args:
        api_key: API key string (JWT format)

    Returns:
        StationAuth with station info

    Raises:
        InvalidTokenException: If API key is invalid
    """
    payload = security.decode_access_token(api_key)
    if payload is None:
        raise InvalidTokenException(message="Invalid or expired API key")

    # Verify this is a station token, not a user token
    token_type = payload.get("type")
    if token_type != "station":
        raise InvalidTokenException(message="Invalid API key type")

    station_id = payload.get("station_id")
    if not station_id:
        raise InvalidTokenException(message="API key missing station_id")

    return StationAuth(station_id=station_id)


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


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.

    Yields:
        AsyncSession: SQLAlchemy async session

    Usage:
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_auth_context(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(get_api_key_header),
    db: Session = Depends(get_db),
) -> Union[User, StationAuth]:
    """
    Hybrid authentication: Accept JWT Bearer token OR X-API-Key.

    Priority:
    1. Bearer token (JWT) -> returns User
    2. X-API-Key -> returns StationAuth
    3. Neither -> raises 401

    Args:
        token: JWT from Authorization header
        api_key: API key from X-API-Key header
        db: Database session

    Returns:
        User object if JWT authenticated, or StationAuth if API key

    Raises:
        InvalidTokenException: If neither auth method succeeds

    Usage:
        @router.get("/processes/active")
        def get_processes(auth: Union[User, StationAuth] = Depends(get_auth_context)):
            if isinstance(auth, StationAuth):
                # Station authenticated via API key
                log.info(f"Station {auth.station_id} accessed")
            else:
                # User authenticated via JWT
                log.info(f"User {auth.username} accessed")
    """
    # Try JWT first (user authentication)
    if token:
        try:
            payload = security.decode_access_token(token)
            if payload is not None:
                # Check if this is a user token (has 'sub' but no 'type' or type != 'station')
                token_type = payload.get("type")
                if token_type != "station":
                    user_id = payload.get("sub")
                    if user_id:
                        user = user_crud.get(db, user_id=int(user_id))
                        if user:
                            return user
        except Exception:
            pass  # Fall through to API key

    # Try API key (station authentication)
    if api_key:
        return verify_station_api_key(api_key)

    raise InvalidTokenException(
        message="Authentication required (Bearer token or X-API-Key)"
    )


def get_optional_auth_context(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(get_api_key_header),
    db: Session = Depends(get_db),
) -> Optional[Union[User, StationAuth]]:
    """
    Optional authentication: Accept JWT Bearer token OR X-API-Key, but allow anonymous.

    Same as get_auth_context but returns None instead of raising exception
    when no authentication is provided.

    Args:
        token: JWT from Authorization header
        api_key: API key from X-API-Key header
        db: Database session

    Returns:
        User object if JWT authenticated, StationAuth if API key, or None if no auth

    Usage:
        @router.get("/processes/active")
        def get_processes(auth: Optional[Union[User, StationAuth]] = Depends(get_optional_auth_context)):
            # Works with or without authentication
            ...
    """
    # Try JWT first (user authentication)
    if token:
        try:
            payload = security.decode_access_token(token)
            if payload is not None:
                token_type = payload.get("type")
                if token_type != "station":
                    user_id = payload.get("sub")
                    if user_id:
                        user = user_crud.get(db, user_id=int(user_id))
                        if user:
                            return user
        except Exception:
            pass  # Fall through to API key

    # Try API key (station authentication)
    if api_key:
        try:
            return verify_station_api_key(api_key)
        except Exception:
            pass  # Fall through to None

    # No auth provided - that's OK for optional auth
    return None


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
    if not token:
        raise InvalidTokenException(message="Authentication token is missing")

    # Decode token
    payload = security.decode_access_token(token)
    if payload is None:
        raise InvalidTokenException(message="Invalid or expired token")

    # Extract user ID from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise InvalidTokenException(message="Invalid token payload")

    # Get user from database
    try:
        user = user_crud.get(db, user_id=int(user_id))
    except ValueError as exc:
        raise InvalidTokenException(message="Invalid user ID in token") from exc

    if user is None:
        raise UserNotFoundException(user_id=user_id)

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
        raise ValidationException(message="User account is inactive")
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
        raise InsufficientPermissionsException(message="Admin privileges required")
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
        raise InsufficientPermissionsException(message="Manager or admin privileges required")
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
            raise InsufficientPermissionsException(
                message=f"Role '{required_role.value}' or higher required"
            )
        return current_user

    return role_checker


# ============================================================
# Station-Only Authentication
# ============================================================

def get_station_auth(
    api_key: Optional[str] = Depends(get_api_key_header),
) -> StationAuth:
    """
    Station-only authentication via X-API-Key.

    Unlike get_auth_context, this dependency ONLY accepts station API keys.
    User JWT tokens are NOT accepted - use this for station-specific endpoints.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        StationAuth with station context

    Raises:
        InvalidTokenException: If API key is missing or invalid

    Usage:
        @router.post("/pull/{sequence_name}")
        def pull_sequence(
            sequence_name: str,
            station: StationAuth = Depends(get_station_auth),
        ):
            # Only stations with valid API keys can access
            log.info(f"Station {station.station_id} pulling sequence")
    """
    if not api_key:
        raise InvalidTokenException(
            message="Station API key required (X-API-Key header)"
        )

    return verify_station_api_key(api_key)
