"""Main ViewModel - Business logic for main window"""

from PySide6.QtCore import QObject, Signal
from typing import Optional
from requests.exceptions import ConnectionError, Timeout, HTTPError
import logging

logger = logging.getLogger(__name__)


class MainViewModel(QObject):
    """메인 화면 비즈니스 로직"""

    # UI 업데이트 시그널
    current_lot_updated = Signal(object)  # Lot data dict
    daily_stats_updated = Signal(dict)    # Stats dict
    stats_updated = Signal(dict)          # Stats dict (alias for daily_stats_updated)
    process_started = Signal(str)         # LOT number
    process_completed = Signal(dict)      # Completion data
    error_occurred = Signal(str)          # Error message
    status_message = Signal(str)          # Status bar message
    loading_changed = Signal(bool)        # Loading state
    connection_status_changed = Signal(bool)  # Connection status
    offline_queue_changed = Signal(int)   # Offline queue size

    def __init__(self, process_service, file_watcher_service, config, app_state, offline_manager=None, retry_manager=None):
        super().__init__()
        self.process_service = process_service
        self.file_watcher_service = file_watcher_service
        self.config = config
        self.app_state = app_state
        self.current_lot = None
        self.offline_manager = offline_manager
        self.retry_manager = retry_manager

        # Worker threads tracking
        self._active_workers = []

        # Connect file watcher
        self.file_watcher_service.json_file_detected.connect(self._on_json_detected)
        self.file_watcher_service.error_occurred.connect(self.error_occurred.emit)

        # Connect offline manager signals if available
        if self.offline_manager:
            self.offline_manager.connection_status_changed.connect(self._on_connection_status_changed)
            self.offline_manager.offline_queue_changed.connect(self._on_offline_queue_changed)

        # Connect retry manager signals if available
        if self.retry_manager:
            self.retry_manager.retry_success.connect(self._on_retry_success)
            self.retry_manager.retry_failed.connect(self._on_retry_failed)

    def start_process(self, lot_number: str):
        """착공 처리 (바코드 스캔) - Non-blocking with QThread"""
        from workers import ProcessStartWorker

        self.loading_changed.emit(True)
        self.status_message.emit(f"LOT {lot_number} 착공 처리 중...")
        logger.info(f"Starting process for LOT: {lot_number}")

        # Create worker thread
        operator_id = self.app_state.current_user.get("id") if self.app_state.current_user else 1
        worker = ProcessStartWorker(
            self.process_service,
            lot_number,
            self.config.process_number,
            operator_id
        )

        # Connect worker signals
        worker.lot_loaded.connect(self._on_worker_lot_loaded)
        worker.process_started.connect(self._on_worker_process_started)
        worker.error.connect(self._on_worker_error)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.finished.connect(lambda: self.loading_changed.emit(False))

        # Track and start worker
        self._active_workers.append(worker)
        worker.start()

    def _on_worker_lot_loaded(self, lot: dict):
        """Handle LOT loaded from worker"""
        self.current_lot = lot
        self.app_state.current_lot = lot
        self.current_lot_updated.emit(lot)

    def _on_worker_process_started(self, lot_number: str):
        """Handle process started from worker"""
        self.process_started.emit(lot_number)
        self.status_message.emit(f"LOT {lot_number} 착공 완료")

    def _on_worker_progress(self, progress: int, message: str):
        """Handle worker progress updates"""
        self.status_message.emit(message)

    def _on_worker_error(self, error_message: str):
        """Handle worker error"""
        # Check error type and provide appropriate message
        if "연결할 수 없습니다" in error_message or "Connection" in error_message:
            self.error_occurred.emit("🔴 백엔드 서버에 연결할 수 없습니다.\n오프라인 모드로 전환되었습니다.")
        elif "시간이 초과" in error_message or "Timeout" in error_message:
            self.error_occurred.emit("⏱️ 서버 응답 시간이 초과되었습니다.\n잠시 후 다시 시도해주세요.")
        elif "찾을 수 없습니다" in error_message:
            self.error_occurred.emit(f"⚠️ {error_message}")
        else:
            self.error_occurred.emit(f"작업 실패: {error_message}")

    def _cleanup_worker(self, worker):
        """Clean up finished worker"""
        if worker in self._active_workers:
            self._active_workers.remove(worker)
        worker.deleteLater()

    def _on_json_detected(self, json_data: dict):
        """JSON 파일 감지 → 완공 처리 - Non-blocking with QThread"""
        from workers import ProcessCompleteWorker

        logger.info(f"JSON file detected: {json_data.get('lot_number')}")
        self.status_message.emit(f"LOT {json_data.get('lot_number')} 완공 처리 중...")

        # Prepare complete data
        complete_data = {
            "lot_number": json_data["lot_number"],
            "process_id": self.config.process_number,
            "operator_id": self.app_state.current_user.get("id") if self.app_state.current_user else 1,
            "result": json_data.get("result", "PASS"),
            "measurements": json_data.get("process_data", {}),
            "completed_at": self._get_current_timestamp()
        }

        # Create worker thread
        worker = ProcessCompleteWorker(self.process_service, complete_data)

        # Connect worker signals
        worker.completed.connect(lambda data: self._on_process_completed(data, json_data))
        worker.error.connect(self._on_complete_error)
        worker.progress.connect(self._on_worker_progress)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        # Track and start worker
        self._active_workers.append(worker)
        worker.start()

    def _on_process_completed(self, complete_data: dict, json_data: dict):
        """Handle process completion from worker"""
        self.process_completed.emit(json_data)
        self.status_message.emit(f"LOT {json_data.get('lot_number')} 완공 완료")
        logger.info(f"Process completed successfully")

        # Refresh current lot in background
        if self.current_lot:
            self.refresh_current_lot()

    def _on_complete_error(self, error_message: str):
        """Handle completion error"""
        if "연결할 수 없습니다" in error_message or "Connection" in error_message:
            self.error_occurred.emit("🔴 백엔드 서버에 연결할 수 없습니다.\n데이터가 로컬에 저장되었습니다.")
        elif "시간이 초과" in error_message or "Timeout" in error_message:
            self.error_occurred.emit("⏱️ 서버 응답 시간이 초과되었습니다.")
        else:
            self.error_occurred.emit(f"완공 실패: {error_message}")

    def refresh_current_lot(self):
        """현재 LOT 정보 갱신 - Non-blocking with QThread"""
        from workers import LotRefreshWorker

        if not self.current_lot:
            return

        lot_id = self.current_lot.get("id")
        logger.info(f"Refreshing LOT {lot_id}...")

        # Create worker thread
        worker = LotRefreshWorker(self.process_service, lot_id)

        # Connect worker signals
        worker.lot_refreshed.connect(self._on_lot_refreshed)
        worker.error.connect(lambda err: logger.error(f"Failed to refresh lot: {err}"))
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        # Track and start worker
        self._active_workers.append(worker)
        worker.start()

    def _on_lot_refreshed(self, lot: dict):
        """Handle LOT refresh from worker"""
        self.current_lot = lot
        self.app_state.current_lot = lot
        self.current_lot_updated.emit(lot)
        logger.info(f"LOT refreshed successfully")

    def load_daily_stats(self):
        """금일 작업 현황 로드 - Non-blocking with QThread"""
        from workers import StatsLoaderWorker

        logger.info("Loading daily stats...")
        self.status_message.emit("통계 로드 중...")

        # Create worker thread
        worker = StatsLoaderWorker(self.process_service, self.config.process_number)

        # Connect worker signals
        worker.stats_ready.connect(self._on_stats_loaded)
        worker.error.connect(self._on_stats_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))

        # Track and start worker
        self._active_workers.append(worker)
        worker.start()

    def _on_stats_loaded(self, stats: dict):
        """Handle stats loaded from worker"""
        self.daily_stats_updated.emit(stats)
        self.stats_updated.emit(stats)
        self.status_message.emit("통계 로드 완료")
        logger.info("Daily stats loaded successfully")

    def _on_stats_error(self, error_message: str):
        """Handle stats loading error"""
        logger.error(f"Failed to load daily stats: {error_message}")
        self.error_occurred.emit(f"통계 로드 실패: {error_message}")

    def _get_current_timestamp(self) -> str:
        """현재 시간을 ISO 8601 형식으로 반환"""
        from datetime import datetime
        return datetime.now().isoformat() + "Z"

    def _on_connection_status_changed(self, is_online: bool):
        """연결 상태 변경 시그널 전달"""
        self.connection_status_changed.emit(is_online)
        if is_online:
            logger.info("Connection restored - Online mode")
        else:
            logger.warning("Connection lost - Offline mode")

    def _on_offline_queue_changed(self, queue_size: int):
        """오프라인 큐 크기 변경 시그널 전달"""
        self.offline_queue_changed.emit(queue_size)
        logger.info(f"Offline queue size: {queue_size}")

    def _on_retry_success(self, filename: str):
        """재시도 성공"""
        logger.info(f"Retry successful: {filename}")

    def _on_retry_failed(self, filename: str, error: str):
        """재시도 실패"""
        logger.error(f"Retry failed for {filename}: {error}")

    def manual_retry_offline_queue(self):
        """수동으로 오프라인 큐 재시도"""
        if self.retry_manager:
            logger.info("Manual retry triggered by user")
            self.retry_manager.manual_retry()
        else:
            logger.warning("RetryManager not available")

    def get_offline_queue_size(self) -> int:
        """현재 오프라인 큐 크기 반환"""
        if self.offline_manager:
            return self.offline_manager.get_queue_size()
        return 0

    def is_online(self) -> bool:
        """현재 온라인 상태 반환"""
        if self.offline_manager:
            return self.offline_manager.is_online
        return True

    def cleanup_workers(self):
        """Clean up all active worker threads"""
        logger.info(f"Cleaning up {len(self._active_workers)} active workers...")
        for worker in self._active_workers[:]:  # Create copy to iterate
            if worker.isRunning():
                worker.cancel()
                worker.quit()
                worker.wait(1000)  # Wait up to 1 second
            worker.deleteLater()
        self._active_workers.clear()
        logger.info("Worker cleanup completed")