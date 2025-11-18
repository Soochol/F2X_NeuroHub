"""
Work Service for start/complete operations with threading support.
"""
from PySide6.QtCore import QObject, Signal
from typing import Dict, Optional
from datetime import datetime
from .api_client import APIClient
from .workers import StartWorkWorker, CompleteWorkWorker, StatsWorker
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

        Args:
            lot_number: LOT number from barcode
            worker_id: Current worker ID

        Emits:
            work_started: On success with API response
            error_occurred: On failure with error message
        """
        logger.info(f"Starting work (threaded) for LOT: {lot_number}, Process: {self.config.process_name}")

        worker = StartWorkWorker(self.api_client, lot_number, worker_id, self.config)
        worker.work_started.connect(self._on_work_started)
        worker.work_failed.connect(self._on_work_failed)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def complete_work(self, json_data: Dict):
        """
        Complete work from JSON file - POST /api/v1/process/complete (non-blocking)

        Args:
            json_data: Completion data from JSON file

        Emits:
            work_completed: On success with API response
            error_occurred: On failure with error message
        """
        lot_number = json_data.get('lot_number', 'UNKNOWN')
        logger.info(f"Completing work (threaded) for LOT: {lot_number}")

        worker = CompleteWorkWorker(self.api_client, json_data)
        worker.work_completed.connect(self._on_work_completed)
        worker.work_failed.connect(self._on_completion_failed)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def get_today_stats(self):
        """
        Get today's statistics for current process (non-blocking).

        Emits:
            stats_ready: Statistics data (always succeeds, returns defaults on error)
        """
        logger.debug(f"Fetching stats (threaded) for process: {self.config.process_id}")

        worker = StatsWorker(self.api_client, self.config.process_id)
        worker.stats_ready.connect(self._on_stats_ready)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        self._active_workers.append(worker)
        worker.start()

    def _on_work_started(self, response: dict):
        """Handle successful work start."""
        logger.info(f"Work started successfully: {response}")
        self.work_started.emit(response)

    def _on_work_failed(self, error_msg: str):
        """Handle work start failure."""
        logger.error(f"Work start failed: {error_msg}")
        self.error_occurred.emit(f"착공 등록 실패: {error_msg}")

    def _on_work_completed(self, response: dict):
        """Handle successful work completion."""
        logger.info(f"Work completed successfully: {response}")
        self.work_completed.emit(response)

    def _on_completion_failed(self, error_msg: str):
        """Handle work completion failure."""
        logger.error(f"Work completion failed: {error_msg}")
        self.error_occurred.emit(f"완공 처리 실패: {error_msg}")

    def _on_stats_ready(self, stats: dict):
        """Handle statistics fetched."""
        logger.debug(f"Stats ready: {stats}")
        self.stats_ready.emit(stats)

    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {type(worker).__name__}")

    def cancel_all_operations(self):
        """Cancel all active operations and clean up workers."""
        logger.info(f"Cancelling {len(self._active_workers)} active workers")
        for worker in self._active_workers[:]:
            if hasattr(worker, 'cancel'):
                worker.cancel()
            if worker.isRunning():
                worker.quit()
                worker.wait(1000)  # Wait up to 1 second
        self._active_workers.clear()
        logger.info("All workers cancelled")
