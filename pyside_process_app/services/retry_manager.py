"""Retry Manager - Handles offline queue retry logic"""

from PySide6.QtCore import QObject, Signal, QTimer
import logging

logger = logging.getLogger(__name__)


class RetryManager(QObject):
    """오프라인 큐 재시도 관리자"""

    retry_success = Signal(str)  # filename
    retry_failed = Signal(str, str)  # filename, error
    retry_progress = Signal(int, int)  # current, total

    def __init__(self, offline_manager, api_client):
        super().__init__()
        self.offline_manager = offline_manager
        self.api_client = api_client
        self.is_processing = False
        self._retry_worker = None  # Track worker thread

        # Auto-retry timer when connection restored
        self.retry_timer = QTimer()
        self.retry_timer.timeout.connect(self.process_queue)

        # Connect to connection status changes
        self.offline_manager.connection_status_changed.connect(self._on_connection_changed)

    def _on_connection_changed(self, is_online: bool):
        """연결 복구 시 자동 재시도"""
        if is_online:
            logger.info("Connection restored, scheduling offline queue processing...")
            # Wait 2 seconds before processing to ensure connection is stable
            QTimer.singleShot(2000, self.process_queue)

    def process_queue(self):
        """큐에 저장된 요청 처리 - Non-blocking with QThread"""
        from workers import RetryQueueWorker

        # Check if already processing
        if self.is_processing:
            logger.info("Queue processing already in progress, skipping...")
            return

        if not self.offline_manager.is_online:
            logger.info("Still offline, cannot process queue")
            return

        queued = self.offline_manager.get_queued_requests()

        if not queued:
            logger.info("Offline queue is empty")
            return

        # Cancel existing worker if running
        if self._retry_worker and self._retry_worker.isRunning():
            self._retry_worker.cancel()
            self._retry_worker.quit()
            self._retry_worker.wait()

        self.is_processing = True
        logger.info(f"Processing {len(queued)} queued requests...")

        # Create worker thread
        self._retry_worker = RetryQueueWorker(
            self.offline_manager,
            self.api_client
        )

        # Connect worker signals
        self._retry_worker.item_processed.connect(self._on_item_processed)
        self._retry_worker.progress.connect(self.retry_progress.emit)
        self._retry_worker.completed.connect(self._on_queue_completed)
        self._retry_worker.error.connect(self._on_queue_error)
        self._retry_worker.finished.connect(self._on_worker_finished)

        # Start worker
        self._retry_worker.start()

    def _on_item_processed(self, filename: str, success: bool):
        """Handle individual item processing result"""
        if success:
            self.retry_success.emit(filename)
            logger.info(f"Successfully processed: {filename}")
        else:
            self.retry_failed.emit(filename, "Processing failed")
            logger.warning(f"Failed to process: {filename}")

    def _on_queue_completed(self, success_count: int, fail_count: int):
        """Handle queue processing completion"""
        logger.info(
            f"Queue processing completed. "
            f"Success: {success_count}, Failed: {fail_count}"
        )

    def _on_queue_error(self, error_message: str):
        """Handle critical queue processing error"""
        logger.error(f"Queue processing error: {error_message}")

    def _on_worker_finished(self):
        """Handle worker thread completion"""
        self.is_processing = False
        if self._retry_worker:
            self._retry_worker.deleteLater()
            self._retry_worker = None

    def manual_retry(self):
        """수동 재시도 트리거"""
        logger.info("Manual retry triggered")
        self.process_queue()

    def clear_failed_requests(self):
        """실패한 요청들 정리 (재시도 횟수 3회 이상)"""
        queued = self.offline_manager.get_queued_requests()
        removed_count = 0

        for item in queued:
            if item.get('retry_count', 0) >= 3:
                self.offline_manager.remove_from_queue(item['_filename'])
                removed_count += 1
                logger.info(f"Removed failed request: {item['_filename']}")

        logger.info(f"Cleared {removed_count} failed requests")
        return removed_count

    def cleanup(self):
        """Clean up worker thread"""
        if self._retry_worker and self._retry_worker.isRunning():
            logger.info("Cleaning up retry worker...")
            self._retry_worker.cancel()
            self._retry_worker.quit()
            self._retry_worker.wait(1000)  # Wait up to 1 second
            self._retry_worker.deleteLater()
            self._retry_worker = None
        self.is_processing = False
