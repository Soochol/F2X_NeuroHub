"""
Work Service for start/complete operations with threading support.

Refactored to use single APIWorker instead of multiple specific workers.
"""
from PySide6.QtCore import QObject, Signal
from typing import Dict
from datetime import datetime
from .api_client import APIClient
from .workers import APIWorker
import logging

logger = logging.getLogger(__name__)


class WorkService(QObject):
    """Handle work start and completion API calls with non-blocking threading."""

    # Signals for threaded operations
    work_started = Signal(dict)     # Work started successfully
    work_completed = Signal(dict)   # Work completed successfully
    stats_ready = Signal(dict)      # Statistics fetched
    error_occurred = Signal(str)    # Operation failed

    def __init__(self, api_client: APIClient, config):
        super().__init__()
        self.api_client = api_client
        self.config = config
        self._active_workers = []

    def start_work(self, lot_number: str, worker_id: str):
        """
        Start work for LOT - POST /api/v1/process/start (non-blocking)
        """
        logger.info(f"Starting work (threaded) for LOT: {lot_number}")

        data = {
            "lot_number": lot_number,
            "line_id": self.config.line_id,
            "process_id": self.config.process_id,
            "process_name": self.config.process_name,
            "equipment_id": self.config.equipment_id,
            "worker_id": worker_id,
            "start_time": datetime.now().isoformat()
        }

        worker = APIWorker(
            api_client=self.api_client,
            operation="start_work",
            method="POST",
            endpoint="/api/v1/process/start",
            data=data
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def complete_work(self, json_data: Dict):
        """
        Complete work from JSON file - POST /api/v1/process/complete (non-blocking)
        """
        lot_number = json_data.get('lot_number', 'UNKNOWN')
        logger.info(f"Completing work (threaded) for LOT: {lot_number}")

        worker = APIWorker(
            api_client=self.api_client,
            operation="complete_work",
            method="POST",
            endpoint="/api/v1/process/complete",
            data=json_data
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def get_today_stats(self):
        """
        Get today's statistics for current process (non-blocking).
        """
        logger.debug(f"Fetching stats (threaded) for process: {self.config.process_id}")

        worker = APIWorker(
            api_client=self.api_client,
            operation="get_stats",
            method="GET",
            endpoint="/api/v1/analytics/daily",
            params={"process_id": self.config.process_id}
        )
        worker.success.connect(self._on_api_success)
        worker.error.connect(self._on_api_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def _on_api_success(self, operation: str, result: dict):
        """Handle successful API call based on operation type."""
        logger.info(f"API success [{operation}]: {result}")

        if operation == "start_work":
            self.work_started.emit(result)
        elif operation == "complete_work":
            self.work_completed.emit(result)
        elif operation == "get_stats":
            self.stats_ready.emit(result)

    def _on_api_error(self, operation: str, error_msg: str):
        """Handle API error based on operation type."""
        logger.error(f"API error [{operation}]: {error_msg}")

        if operation == "start_work":
            self.error_occurred.emit(f"착공 등록 실패: {error_msg}")
        elif operation == "complete_work":
            self.error_occurred.emit(f"완공 처리 실패: {error_msg}")
        elif operation == "get_stats":
            # Stats failure is silent, return defaults
            default_stats = {
                "started": 0,
                "completed": 0,
                "passed": 0,
                "failed": 0,
                "in_progress": 0
            }
            self.stats_ready.emit(default_stats)

    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {worker.operation}")

    def cancel_all_operations(self):
        """Cancel all active operations and clean up workers."""
        logger.info(f"Cancelling {len(self._active_workers)} active workers")
        for worker in self._active_workers[:]:
            if hasattr(worker, 'cancel'):
                worker.cancel()
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)
        self._active_workers.clear()
        logger.info("All workers cancelled")