"""
BackendClient for Station Service.

Provides async HTTP client for Backend WIP process operations:
- WIP lookup (string ID -> int ID)
- Process start (착공)
- Process complete (완공)
- Serial conversion (시리얼 변환)
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from station_service.core.exceptions import (
    BackendConnectionError,
    BackendError,
    DuplicatePassError,
    InvalidWIPStatusError,
    PrerequisiteNotMetError,
    WIPNotFoundError,
)
from station_service.models.config import BackendConfig
from station_service.sync.models import (
    ProcessCompleteRequest,
    ProcessStartRequest,
    SerialConvertRequest,
    WIPLookupResult,
)

logger = logging.getLogger(__name__)


class BackendClient:
    """
    Async HTTP client for Backend WIP process operations.

    Handles:
    - WIP lookup via scan endpoint (string -> int ID)
    - Process start (착공) API
    - Process complete (완공) API
    - Serial conversion API
    - Error mapping from Backend to Station exceptions

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

    async def lookup_wip(
        self,
        wip_id_string: str,
        process_id: Optional[int] = None,
    ) -> WIPLookupResult:
        """
        Lookup WIP by string ID to get integer ID.

        Uses the scan endpoint to validate WIP and get its data.

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

        try:
            response = await self._client.post(url, params=params)
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

    async def start_process(
        self,
        wip_int_id: int,
        request: ProcessStartRequest,
    ) -> Dict[str, Any]:
        """
        Start a process on WIP item (착공).

        Args:
            wip_int_id: WIP integer ID (from lookup)
            request: Process start request data

        Returns:
            Backend response with wip_item and message

        Raises:
            WIPNotFoundError: If WIP not found
            PrerequisiteNotMetError: If previous process not completed (BR-003)
            InvalidWIPStatusError: If WIP status doesn't allow start
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/wip-items/{wip_int_id}/start-process"

        payload = request.model_dump(exclude_none=True)
        if request.started_at:
            payload["started_at"] = request.started_at.isoformat()

        try:
            response = await self._client.post(url, json=payload)
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

    async def complete_process(
        self,
        wip_int_id: int,
        process_id: int,
        operator_id: int,
        request: ProcessCompleteRequest,
    ) -> Dict[str, Any]:
        """
        Complete a process on WIP item (완공).

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
        if request.completed_at:
            payload["completed_at"] = request.completed_at.isoformat()

        try:
            response = await self._client.post(url, params=params, json=payload)
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

    async def convert_to_serial(
        self,
        wip_int_id: int,
        request: SerialConvertRequest,
    ) -> Dict[str, Any]:
        """
        Convert WIP to serial number (시리얼 변환).

        Args:
            wip_int_id: WIP integer ID (from lookup)
            request: Serial conversion request data

        Returns:
            Backend response with serial and wip_item

        Raises:
            WIPNotFoundError: If WIP not found
            InvalidWIPStatusError: If WIP not in COMPLETED status
            BackendError: If API call fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = f"/api/v1/wip-items/{wip_int_id}/convert-to-serial"

        payload = request.model_dump(exclude_none=True)

        try:
            response = await self._client.post(url, json=payload)

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
            error_code = error_data.get("error", "BACKEND_ERROR")
            error_message = error_data.get("message", f"HTTP {response.status_code}")

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
    ) -> Dict[str, Any]:
        """
        Login to Backend and get operator credentials.

        Args:
            username: Operator username
            password: Operator password

        Returns:
            Login response with access_token and user info

        Raises:
            BackendError: If login fails
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/auth/login/json"
        payload = {
            "username": username,
            "password": password,
        }

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

    async def get_current_user(
        self,
        access_token: str,
    ) -> Dict[str, Any]:
        """
        Get current user info using access token.

        Args:
            access_token: JWT access token

        Returns:
            User info dict

        Raises:
            BackendError: If request fails or token is invalid
        """
        if not self._client:
            raise BackendConnectionError(self._config.url, "Client not connected")

        url = "/api/v1/auth/me"

        try:
            # Use token for this request
            headers = {"Authorization": f"Bearer {access_token}"}
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
