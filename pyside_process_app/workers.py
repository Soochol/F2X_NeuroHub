"""QThread Worker Classes for Background Operations

Refactored: Single APIWorker + 2 specialized workers for complex operations.
Before: 7 workers (520 lines) → After: 3 workers (200 lines)
"""

from PySide6.QtCore import QThread, Signal
from typing import Dict, Any, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class APIWorker(QThread):
    """Universal API worker for all background operations.

    Usage:
        # POST request
        worker = APIWorker(
            api_client=self.api_client,
            operation="start_process",
            method="POST",
            endpoint="/api/v1/process/start",
            data={"lot_number": "LOT001", ...}
        )
        worker.success.connect(self.on_success)
        worker.error.connect(self.on_error)
        worker.start()

        # GET request with params
        worker = APIWorker(
            api_client=self.api_client,
            operation="load_stats",
            method="GET",
            endpoint="/api/v1/analytics/daily",
            params={"process_id": 1}
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


class ProcessWorker(QThread):
    """Worker for process operations (start/complete) that involve multiple steps.

    Handles complex workflows like:
    - LOT lookup → Start process (착공)
    - Process completion (완공)
    """

    lot_loaded = Signal(dict)        # LOT data loaded
    process_started = Signal(str)    # LOT number
    process_completed = Signal(dict) # Completion data
    error = Signal(str)              # Error message
    progress = Signal(int, str)      # (percent, message)

    def __init__(
        self,
        process_service,
        operation: str,  # "start" or "complete"
        lot_number: str = "",
        process_id: int = 0,
        operator_id: int = 0,
        complete_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__()
        self.process_service = process_service
        self.operation = operation
        self.lot_number = lot_number
        self.process_id = process_id
        self.operator_id = operator_id
        self.complete_data = complete_data or {}
        self._is_cancelled = False

    def run(self):
        """Execute process operation in background."""
        if self._is_cancelled:
            return

        try:
            if self.operation == "start":
                self._run_start()
            elif self.operation == "complete":
                self._run_complete()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"ProcessWorker [{self.operation}] error: {e}")
                self.error.emit(str(e))

    def _run_start(self):
        """Start process workflow."""
        # Step 1: Get LOT info
        self.progress.emit(20, "LOT 정보 조회 중...")
        logger.info(f"Starting process for LOT: {self.lot_number}")

        lot = self.process_service.get_lot_by_number(self.lot_number)
        if not lot:
            raise ValueError(f"LOT를 찾을 수 없습니다: {self.lot_number}")

        if self._is_cancelled:
            return

        self.progress.emit(50, "LOT 정보 로드 완료")
        self.lot_loaded.emit(lot)

        # Step 2: Start process
        self.progress.emit(70, "공정 착공 중...")
        from datetime import datetime

        start_data = {
            "lot_id": lot.get("id"),
            "process_id": self.process_id,
            "operator_id": self.operator_id,
            "data_level": "LOT",
            "started_at": datetime.now().isoformat() + "Z"
        }

        result = self.process_service.start_process(start_data)

        if self._is_cancelled:
            return

        self.progress.emit(100, "착공 완료")
        logger.info(f"Process started successfully: {result}")
        self.process_started.emit(self.lot_number)

    def _run_complete(self):
        """Complete process workflow."""
        self.progress.emit(30, "공정 완공 처리 중...")
        logger.info(f"Completing process for LOT: {self.complete_data.get('lot_number')}")

        result = self.process_service.complete_process(self.complete_data)

        if self._is_cancelled:
            return

        self.progress.emit(100, "완공 완료")
        logger.info(f"Process completed successfully: {result}")
        self.process_completed.emit(self.complete_data)

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True


class RetryQueueWorker(QThread):
    """Worker for processing offline queue retry.

    This is kept as a specialized worker because it handles
    complex retry logic with multiple items.
    """

    item_processed = Signal(str, bool)  # filename, success
    progress = Signal(int, int)          # current, total
    completed = Signal(int, int)         # success_count, fail_count
    error = Signal(str)

    def __init__(self, offline_manager, api_client):
        super().__init__()
        self.offline_manager = offline_manager
        self.api_client = api_client
        self._is_cancelled = False

    def run(self):
        """Process offline queue in background."""
        try:
            if self._is_cancelled:
                return

            queued = self.offline_manager.get_queued_requests()

            if not queued:
                logger.info("Offline queue is empty")
                self.completed.emit(0, 0)
                return

            logger.info(f"Processing {len(queued)} queued requests...")
            total = len(queued)
            success_count = 0
            fail_count = 0

            for idx, item in enumerate(queued):
                if self._is_cancelled:
                    break

                self.progress.emit(idx + 1, total)

                try:
                    # Check retry limit
                    retry_count = item.get('retry_count', 0)
                    if retry_count >= 3:
                        logger.warning(f"Max retries reached for {item['_filename']}")
                        self.offline_manager.remove_from_queue(item['_filename'])
                        self.item_processed.emit(item['_filename'], False)
                        fail_count += 1
                        continue

                    # Send request
                    request_type = item['type']
                    endpoint = item['endpoint']
                    data = item['data']

                    if request_type == 'POST':
                        self.api_client.post(endpoint, data)
                    elif request_type == 'PUT':
                        self.api_client.put(endpoint, data)
                    elif request_type == 'DELETE':
                        self.api_client.delete(endpoint)
                    elif request_type == 'GET':
                        self.api_client.get(endpoint, params=data)

                    # Success
                    self.offline_manager.remove_from_queue(item['_filename'])
                    self.item_processed.emit(item['_filename'], True)
                    success_count += 1

                except Exception as e:
                    logger.error(f"Failed to process {item['_filename']}: {e}")
                    self.offline_manager.increment_retry_count(item['_filename'])
                    self.item_processed.emit(item['_filename'], False)
                    fail_count += 1

            if not self._is_cancelled:
                logger.info(f"Queue processing completed. Success: {success_count}, Failed: {fail_count}")
                self.completed.emit(success_count, fail_count)

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Critical error in retry queue worker: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation."""
        self._is_cancelled = True
