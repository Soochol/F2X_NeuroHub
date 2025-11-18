"""
QThread worker classes for non-blocking API operations.
"""
from PySide6.QtCore import QThread, Signal
from typing import Dict, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)


class APIWorker(QThread):
    """Base worker for API operations."""

    result_ready = Signal(object)  # Success result
    error_occurred = Signal(str)   # Error message

    def __init__(self, api_call: Callable, *args, **kwargs):
        """
        Initialize API worker.

        Args:
            api_call: Callable that performs the API operation
            *args, **kwargs: Arguments to pass to the API call
        """
        super().__init__()
        self.api_call = api_call
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    def run(self):
        """Execute API call in background thread."""
        if self._is_cancelled:
            return

        try:
            logger.debug(f"API worker starting: {self.api_call.__name__}")
            result = self.api_call(*self.args, **self.kwargs)

            if not self._is_cancelled:
                self.result_ready.emit(result)
                logger.debug(f"API worker completed: {self.api_call.__name__}")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)
                logger.error(f"API worker error in {self.api_call.__name__}: {error_msg}")
                self.error_occurred.emit(error_msg)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug(f"API worker cancelled: {self.api_call.__name__}")


class LoginWorker(QThread):
    """Worker for login operations."""

    login_success = Signal(dict)  # User data
    login_failed = Signal(str)     # Error message

    def __init__(self, api_client, username: str, password: str):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.password = password
        self._is_cancelled = False

    def run(self):
        """Perform login in background."""
        if self._is_cancelled:
            return

        try:
            logger.info(f"Login worker starting for user: {self.username}")
            response = self.api_client.post('/api/v1/auth/login', {
                'username': self.username,
                'password': self.password
            })

            if not self._is_cancelled:
                self.login_success.emit(response)
                logger.info(f"Login worker completed for user: {self.username}")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)
                logger.error(f"Login worker error: {error_msg}")
                self.login_failed.emit(error_msg)

    def cancel(self):
        """Cancel the login operation."""
        self._is_cancelled = True
        logger.debug(f"Login worker cancelled for user: {self.username}")


class StartWorkWorker(QThread):
    """Worker for start work operations."""

    work_started = Signal(dict)    # API response
    work_failed = Signal(str)      # Error message

    def __init__(self, api_client, lot_number: str, worker_id: str, config):
        super().__init__()
        self.api_client = api_client
        self.lot_number = lot_number
        self.worker_id = worker_id
        self.config = config
        self._is_cancelled = False

    def run(self):
        """Start work in background."""
        if self._is_cancelled:
            return

        try:
            from datetime import datetime

            data = {
                "lot_number": self.lot_number,
                "line_id": self.config.line_id,
                "process_id": self.config.process_id,
                "process_name": self.config.process_name,
                "equipment_id": self.config.equipment_id,
                "worker_id": self.worker_id,
                "start_time": datetime.now().isoformat()
            }

            logger.info(f"Start work worker executing for LOT: {self.lot_number}")
            response = self.api_client.post("/api/v1/process/start", data)

            if not self._is_cancelled:
                self.work_started.emit(response)
                logger.info(f"Start work worker completed for LOT: {self.lot_number}")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)
                logger.error(f"Start work worker error: {error_msg}")
                self.work_failed.emit(error_msg)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug(f"Start work worker cancelled for LOT: {self.lot_number}")


class CompleteWorkWorker(QThread):
    """Worker for complete work operations."""

    work_completed = Signal(dict)  # API response
    work_failed = Signal(str)       # Error message

    def __init__(self, api_client, json_data: Dict):
        super().__init__()
        self.api_client = api_client
        self.json_data = json_data
        self._is_cancelled = False

    def run(self):
        """Complete work in background."""
        if self._is_cancelled:
            return

        try:
            lot_number = self.json_data.get('lot_number', 'UNKNOWN')
            logger.info(f"Complete work worker executing for LOT: {lot_number}")

            response = self.api_client.post("/api/v1/process/complete", self.json_data)

            if not self._is_cancelled:
                self.work_completed.emit(response)
                logger.info(f"Complete work worker completed for LOT: {lot_number}")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)
                logger.error(f"Complete work worker error: {error_msg}")
                self.work_failed.emit(error_msg)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug("Complete work worker cancelled")


class StatsWorker(QThread):
    """Worker for statistics refresh operations."""

    stats_ready = Signal(dict)     # Statistics data
    stats_failed = Signal(str)     # Error message (silent failure)

    def __init__(self, api_client, process_id: str):
        super().__init__()
        self.api_client = api_client
        self.process_id = process_id
        self._is_cancelled = False

    def run(self):
        """Fetch statistics in background."""
        if self._is_cancelled:
            return

        try:
            logger.debug(f"Stats worker executing for process: {self.process_id}")
            params = {"process_id": self.process_id}
            response = self.api_client.get("/api/v1/analytics/daily", params)

            if not self._is_cancelled:
                self.stats_ready.emit(response)
                logger.debug("Stats worker completed")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)
                logger.debug(f"Stats worker error (silent): {error_msg}")
                # Return default stats on error
                default_stats = {
                    "started": 0,
                    "completed": 0,
                    "passed": 0,
                    "failed": 0,
                    "in_progress": 0
                }
                self.stats_ready.emit(default_stats)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug("Stats worker cancelled")


class TokenValidationWorker(QThread):
    """Worker for token validation operations."""

    validation_success = Signal(dict)  # User data
    validation_failed = Signal(str)     # Error message

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self._is_cancelled = False

    def run(self):
        """Validate token in background."""
        if self._is_cancelled:
            return

        try:
            logger.info("Token validation worker executing")
            user = self.api_client.get('/api/v1/auth/me')

            if not self._is_cancelled:
                self.validation_success.emit(user)
                logger.info("Token validation worker completed")

        except Exception as e:
            if not self._is_cancelled:
                error_msg = str(e)
                logger.error(f"Token validation worker error: {error_msg}")
                self.validation_failed.emit(error_msg)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
        logger.debug("Token validation worker cancelled")
