"""
BackendClient for Station Service.

Provides async HTTP client for Backend WIP process operations:
- WIP lookup (string ID -> int ID)
- Process start (착공)
- Process complete (완공)
- Serial conversion (시리얼 변환)

Supports hybrid authentication:
- API Key: For service-level calls (WIP lookup, headers, processes list)
- JWT: For user-tracked calls (착공/완공) with automatic refresh on 401
"""

import functools
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

import httpx

from station_service.core.exceptions import (
    BackendConnectionError,
    BackendError,
    DuplicatePassError,
    InvalidWIPStatusError,
    PrerequisiteNotMetError,
    TokenExpiredError,
    TokenRefreshError,
    WIPNotFoundError,
)
from station_service.models.config import BackendConfig
from station_service.sync.models import (
    ProcessCompleteRequest,
    ProcessStartRequest,
    SerialConvertRequest,
    WIPLookupResult,
    ProcessHeaderOpenRequest,
    ProcessHeaderCloseRequest,
    ProcessHeaderResponse,
    ProcessHeaderSummary,
    SequencePullRequest,
    SequencePullResponse,
)

logger = logging.getLogger(__name__)

# Type variable for decorator return type preservation
T = TypeVar("T")


class AuthMode(str, Enum):
    """Authentication mode for API calls."""
    API_KEY = "api_key"  # Use X-API-Key header (service-level)
    JWT = "jwt"          # Use Bearer token with auto-refresh (user-level)
    NONE = "none"        # No authentication


