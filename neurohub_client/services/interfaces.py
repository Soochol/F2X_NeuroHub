"""
Service Interfaces for Production Tracker App.

Protocol-based interfaces that define contracts for services.
Using Protocol instead of ABC to avoid metaclass conflicts with QObject.

This enables:
- Dependency injection for testability
- Mock implementations for unit testing
- Clear API contracts between components
- Compatible with Qt's QObject inheritance
"""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class IAPIClient(Protocol):
    """
    Interface for REST API communication.

    Implementations should handle:
    - HTTP request/response
    - Authentication token management
    - Error handling and retries
    """

    def get_base_url(self) -> str:
        """Get the API base URL."""
        ...

    def set_token(self, token: str) -> None:
        """Set JWT token for authenticated requests."""
        ...

    def clear_token(self) -> None:
        """Clear JWT token."""
        ...

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response data (JSON decoded)

        Raises:
            ConnectionError: Backend unreachable
            Timeout: Request timeout
            HTTPError: HTTP error response
        """
        ...

    def post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """
        Perform POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            Response data (JSON decoded)

        Raises:
            ConnectionError: Backend unreachable
            Timeout: Request timeout
            HTTPError: HTTP error response
        """
        ...

    def get_production_lines(self) -> List[Dict[str, Any]]:
        """Get list of active production lines."""
        ...

    def get_equipment(self) -> List[Dict[str, Any]]:
        """Get list of active equipment."""
        ...

    def get_processes(self) -> List[Dict[str, Any]]:
        """Get list of active processes."""
        ...


@runtime_checkable
class IAuthService(Protocol):
    """
    Interface for authentication lifecycle management.

    Implementations should handle:
    - Login/logout operations
    - Token validation and refresh
    - User session management
    """

    @property
    def access_token(self) -> Optional[str]:
        """Get current access token."""
        ...

    @property
    def current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user data."""
        ...

    def login(self, username: str, password: str) -> None:
        """
        Initiate login process (non-blocking).

        Args:
            username: User login name
            password: User password

        Emits:
            login_success: On successful authentication
            auth_error: On authentication failure
        """
        ...

    def logout(self) -> None:
        """Clear authentication state and stop auto-refresh."""
        ...

    def validate_token(self) -> None:
        """
        Validate current token (non-blocking).

        Emits:
            token_validated: On valid token
            auth_error: On invalid token
        """
        ...

    def get_current_user_id(self) -> str:
        """
        Get current user's identifier for worker tracking.

        Returns:
            User's full name or username, 'UNKNOWN' if not authenticated
        """
        ...

    def get_current_username(self) -> str:
        """
        Get current user's login username.

        Returns:
            Username or 'UNKNOWN' if not authenticated
        """
        ...

    def cancel_all_operations(self) -> None:
        """Cancel all pending authentication operations."""
        ...


@runtime_checkable
class IWorkService(Protocol):
    """
    Interface for work start/complete operations.

    Implementations should handle:
    - Work lifecycle (start, complete)
    - Threaded API communication
    - Error handling and user-friendly messages
    """

    def start_work(self, wip_id: str, worker_id: str) -> None:
        """
        Start work for WIP (non-blocking).

        Args:
            wip_id: WIP ID (required)
            worker_id: Worker identifier

        Emits:
            work_started: On successful start
            error_occurred: On failure
        """
        ...

    def start_work_sync(self, worker_id: str, wip_id: str) -> Dict[str, Any]:
        """
        Start work synchronously (for TCP server use).

        Args:
            worker_id: Worker identifier
            wip_id: WIP ID (required)

        Returns:
            Dict with 'success' (bool) and 'error' or 'data'
        """
        ...

    def complete_work(self, json_data: Dict[str, Any]) -> None:
        """
        Complete work with completion data (non-blocking).

        Args:
            json_data: Completion data containing wip_id and result

        Emits:
            work_completed: On successful completion
            error_occurred: On failure
        """
        ...

    def convert_wip_to_serial(self, wip_id: int, operator_id: int) -> None:
        """
        Convert WIP to Serial (non-blocking).

        Args:
            wip_id: WIP item ID
            operator_id: Operator ID

        Emits:
            serial_converted: On successful conversion
            error_occurred: On failure
        """
        ...

    def cancel_all_operations(self) -> None:
        """Cancel all pending work operations."""
        ...


@runtime_checkable
class IBarcodeService(Protocol):
    """
    Interface for barcode scanning service.

    Implementations should handle:
    - Keyboard input processing
    - Barcode format validation
    - Signal emission for valid/invalid barcodes
    """

    def process_key(self, key: str) -> None:
        """
        Process a keyboard key input.

        Args:
            key: Single character or '\\n' for Enter
        """
        ...

    def clear_buffer(self) -> None:
        """Clear the input buffer."""
        ...


@runtime_checkable
class ICompletionWatcher(Protocol):
    """
    Interface for JSON file completion monitoring.

    Implementations should handle:
    - Directory watching for new files
    - JSON file parsing and validation
    - File lifecycle management (pending → completed/error)
    """

    def stop(self) -> None:
        """Stop monitoring."""
        ...


@runtime_checkable
class ITCPServer(Protocol):
    """
    Interface for TCP server communication with equipment.

    Implementations should handle:
    - TCP socket listening
    - JSON message parsing (START, COMPLETE)
    - Signal emission for received data
    """

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        ...

    def start(self) -> bool:
        """
        Start the TCP server.

        Returns:
            True if started successfully
        """
        ...

    def stop(self) -> None:
        """Stop the TCP server."""
        ...

    def set_services(self, work_service: Any, auth_service: Any) -> None:
        """
        Set service references for synchronous API calls.

        Args:
            work_service: Work service for API calls
            auth_service: Auth service for user identification
        """
        ...


@runtime_checkable
class IHistoryManager(Protocol):
    """
    Interface for event history management.

    Implementations should handle:
    - Event recording (start, complete, error)
    - Persistent storage
    - History retrieval and filtering
    """

    def add_start_event(
        self,
        wip_id: str,
        lot_number: str,
        process_name: str,
        success: bool = True,
        message: str = ""
    ) -> None:
        """Record a work start event."""
        ...

    def add_complete_event(
        self,
        wip_id: str,
        lot_number: str,
        result: str,
        process_name: str,
        duration_seconds: Optional[int] = None,
        message: str = ""
    ) -> None:
        """Record a work completion event."""
        ...

    def add_error_event(
        self,
        wip_id: str,
        lot_number: str,
        error_message: str,
        process_name: str
    ) -> None:
        """Record an error event."""
        ...

    def get_today_events(self) -> List[Dict[str, Any]]:
        """Get all events for today."""
        ...
