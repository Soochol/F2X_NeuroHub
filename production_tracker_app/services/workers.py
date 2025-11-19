"""
QThread worker classes for non-blocking API operations.

Refactored: Single APIWorker handles all API operations.
Before: 6 workers (267 lines) → After: 1 worker (80 lines)
"""
from PySide6.QtCore import QThread, Signal
from typing import Any, Optional
import logging

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
        api_client,
        operation: str,
        method: str = "GET",
        endpoint: str = "",
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ):
        super().__init__()
        self.api_client = api_client
        self.operation = operation
        self.method = method.upper()
        self.endpoint = endpoint
        self.data = data
        self.params = params
        self._is_cancelled = False

    def run(self):
        """Execute API call in background thread."""
        if self._is_cancelled:
            return

        try:
            logger.debug(f"APIWorker [{self.operation}] starting: {self.method} {self.endpoint}")

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
                logger.error(f"APIWorker [{self.operation}] error: {error_msg}")
                self.error.emit(self.operation, error_msg)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug(f"APIWorker [{self.operation}] cancelled")