"""
Operator session management routes.

Provides endpoints for:
- Get operator session (/operator)
- Operator login (/operator-login)
- Operator logout (/operator-logout)

Also exports session management functions for use by other modules.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from station_service.api.dependencies import get_backend_client, get_config
from station_service.api.schemas.responses import ApiResponse, ErrorResponse
from station_service.api.routes.system.schemas import (
    OperatorInfo,
    OperatorSession,
    OperatorLoginRequest,
)
from station_service.models.config import StationConfig
from station_service.sync.backend_client import BackendClient

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Session State Management
# ============================================================================

# In-memory operator session state (single station)
_operator_session: Dict[str, Any] = {
    "logged_in": False,
    "operator": None,
    "access_token": None,
    "refresh_token": None,
    "expires_at": None,
    "logged_in_at": None,
}


def get_operator_session() -> Dict[str, Any]:
    """Get the current operator session state."""
    return _operator_session


def set_operator_session(
    operator: Optional[Dict[str, Any]] = None,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
    expires_in: Optional[int] = None,
    station_api_key: Optional[str] = None,
) -> None:
    """
    Set the operator session state.

    Args:
        operator: Operator info dict with id, username, name, role
        access_token: JWT access token
        refresh_token: Refresh token for obtaining new access tokens
        expires_in: Token expiration time in seconds
        station_api_key: Station API key for service-level calls
    """
    global _operator_session
    if operator and access_token:
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)

        _operator_session = {
            "logged_in": True,
            "operator": operator,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "logged_in_at": datetime.now(),
        }

        # Also update TokenManager for centralized token management
        from station_service.core.token_manager import get_token_manager
        token_manager = get_token_manager()
        token_manager.set_tokens(
            access_token=access_token,
            refresh_token=refresh_token or "",
            expires_in=expires_in,
            user_id=operator.get("id"),
            username=operator.get("username"),
            station_api_key=station_api_key,
        )
    else:
        _operator_session = {
            "logged_in": False,
            "operator": None,
            "access_token": None,
            "refresh_token": None,
            "expires_at": None,
            "logged_in_at": None,
        }

        # Clear TokenManager
        from station_service.core.token_manager import get_token_manager
        get_token_manager().clear_tokens()


def update_operator_tokens(
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[datetime] = None,
) -> None:
    """
    Update operator session tokens after refresh.

    Args:
        access_token: New access token
        refresh_token: New refresh token (or keep existing)
        expires_at: New expiration timestamp
    """
    global _operator_session
    if _operator_session["logged_in"]:
        _operator_session["access_token"] = access_token
        if refresh_token:
            _operator_session["refresh_token"] = refresh_token
        if expires_at:
            _operator_session["expires_at"] = expires_at
        logger.debug("Operator session tokens updated")


def clear_operator_session() -> None:
    """Clear the operator session state."""
    set_operator_session(None, None)


# ============================================================================
# API Endpoints
# ============================================================================


@router.get(
    "/operator",
    response_model=ApiResponse[OperatorSession],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Get current operator session",
    description="""
    Get the current operator session state.

    Returns:
    - logged_in: Whether an operator is logged in
    - operator: Operator info if logged in (id, username, name, role)
    - logged_in_at: Login timestamp if logged in
    """,
)
async def get_operator(
    config: StationConfig = Depends(get_config),
) -> ApiResponse[OperatorSession]:
    """Get current operator session."""
    try:
        session = get_operator_session()

        operator_info = None
        if session["operator"]:
            operator_info = OperatorInfo(
                id=session["operator"].get("id", 0),
                username=session["operator"].get("username", ""),
                name=session["operator"].get("name", session["operator"].get("username", "")),
                role=session["operator"].get("role", ""),
            )

        response = OperatorSession(
            logged_in=session["logged_in"],
            operator=operator_info,
            access_token=None,  # Don't expose token in response
            logged_in_at=session["logged_in_at"],
        )

        return ApiResponse(
            success=True,
            data=response,
        )
    except Exception as e:
        logger.exception("Failed to get operator session")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get operator session: {str(e)}",
        )


@router.post(
    "/operator-login",
    response_model=ApiResponse[OperatorSession],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Operator login",
    description="""
    Login an operator using backend authentication.

    Authenticates with the backend server and stores the session.
    The operator info is used for 착공/완공 process tracking.
    """,
)
async def operator_login(
    request: OperatorLoginRequest,
    config: StationConfig = Depends(get_config),
    backend_client: BackendClient = Depends(get_backend_client),
) -> ApiResponse[OperatorSession]:
    """Login operator via backend."""
    from station_service.core.exceptions import BackendConnectionError, BackendError

    try:
        # Check if backend is configured
        if not config.backend.url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend not configured. Set backend URL in station.yaml.",
            )

        # Ensure client is connected
        if not backend_client.is_connected:
            await backend_client.connect()

        # Authenticate with backend
        login_response = await backend_client.login(
            username=request.username,
            password=request.password,
        )

        # Extract user info and tokens
        access_token = login_response.get("access_token", "")
        refresh_token = login_response.get("refresh_token")
        expires_in = login_response.get("expires_in")
        user_info = login_response.get("user", {})
        station_api_key = login_response.get("station_api_key")

        if not access_token or not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login response from backend",
            )

        # Store session with refresh token and station API key
        set_operator_session(
            operator={
                "id": user_info.get("id", 0),
                "username": user_info.get("username", request.username),
                "name": user_info.get("name", user_info.get("username", "")),
                "role": user_info.get("role", ""),
            },
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            station_api_key=station_api_key,
        )

        session = get_operator_session()
        operator_info = OperatorInfo(
            id=session["operator"]["id"],
            username=session["operator"]["username"],
            name=session["operator"]["name"],
            role=session["operator"]["role"],
        )

        logger.info(f"Operator logged in: {operator_info.username} (ID: {operator_info.id})")

        return ApiResponse(
            success=True,
            data=OperatorSession(
                logged_in=True,
                operator=operator_info,
                access_token=None,  # Don't expose token
                logged_in_at=session["logged_in_at"],
            ),
            message=f"Welcome, {operator_info.name or operator_info.username}!",
        )

    except BackendConnectionError as e:
        logger.error(f"Backend connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to backend: {str(e)}",
        )
    except BackendError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.message) if hasattr(e, "message") else "Login failed",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to login operator")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login: {str(e)}",
        )


@router.post(
    "/operator-logout",
    response_model=ApiResponse[OperatorSession],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
    summary="Operator logout",
    description="""
    Logout the current operator.

    Clears the operator session from the station service.
    """,
)
async def operator_logout() -> ApiResponse[OperatorSession]:
    """Logout current operator."""
    try:
        session = get_operator_session()
        username = session["operator"]["username"] if session["operator"] else "unknown"

        clear_operator_session()

        logger.info(f"Operator logged out: {username}")

        return ApiResponse(
            success=True,
            data=OperatorSession(
                logged_in=False,
                operator=None,
                access_token=None,
                logged_in_at=None,
            ),
            message="Logged out successfully",
        )
    except Exception as e:
        logger.exception("Failed to logout operator")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}",
        )
