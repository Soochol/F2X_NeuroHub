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

from utils.exception_handler import safe_cleanup, try_or_log

logger = logging.getLogger(__name__)


class WorkService(QObject):
    """Handle work start and completion API calls with non-blocking threading."""

    # Signals for threaded operations
    work_started = Signal(dict)     # Work started successfully
    work_completed = Signal(dict)   # Work completed successfully
    error_occurred = Signal(str)    # Operation failed

    def __init__(self, api_client: APIClient, config):
        super().__init__()
        self.api_client = api_client
        self.config = config
        self._active_workers = []

    def start_work(self, lot_number: str, worker_id: str, serial_number: str = None):
        """
        Start work for LOT - POST /api/v1/process-operations/start (non-blocking)
        """
        try:
            logger.info(f"Starting work (threaded) for LOT: {lot_number}")

            # Use serial_number if provided, otherwise generate from lot_number
            if not serial_number:
                serial_number = f"{lot_number}-0001"

            data = {
                "lot_number": lot_number,
                "serial_number": serial_number,
                "process_id": str(self.config.process_db_id),  # Database PK as string
                "worker_id": worker_id,
                "equipment_id": self.config.equipment_code,
                "line_id": self.config.line_code,
                "start_time": datetime.now().isoformat()
            }

            logger.debug(f"Start work data: {data}")

            worker = APIWorker(
                api_client=self.api_client,
                operation="start_work",
                method="POST",
                endpoint="/api/v1/process-operations/start",
                data=data
            )
            worker.success.connect(self._on_api_success)
            worker.error.connect(self._on_api_error)
            worker.finished.connect(lambda: self._cleanup_worker(worker))

            self._active_workers.append(worker)
            worker.start()
        except Exception as e:
            error_msg = f"착공 요청 생성 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def complete_work(self, json_data: Dict):
        """
        Complete work from JSON file - POST /api/v1/process-operations/complete (non-blocking)
        """
        try:
            lot_number = json_data.get('lot_number', 'UNKNOWN')
            serial_number = json_data.get('serial_number', f"{lot_number}-0001")
            logger.info(f"Completing work (threaded) for LOT: {lot_number}, Serial: {serial_number}")

            # Build complete data with process_id from config
            data = {
                "lot_number": lot_number,
                "serial_number": serial_number,
                "process_id": self.config.process_db_id,  # Database PK as integer
                "result": json_data.get('result', 'PASS'),
                "measurement_data": json_data.get('measurement_data'),
                "defect_data": json_data.get('defect_data')
            }

            logger.debug(f"Complete work data: {data}")

            worker = APIWorker(
                api_client=self.api_client,
                operation="complete_work",
                method="POST",
                endpoint="/api/v1/process-operations/complete",
                data=data
            )
            worker.success.connect(self._on_api_success)
            worker.error.connect(self._on_api_error)
            worker.finished.connect(lambda: self._cleanup_worker(worker))

            self._active_workers.append(worker)
            worker.start()
        except Exception as e:
            error_msg = f"완공 요청 생성 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def _on_api_success(self, operation: str, result: dict):
        """Handle successful API call based on operation type."""
        logger.info(f"API success [{operation}]: {result}")

        if operation == "start_work":
            self.work_started.emit(result)
        elif operation == "complete_work":
            self.work_completed.emit(result)

    def _on_api_error(self, operation: str, error_msg: str):
        """Handle API error based on operation type."""
        logger.error(f"API error [{operation}]: {error_msg}")

        if operation == "start_work":
            self.error_occurred.emit(f"착공 등록 실패: {error_msg}")
        elif operation == "complete_work":
            self.error_occurred.emit(f"완공 처리 실패: {error_msg}")

    def _cleanup_worker(self, worker):
        """Clean up finished worker."""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()
        logger.debug(f"Worker cleaned up: {worker.operation}")

    @safe_cleanup("작업 취소 실패")
    def cancel_all_operations(self):
        """Cancel all active operations and clean up workers."""
        logger.info(f"Cancelling {len(self._active_workers)} active workers")
        for worker in self._active_workers[:]:
            try:
                if hasattr(worker, 'cancel'):
                    worker.cancel()
                if worker.isRunning():
                    worker.quit()
                    worker.wait(1000)
            except Exception as e:
                logger.warning(f"Worker 취소 실패: {e}")
        self._active_workers.clear()
        logger.info("All workers cancelled")