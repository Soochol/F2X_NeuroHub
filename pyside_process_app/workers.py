"""QThread Worker Classes for Background Operations

This module provides QThread-based worker classes to prevent UI blocking
during long-running operations like API calls, database queries, and file I/O.
"""

from PySide6.QtCore import QThread, Signal
from typing import Dict, Any, Optional, Callable, List
from datetime import date
import logging

logger = logging.getLogger(__name__)


class APIWorker(QThread):
    """Generic API request worker for non-blocking network operations

    Signals:
        success (dict): Emitted when API request succeeds with response data
        error (str): Emitted when error occurs with error message
        finished: Emitted when thread completes (success or failure)
    """

    success = Signal(object)  # Response data (dict or list)
    error = Signal(str)       # Error message
    progress = Signal(int)    # Progress percentage (0-100)

    def __init__(self, api_call: Callable, *args, **kwargs):
        """Initialize API worker

        Args:
            api_call: The API method to call (e.g., api_client.get)
            *args: Positional arguments for api_call
            **kwargs: Keyword arguments for api_call
        """
        super().__init__()
        self.api_call = api_call
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    def run(self):
        """Execute API call in background thread"""
        try:
            if self._is_cancelled:
                return

            self.progress.emit(10)
            logger.debug(f"API Worker starting: {self.api_call.__name__}")

            self.progress.emit(50)
            result = self.api_call(*self.args, **self.kwargs)

            if self._is_cancelled:
                return

            self.progress.emit(100)
            logger.debug(f"API Worker completed: {self.api_call.__name__}")
            self.success.emit(result)

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"API Worker error in {self.api_call.__name__}: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class HistoryLoaderWorker(QThread):
    """Worker for loading process history data

    Signals:
        data_ready (list): Emitted when history data is loaded
        error (str): Emitted on error
        progress (int): Progress percentage (0-100)
    """

    data_ready = Signal(list)
    error = Signal(str)
    progress = Signal(int)

    def __init__(
        self,
        history_service,
        process_id: Optional[int] = None,
        operator_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        result_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ):
        """Initialize history loader worker

        Args:
            history_service: HistoryService instance
            process_id: Filter by process ID
            operator_id: Filter by operator ID
            start_date: Start date for filtering
            end_date: End date for filtering
            result_filter: Filter by result (PASS, FAIL, REWORK)
            skip: Pagination offset
            limit: Maximum records to return
        """
        super().__init__()
        self.history_service = history_service
        self.process_id = process_id
        self.operator_id = operator_id
        self.start_date = start_date
        self.end_date = end_date
        self.result_filter = result_filter
        self.skip = skip
        self.limit = limit
        self._is_cancelled = False

    def run(self):
        """Load history data in background"""
        try:
            if self._is_cancelled:
                return

            self.progress.emit(20)
            logger.info("Loading process history...")

            history = self.history_service.get_process_history(
                process_id=self.process_id,
                operator_id=self.operator_id,
                start_date=self.start_date,
                end_date=self.end_date,
                result_filter=self.result_filter,
                skip=self.skip,
                limit=self.limit
            )

            if self._is_cancelled:
                return

            self.progress.emit(100)
            logger.info(f"Loaded {len(history)} history records")
            self.data_ready.emit(history)

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Failed to load history: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class StatsLoaderWorker(QThread):
    """Worker for loading daily statistics

    Signals:
        stats_ready (dict): Emitted when stats are loaded
        error (str): Emitted on error
        progress (int): Progress percentage (0-100)
    """

    stats_ready = Signal(dict)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, process_service, process_id: int):
        """Initialize stats loader worker

        Args:
            process_service: ProcessService instance
            process_id: Process ID to get stats for
        """
        super().__init__()
        self.process_service = process_service
        self.process_id = process_id
        self._is_cancelled = False

    def run(self):
        """Load stats data in background"""
        try:
            if self._is_cancelled:
                return

            self.progress.emit(30)
            logger.info(f"Loading daily stats for process {self.process_id}...")

            stats = self.process_service.get_daily_stats(
                process_id=self.process_id
            )

            if self._is_cancelled:
                return

            self.progress.emit(100)
            logger.info("Daily stats loaded successfully")
            self.stats_ready.emit(stats)

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Failed to load stats: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class ProcessStartWorker(QThread):
    """Worker for starting a process (착공)

    Signals:
        lot_loaded (dict): Emitted when LOT data is loaded
        process_started (str): Emitted when process starts with LOT number
        error (str): Emitted on error
        progress (int, str): Progress percentage and message
    """

    lot_loaded = Signal(dict)
    process_started = Signal(str)
    error = Signal(str)
    progress = Signal(int, str)

    def __init__(
        self,
        process_service,
        lot_number: str,
        process_id: int,
        operator_id: int
    ):
        """Initialize process start worker

        Args:
            process_service: ProcessService instance
            lot_number: LOT number to start
            process_id: Process ID
            operator_id: Operator ID
        """
        super().__init__()
        self.process_service = process_service
        self.lot_number = lot_number
        self.process_id = process_id
        self.operator_id = operator_id
        self._is_cancelled = False

    def run(self):
        """Start process in background"""
        try:
            if self._is_cancelled:
                return

            self.progress.emit(20, "LOT 정보 조회 중...")
            logger.info(f"Starting process for LOT: {self.lot_number}")

            # Get LOT info
            lot = self.process_service.get_lot_by_number(self.lot_number)
            if not lot:
                raise ValueError(f"LOT를 찾을 수 없습니다: {self.lot_number}")

            if self._is_cancelled:
                return

            self.progress.emit(50, "LOT 정보 로드 완료")
            self.lot_loaded.emit(lot)

            # Start process
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

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Failed to start process: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class ProcessCompleteWorker(QThread):
    """Worker for completing a process (완공)

    Signals:
        completed (dict): Emitted when process completes with result data
        error (str): Emitted on error
        progress (int, str): Progress percentage and message
    """

    completed = Signal(dict)
    error = Signal(str)
    progress = Signal(int, str)

    def __init__(
        self,
        process_service,
        complete_data: Dict[str, Any]
    ):
        """Initialize process complete worker

        Args:
            process_service: ProcessService instance
            complete_data: Process completion data
        """
        super().__init__()
        self.process_service = process_service
        self.complete_data = complete_data
        self._is_cancelled = False

    def run(self):
        """Complete process in background"""
        try:
            if self._is_cancelled:
                return

            self.progress.emit(30, "공정 완공 처리 중...")
            logger.info(f"Completing process for LOT: {self.complete_data.get('lot_number')}")

            result = self.process_service.complete_process(self.complete_data)

            if self._is_cancelled:
                return

            self.progress.emit(100, "완공 완료")
            logger.info(f"Process completed successfully: {result}")
            self.completed.emit(self.complete_data)

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Failed to complete process: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class RetryQueueWorker(QThread):
    """Worker for processing offline queue retry

    Signals:
        item_processed (str, bool): Emitted for each item (filename, success)
        progress (int, int): Progress (current, total)
        completed (int, int): Emitted when done (success_count, fail_count)
        error (str): Emitted on critical error
    """

    item_processed = Signal(str, bool)  # filename, success
    progress = Signal(int, int)          # current, total
    completed = Signal(int, int)         # success_count, fail_count
    error = Signal(str)

    def __init__(self, offline_manager, api_client):
        """Initialize retry queue worker

        Args:
            offline_manager: OfflineManager instance
            api_client: APIClient instance
        """
        super().__init__()
        self.offline_manager = offline_manager
        self.api_client = api_client
        self._is_cancelled = False

    def run(self):
        """Process offline queue in background"""
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
                        logger.warning(
                            f"Max retries reached for {item['_filename']}, "
                            f"removing from queue"
                        )
                        self.offline_manager.remove_from_queue(item['_filename'])
                        self.item_processed.emit(item['_filename'], False)
                        fail_count += 1
                        continue

                    # Attempt to send request
                    request_type = item['type']
                    endpoint = item['endpoint']
                    data = item['data']

                    logger.info(
                        f"Retrying {request_type} {endpoint} "
                        f"(attempt {retry_count + 1}/3)"
                    )

                    if request_type == 'POST':
                        self.api_client.post(endpoint, data)
                    elif request_type == 'PUT':
                        self.api_client.put(endpoint, data)
                    elif request_type == 'DELETE':
                        self.api_client.delete(endpoint)
                    elif request_type == 'GET':
                        self.api_client.get(endpoint, params=data)
                    else:
                        logger.error(f"Unknown request type: {request_type}")
                        continue

                    # Success - remove from queue
                    self.offline_manager.remove_from_queue(item['_filename'])
                    self.item_processed.emit(item['_filename'], True)
                    success_count += 1
                    logger.info(f"Successfully processed: {item['_filename']}")

                except Exception as e:
                    logger.error(f"Failed to process {item['_filename']}: {e}")
                    # Increment retry count
                    self.offline_manager.increment_retry_count(item['_filename'])
                    self.item_processed.emit(item['_filename'], False)
                    fail_count += 1

            if not self._is_cancelled:
                logger.info(
                    f"Queue processing completed. "
                    f"Success: {success_count}, Failed: {fail_count}"
                )
                self.completed.emit(success_count, fail_count)

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Critical error in retry queue worker: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class LotRefreshWorker(QThread):
    """Worker for refreshing LOT information

    Signals:
        lot_refreshed (dict): Emitted when LOT is refreshed
        error (str): Emitted on error
    """

    lot_refreshed = Signal(dict)
    error = Signal(str)

    def __init__(self, process_service, lot_id: int):
        """Initialize LOT refresh worker

        Args:
            process_service: ProcessService instance
            lot_id: LOT ID to refresh
        """
        super().__init__()
        self.process_service = process_service
        self.lot_id = lot_id
        self._is_cancelled = False

    def run(self):
        """Refresh LOT in background"""
        try:
            if self._is_cancelled:
                return

            logger.info(f"Refreshing LOT {self.lot_id}...")

            lot = self.process_service.get_lot_by_id(self.lot_id)

            if self._is_cancelled:
                return

            if lot:
                logger.info(f"LOT {self.lot_id} refreshed successfully")
                self.lot_refreshed.emit(lot)
            else:
                raise ValueError(f"LOT {self.lot_id}를 찾을 수 없습니다")

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"Failed to refresh LOT: {e}")
                self.error.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True
