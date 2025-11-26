"""
QThread worker classes for non-blocking API operations.

Refactored: Single APIWorker handles all API operations.
Before: 6 workers (267 lines) -> After: 1 worker (80 lines)
"""
import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class APIWorker(QThread):
    """
    Universal API worker for all background operations.

    Usage:
        # POST request
        worker = APIWorker(
            api_client=self.api_client,
            operation="start_work",
            method="POST",
            endpoint="/api/v1/process/start",
            data={"lot_number": "LOT001", ...}
        )
        worker.success.connect(self.on_success)
        worker.error.connect(self.on_error)
        worker.start()

        # GET request
        worker = APIWorker(
            api_client=self.api_client,
            operation="load_stats",
            method="GET",
            endpoint="/api/v1/analytics/daily",
            params={"process_id": "P001"}
        )
    """

    success = Signal(str, object)  # (operation_name, result)
    error = Signal(str, str)       # (operation_name, error_message)

    def __init__(
        self,
        api_client: Any,
        operation: str,
        method: str = "GET",
        endpoint: str = "",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__()
        self.api_client: Any = api_client
        self.operation: str = operation
        self.method: str = method.upper()
        self.endpoint: str = endpoint
        self.data: Optional[Dict[str, Any]] = data
        self.params: Optional[Dict[str, Any]] = params
        self._is_cancelled: bool = False

    def run(self) -> None:
        """Execute API call in background thread."""
        if self._is_cancelled:
            return

        try:
            logger.debug(
                f"APIWorker [{self.operation}] starting: "
                f"{self.method} {self.endpoint}"
            )

            if self.method == "GET":
                result = self.api_client.get(self.endpoint, self.params)
            elif self.method == "POST":
                result = self.api_client.post(self.endpoint, self.data)
            elif self.method == "PUT":
                result = self.api_client.put(self.endpoint, self.data)
            elif self.method == "DELETE":
                result = self.api_client.delete(self.endpoint)
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")

            if not self._is_cancelled:
                self.success.emit(self.operation, result)
                logger.debug(f"APIWorker [{self.operation}] completed")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)

                # Log response body for HTTPError (for debugging)
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    response_body = e.response.text[:500]
                    logger.error(
                        f"APIWorker [{self.operation}] "
                        f"Response body: {response_body}"
                    )

                logger.error(f"APIWorker [{self.operation}] error: {error_msg}")
                self.error.emit(self.operation, error_msg)

    def cancel(self) -> None:
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug(f"APIWorker [{self.operation}] cancelled")