def with_auth(auth_mode: AuthMode = AuthMode.JWT):
    """
    Decorator factory for authenticated API calls.

    Args:
        auth_mode: Which authentication to use
            - API_KEY: Uses configured api_key via X-API-Key header
            - JWT: Uses JWT from TokenManager with auto-refresh on 401
            - NONE: No authentication header

    Features:
        - JWT mode: Automatic 401 handling with token refresh (max 1 retry)
        - API_KEY mode: Uses station's API key, no refresh needed

    Usage:
        @with_auth(AuthMode.API_KEY)
        async def get_processes(self) -> list:
            ...

        @with_auth(AuthMode.JWT)
        async def start_process(self, ...) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(self: "BackendClient", *args, **kwargs) -> T:
            max_retries = 1 if auth_mode == AuthMode.JWT else 0

            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except BackendError as e:
                    is_last_attempt = attempt >= max_retries

                    if e.status_code == 401 and auth_mode == AuthMode.JWT and not is_last_attempt:
                        logger.info(
                            f"401 on {func.__name__}, attempting token refresh "
                            f"(attempt {attempt + 1}/{max_retries + 1})..."
                        )

                        if self._token_manager and await self._token_manager.handle_401_error():
                            new_token = self._token_manager.get_access_token()
                            if new_token:
                                self.update_auth_header(new_token)
                                continue  # Retry with new token

                        # Refresh failed
                        raise TokenExpiredError("Token refresh failed")

                    # Not a 401, or no retries left, or wrong auth mode
                    raise

            # Should never reach here, but safety fallback
            raise TokenExpiredError("Max retries exceeded")

        # Store auth mode on wrapper for introspection
        wrapper._auth_mode = auth_mode
        return wrapper
    return decorator


# Legacy decorator for backward compatibility
def with_token_refresh(func: Callable[..., T]) -> Callable[..., T]:
    """
    Legacy decorator - redirects to with_auth(AuthMode.JWT).

    Deprecated: Use @with_auth(AuthMode.JWT) instead.
    """
    return with_auth(AuthMode.JWT)(func)


class BackendClient:
    """
    Async HTTP client for Backend WIP process operations.

    Handles:
    - WIP lookup via scan endpoint (string -> int ID)
    - Process start (착공) API
    - Process complete (완공) API
    - Serial conversion API
    - Error mapping from Backend to Station exceptions
    - Automatic token refresh on 401 errors

    Usage:
        client = BackendClient(config=backend_config)
        await client.connect()

        # Lookup WIP
        wip = await client.lookup_wip("WIP-KR01PSA2511-001")
        print(f"Int ID: {wip.id}")

        # Start process
        await client.start_process(wip.id, ProcessStartRequest(...))

        await client.disconnect()
    """

    def __init__(self, config: BackendConfig) -> None:
        """
        Initialize the BackendClient.

        Args:
            config: Backend configuration
        """
        self._config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False

        # Token management for automatic refresh
        self._token_manager = None
        self._token_update_callback = None

    def set_token_manager(self, token_manager) -> None:
        """
        Set the TokenManager for automatic token refresh.

        Args:
            token_manager: TokenManager instance
        """
        from station_service.core.token_manager import TokenManager
        self._token_manager: Optional[TokenManager] = token_manager

        # Set up refresh callback
        if token_manager:
            token_manager.set_refresh_callback(self._refresh_token_callback)

    def set_token_update_callback(self, callback) -> None:
        """
        Set callback for token update notifications.

        Called when tokens are refreshed, allowing external state updates
        (e.g., updating operator session).

        Args:
            callback: Function(access_token, refresh_token, expires_at)
        """
        self._token_update_callback = callback
        if self._token_manager:
            self._token_manager.set_token_update_callback(callback)

    async def _refresh_token_callback(self, refresh_token: str) -> Dict[str, Any]:
        """
        Callback for TokenManager to refresh tokens.

        Args:
            refresh_token: Current refresh token

        Returns:
            Dict with new access_token, refresh_token, expires_in
        """
        return await self.refresh_access_token(refresh_token)

    def _get_api_key_header(self) -> Dict[str, str]:
        """
        Get API Key authentication header.

        Used for service-level calls that don't require user tracking.
        Prioritizes dynamic station_api_key from TokenManager (issued at login),
        falls back to static api_key from config.

        Returns:
            Dict with X-API-Key header if api_key is available
        """
        headers = {}

        # Priority 1: Dynamic station_api_key from TokenManager (issued at operator login)
        if self._token_manager:
            station_api_key = self._token_manager.get_station_api_key()
            if station_api_key:
                headers["X-API-Key"] = station_api_key
                return headers

        # Priority 2: Static api_key from config (fallback for initial connection)
        if self._config.api_key:
            headers["X-API-Key"] = self._config.api_key

        return headers

    def _get_jwt_header(self) -> Dict[str, str]:
        """
        Get JWT authentication header from TokenManager.

        Used for user-tracked calls (착공/완공).
        Does NOT trigger proactive refresh - refresh is handled
        reactively by @with_auth decorator on 401.

        Returns:
            Dict with Authorization header if token available
        """
        headers = {}
        if self._token_manager:
            token = self._token_manager.get_access_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    # Legacy method for backward compatibility
    async def _get_auth_header(self, access_token: Optional[str] = None) -> Dict[str, str]:
        """
        Legacy method - prefer _get_jwt_header() or _get_api_key_header().

        Deprecated: This method is kept for backward compatibility.
        """
        if access_token:
            return {"Authorization": f"Bearer {access_token}"}
        return self._get_jwt_header()

    def update_auth_header(self, access_token: str) -> None:
        """
        Update the HTTP client's Authorization header with new token.

        Args:
            access_token: New access token
        """
        if self._client:
            self._client.headers["Authorization"] = f"Bearer {access_token}"
            logger.debug("Updated HTTP client Authorization header")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._client is not None

    @property
    def base_url(self) -> str:
        """Get the Backend base URL."""
        return self._config.url.rstrip("/") if self._config.url else ""

    async def connect(self) -> None:
        """
        Initialize and connect the HTTP client.

        Raises:
            BackendConnectionError: If connection fails
        """
        if self._connected:
            logger.debug("BackendClient already connected")
            return

        if not self._config.url:
            logger.warning("Backend URL not configured")
            return

        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            if self._config.api_key:
                headers["Authorization"] = f"Bearer {self._config.api_key}"

            if self._config.station_id:
                headers["X-Station-ID"] = self._config.station_id

            if self._config.equipment_id:
                headers["X-Equipment-ID"] = str(self._config.equipment_id)

            self._client = httpx.AsyncClient(
                base_url=self._config.url,
                headers=headers,
                timeout=self._config.timeout,
            )

            self._connected = True
            logger.info(f"BackendClient connected to {self._config.url}")

        except Exception as e:
            raise BackendConnectionError(self._config.url, str(e))

    async def disconnect(self) -> None:
        """Disconnect and cleanup the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False
        logger.info("BackendClient disconnected")

    async def __aenter__(self) -> "BackendClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        await self.disconnect()

    async def health_check(self) -> bool:
        """
        Check Backend connection health.

        Returns:
            True if Backend is reachable and healthy
        """
        if not self._client:
            return False

        try:
            response = await self._client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False

    # ================================================================
    # WIP Lookup
    # ================================================================

    @with_auth(AuthMode.JWT)
    async def lookup_wip(
        self,
        wip_id_string: str,
        process_id: Optional[int] = None,
    ) -> WIPLookupResult:
        """
        Lookup WIP by string ID to get integer ID.

        Uses the scan endpoint to validate WIP and get its data.
        Uses JWT authentication (operator must be logged in).

        Args:
            wip_id_string: WIP ID string from barcode (e.g., "WIP-KR01PSA2511-001")
            process_id: Optional process ID for validation

        Returns:
            WIPLookupResult with int ID and status

        Raises:
            WIPNotFoundError: If WIP not found
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/wip-items/{wip_id_string}/scan"
        params = {}
        if process_id is not None:
            params["process_id"] = process_id

        # Use JWT authentication (operator must be logged in)
        headers = self._get_jwt_header()

        try:
            response = await self._client.post(url, params=params, headers=headers)
            return self._handle_wip_response(response, wip_id_string)

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    def _handle_wip_response(
        self,
        response: httpx.Response,
        wip_id_string: str,
    ) -> WIPLookupResult:
        """Handle WIP lookup response and map errors."""
        if response.status_code == 200:
            data = response.json()
            return WIPLookupResult.from_api_response(data)

        if response.status_code == 404:
            raise WIPNotFoundError(wip_id_string)

        # Handle other errors
        self._raise_backend_error(response, wip_id_string)

    # ================================================================
    # Process Start (착공)
    # ================================================================

    @with_auth(AuthMode.JWT)
    async def start_process(
        self,
        wip_int_id: int,
        request: ProcessStartRequest,
    ) -> Dict[str, Any]:
        """
        Start a process on WIP item (착공).

        Uses JWT authentication for operator tracking.
        Automatically refreshes token on 401.

        Args:
            wip_int_id: WIP integer ID (from lookup)
            request: Process start request data

        Returns:
            Backend response with wip_item and message

        Raises:
            WIPNotFoundError: If WIP not found
            PrerequisiteNotMetError: If previous process not completed (BR-003)
            InvalidWIPStatusError: If WIP status doesn't allow start
            TokenExpiredError: If token expired and refresh failed
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/wip-items/{wip_int_id}/start-process"

        payload = request.model_dump(exclude_none=True)
        if request.started_at:
            payload["started_at"] = request.started_at.isoformat()

        # Use JWT authentication for operator tracking
        headers = self._get_jwt_header()

        try:
            response = await self._client.post(url, json=payload, headers=headers)
            return self._handle_process_response(
                response,
                str(wip_int_id),
                request.process_id,
                "start_process",
            )

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    # ================================================================
    # Process Complete (완공)
    # ================================================================

    @with_auth(AuthMode.JWT)
    async def complete_process(
        self,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        request: ProcessCompleteRequest,
    ) -> Dict[str, Any]:
        """
        Complete a process on WIP item (완공).

        Uses JWT authentication for operator tracking.
        Automatically refreshes token on 401.

        Args:
            wip_int_id: WIP integer ID (from lookup)
            process_id: Process ID being completed
            operator_id: Operator ID
            request: Process complete request data

        Returns:
            Backend response with process_history and wip_item

        Raises:
            WIPNotFoundError: If WIP not found
            DuplicatePassError: If duplicate PASS not allowed (BR-004)
            TokenExpiredError: If token expired and refresh failed
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/wip-items/{wip_int_id}/complete-process"
        params = {
            "process_id": process_id,
            "operator_id": operator_id,
        }

        payload = request.model_dump(exclude_none=True)
        if request.started_at:
            payload["started_at"] = request.started_at.isoformat()
        if request.completed_at:
            payload["completed_at"] = request.completed_at.isoformat()

        # Use JWT authentication for operator tracking
        headers = self._get_jwt_header()

        try:
            response = await self._client.post(url, params=params, json=payload, headers=headers)
            return self._handle_process_response(
                response,
                str(wip_int_id),
                process_id,
                "complete_process",
            )

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    # ================================================================
    # Serial Conversion
    # ================================================================

    @with_auth(AuthMode.JWT)
    async def convert_to_serial(
        self,
        wip_int_id: int,
        request: SerialConvertRequest,
    ) -> Dict[str, Any]:
        """
        Convert WIP to serial number (시리얼 변환).

        Uses JWT authentication for operator tracking.
        Automatically refreshes token on 401.

        Args:
            wip_int_id: WIP integer ID (from lookup)
            request: Serial conversion request data

        Returns:
            Backend response with serial and wip_item

        Raises:
            WIPNotFoundError: If WIP not found
            InvalidWIPStatusError: If WIP not in COMPLETED status
            TokenExpiredError: If token expired and refresh failed
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/wip-items/{wip_int_id}/convert-to-serial"

        payload = request.model_dump(exclude_none=True)

        # Use JWT authentication for operator tracking
        headers = self._get_jwt_header()

        try:
            response = await self._client.post(url, json=payload, headers=headers)

            if response.status_code in (200, 201):
                return response.json()

            if response.status_code == 404:
                raise WIPNotFoundError(str(wip_int_id))

            self._raise_backend_error(response, str(wip_int_id))

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    # ================================================================
    # Error Handling
    # ================================================================

    def _handle_process_response(
        self,
        response: httpx.Response,
        wip_id: str,
        process_id: int,
        operation: str,
    ) -> Dict[str, Any]:
        """Handle process API response and map errors."""
        if response.status_code in (200, 201):
            return response.json()

        if response.status_code == 404:
            raise WIPNotFoundError(wip_id)

        # Try to parse error response
        try:
            error_data = response.json()
            error_code = error_data.get("error", "")
            error_message = error_data.get("message", "")

            if error_code == "PREREQUISITE_NOT_MET":
                # Extract required process from message if possible
                required = process_id - 1 if process_id > 1 else 0
                raise PrerequisiteNotMetError(wip_id, process_id, required)

            if error_code == "DUPLICATE_PASS":
                raise DuplicatePassError(wip_id, process_id)

            if error_code == "INVALID_WIP_STATUS":
                status = error_data.get("detail", "unknown")
                raise InvalidWIPStatusError(wip_id, status, operation)

            # Generic backend error
            raise BackendError(
                message=error_message or f"Backend error: {response.status_code}",
                code=error_code or "BACKEND_ERROR",
                response=error_data,
                status_code=response.status_code,
            )

        except (ValueError, KeyError):
            # Could not parse error response
            raise BackendError(
                message=f"Backend error: {response.status_code} - {response.text[:200]}",
                code="BACKEND_ERROR",
                status_code=response.status_code,
            )

    def _raise_backend_error(self, response: httpx.Response, wip_id: str) -> None:
        """Raise appropriate BackendError based on response."""
        try:
            error_data = response.json()

            # Try different error code formats:
            # 1. Backend StandardErrorResponse: {"error_code": "CODE", "message": "..."}
            # 2. Legacy format: {"error": "CODE", "message": "..."}
            error_code = (
                error_data.get("error_code")
                or error_data.get("error")
                or "BACKEND_ERROR"
            )

            # Try different error message formats:
            # 1. Backend/Legacy: {"message": "..."}
            # 2. FastAPI HTTPException: {"detail": "..."}
            error_message = (
                error_data.get("message")
                or error_data.get("detail")
                or f"HTTP {response.status_code}"
            )

            # Handle detail as dict (validation errors)
            if isinstance(error_message, dict):
                error_message = str(error_message)

            raise BackendError(
                message=error_message,
                code=error_code,
                response=error_data,
                status_code=response.status_code,
            )

        except (ValueError, KeyError):
            raise BackendError(
                message=f"Backend error: {response.status_code}",
                code="BACKEND_ERROR",
                status_code=response.status_code,
            )

    # ================================================================
    # Authentication (Operator Login)
    # ================================================================

    async def login(
        self,
        username: str,
        password: str,
        station_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Login to Backend and get operator credentials.

        Args:
            username: Operator username
            password: Operator password
            station_id: Optional station ID for station_api_key generation

        Returns:
            Login response with access_token, user info, and station_api_key (if station_id provided)

        Raises:
            BackendError: If login fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        # Use configured station_id if not provided
        effective_station_id = station_id or self._config.station_id

        url = "/api/v1/auth/login/json"
        payload = {
            "username": username,
            "password": password,
        }
        if effective_station_id:
            payload["station_id"] = effective_station_id

        try:
            response = await self._client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Operator logged in: {username}")
                return data

            # Handle error response
            try:
                error_data = response.json()
                error_message = error_data.get("message", "Login failed")
            except (ValueError, KeyError):
                error_message = f"Login failed: HTTP {response.status_code}"

            raise BackendError(
                message=error_message,
                code="LOGIN_FAILED",
                status_code=response.status_code,
            )

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    async def refresh_access_token(
        self,
        refresh_token: str,
        station_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token
            station_id: Optional station ID for station_api_key refresh

        Returns:
            Dict with new access_token, refresh_token, expires_in, and station_api_key

        Raises:
            TokenRefreshError: If refresh fails
            BackendConnectionError: If connection fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        # Use configured station_id if not provided
        effective_station_id = station_id or self._config.station_id

        url = "/api/v1/auth/refresh"
        payload = {"refresh_token": refresh_token}
        if effective_station_id:
            payload["station_id"] = effective_station_id

        try:
            response = await self._client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info("Access token refreshed successfully")
                return data

            # Handle error response
            try:
                error_data = response.json()
                error_message = (
                    error_data.get("message")
                    or error_data.get("detail")
                    or "Token refresh failed"
                )
            except (ValueError, KeyError):
                error_message = f"Token refresh failed: HTTP {response.status_code}"

            raise TokenRefreshError(error_message)

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    @with_auth(AuthMode.JWT)
    async def get_current_user(self) -> Dict[str, Any]:
        """
        Get current user info using access token.

        Uses JWT authentication with automatic token refresh on 401.

        Returns:
            User info dict

        Raises:
            TokenExpiredError: If token expired and refresh failed
            BackendError: If request fails or token is invalid
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/auth/me"

        try:
            headers = self._get_jwt_header()
            response = await self._client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()

            raise BackendError(
                message="Invalid or expired token",
                code="INVALID_TOKEN",
                status_code=response.status_code,
            )

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    # ================================================================
    # Process List (공정 목록)
    # ================================================================

    async def get_processes(self) -> list[Dict[str, Any]]:
        """
        Get list of active processes from Backend MES.

        Uses optional JWT authentication (falls back to no auth if not logged in).

        Returns:
            List of process dicts with id, process_number, process_code,
            process_name_ko, process_name_en, etc.

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/processes/active"

        try:
            # Use JWT if available, otherwise no auth
            headers = self._get_jwt_header()
            response = await self._client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # Handle wrapped response format
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
                return data

            raise BackendError(
                message=f"Failed to get processes: HTTP {response.status_code}",
                code="BACKEND_ERROR",
                status_code=response.status_code,
            )

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    # ================================================================
    # Process Header Operations (Station/Batch tracking)
    # ================================================================

    @with_auth(AuthMode.API_KEY)
    async def open_header(
        self,
        request: ProcessHeaderOpenRequest,
    ) -> ProcessHeaderResponse:
        """
        Open a process header for station/batch tracking.

        This is called when a batch starts processing. If a header already exists
        for the same station+batch+process combination, it will be returned.

        Uses API Key authentication (service-level call).

        Args:
            request: Header open request with station_id, batch_id, process_id, etc.

        Returns:
            ProcessHeaderResponse with header ID and details

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/process-headers/open"

        payload = request.model_dump(exclude_none=True)

        try:
            headers = self._get_api_key_header()
            response = await self._client.post(url, json=payload, headers=headers)

            if response.status_code in (200, 201):
                data = response.json()
                logger.info(
                    f"Process header opened: id={data['id']}, "
                    f"station={request.station_id}, batch={request.batch_id}"
                )
                return ProcessHeaderResponse.from_api_response(data)

            # Handle error
            self._raise_backend_error(response, f"station={request.station_id}")

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    @with_auth(AuthMode.API_KEY)
    async def close_header(
        self,
        header_id: int,
        status: str = "CLOSED",
    ) -> ProcessHeaderResponse:
        """
        Close a process header when batch completes.

        Uses API Key authentication (service-level call).

        Args:
            header_id: Header ID to close
            status: Final status (CLOSED or CANCELLED)

        Returns:
            ProcessHeaderResponse with updated header details

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/process-headers/{header_id}/close"
        params = {"status": status}

        try:
            headers = self._get_api_key_header()
            response = await self._client.post(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Process header closed: id={header_id}, status={status}")
                return ProcessHeaderResponse.from_api_response(data)

            # Handle error
            self._raise_backend_error(response, f"header_id={header_id}")

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    @with_auth(AuthMode.API_KEY)
    async def get_header(
        self,
        header_id: int,
    ) -> ProcessHeaderResponse:
        """
        Get process header by ID.

        Uses API Key authentication (service-level call).

        Args:
            header_id: Header ID to retrieve

        Returns:
            ProcessHeaderResponse with header details

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails or header not found
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/process-headers/{header_id}"

        try:
            headers = self._get_api_key_header()
            response = await self._client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return ProcessHeaderResponse.from_api_response(data)

            if response.status_code == 404:
                raise BackendError(
                    message=f"Process header not found: {header_id}",
                    code="HEADER_NOT_FOUND",
                    status_code=404,
                )

            self._raise_backend_error(response, f"header_id={header_id}")

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    @with_auth(AuthMode.API_KEY)
    async def get_open_header(
        self,
        station_id: str,
        batch_id: str,
        process_id: int,
    ) -> Optional[ProcessHeaderResponse]:
        """
        Get the currently open header for a station+batch+process combination.

        Uses API Key authentication (service-level call).

        Args:
            station_id: Station identifier
            batch_id: Batch identifier
            process_id: Process ID

        Returns:
            ProcessHeaderResponse if an open header exists, None otherwise

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/process-headers/open"
        params = {
            "station_id": station_id,
            "batch_id": batch_id,
            "process_id": process_id,
        }

        try:
            headers = self._get_api_key_header()
            response = await self._client.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data:
                    return ProcessHeaderResponse.from_api_response(data)
                return None

            if response.status_code == 404:
                return None

            self._raise_backend_error(response, f"station={station_id}")

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    @with_auth(AuthMode.API_KEY)
    async def list_headers(
        self,
        station_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        process_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[ProcessHeaderSummary]:
        """
        List process headers with optional filters.

        Uses API Key authentication (service-level call).

        Args:
            station_id: Optional filter by station ID
            batch_id: Optional filter by batch ID
            process_id: Optional filter by process ID
            status: Optional filter by status (OPEN, CLOSED, CANCELLED)
            limit: Maximum records to return (default 100)

        Returns:
            List of ProcessHeaderSummary

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/process-headers/"
        params: Dict[str, Any] = {"limit": limit}
        if station_id:
            params["station_id"] = station_id
        if batch_id:
            params["batch_id"] = batch_id
        if process_id:
            params["process_id"] = process_id
        if status:
            params["status"] = status

        try:
            headers = self._get_api_key_header()
            response = await self._client.get(url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # Handle wrapped list response
                items = data.get("items", []) if isinstance(data, dict) else data
                return [ProcessHeaderSummary.from_api_response(item) for item in items]

            self._raise_backend_error(response, "list_headers")

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))

    # ================================================================
    # Sequence Pull (CLI-based deployment)
    # ================================================================

    @with_auth(AuthMode.API_KEY)
    async def pull_sequence(
        self,
        sequence_name: str,
        current_version: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> SequencePullResponse:
        """
        Pull sequence package from Backend.

        Uses station's API Key authentication (X-API-Key header).
        The station_id is taken from the BackendConfig.

        Args:
            sequence_name: Name of the sequence to pull
            current_version: Currently installed version (for update check)
            batch_id: Optional batch ID for deployment tracking

        Returns:
            SequencePullResponse with version info and package data if update needed

        Raises:
            BackendConnectionError: If client not connected
            BackendError: If API call fails or sequence not found

        Example:
            >>> response = await client.pull_sequence("psa_sensor_test", "1.0.0")
            >>> if response.needs_update:
            ...     zip_data = base64.b64decode(response.package_data)
            ...     # Extract and install
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        if not self._config.station_id:
            raise BackendError(
                message="station_id not configured in backend config",
                code="CONFIG_ERROR",
            )

        url = f"/api/v1/sequences/{sequence_name}/pull"

        request = SequencePullRequest(
            station_id=self._config.station_id,
            batch_id=batch_id,
            current_version=current_version,
        )
        payload = request.model_dump(exclude_none=True)

        try:
            headers = self._get_api_key_header()
            response = await self._client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"Sequence pull: {sequence_name} v{data['version']}, "
                    f"needs_update={data['needs_update']}"
                )
                return SequencePullResponse.from_api_response(data)

            if response.status_code == 404:
                raise BackendError(
                    message=f"Sequence not found: {sequence_name}",
                    code="SEQUENCE_NOT_FOUND",
                    status_code=404,
                )

            if response.status_code == 401:
                raise BackendError(
                    message="Station API key required or invalid",
                    code="UNAUTHORIZED",
                    status_code=401,
                )

            if response.status_code == 403:
                raise BackendError(
                    message="Station ID mismatch with API key",
                    code="FORBIDDEN",
                    status_code=403,
                )

            self._raise_backend_error(response, f"sequence={sequence_name}")

        except httpx.RequestError as e:
            raise BackendConnectionError(self._config.url, str(e))
