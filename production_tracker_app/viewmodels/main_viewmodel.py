"""
Main ViewModel for Production Tracker App.
"""
from PySide6.QtCore import QObject, Signal, QTimer
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MainViewModel(QObject):
    """Business logic for main window."""

    # Signals
    lot_updated = Signal(dict)        # LOT information updated
    stats_updated = Signal(dict)      # Statistics updated
    work_started = Signal(str)        # Work started (lot_number)
    work_completed = Signal(str)      # Work completed (message)
    error_occurred = Signal(str)      # Error message
    connection_status_changed = Signal(bool)  # Connection status (True=online)

    def __init__(self, config, api_client, auth_service, work_service, barcode_service, completion_watcher):
        super().__init__()
        self.config = config
        self.api_client = api_client
        self.auth_service = auth_service
        self.work_service = work_service
        self.barcode_service = barcode_service
        self.completion_watcher = completion_watcher

        # State
        self.current_lot: Optional[str] = None
        self.current_worker: Optional[str] = None
        self.is_online: bool = True

        # Connect signals
        self._connect_signals()

        # Stats refresh timer (every 5 seconds)
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.refresh_stats)
        self.stats_timer.start(5000)

        logger.info("MainViewModel initialized")

    def _connect_signals(self):
        """Connect internal signals."""
        # Barcode signals
        self.barcode_service.barcode_valid.connect(self.on_barcode_scanned)
        self.barcode_service.barcode_invalid.connect(self.on_barcode_invalid)

        # Completion watcher signals
        self.completion_watcher.completion_detected.connect(self.on_completion_detected)
        self.completion_watcher.file_processed.connect(self.on_file_processed)
        self.completion_watcher.error_occurred.connect(self.on_completion_error)

        # Auth signals (threaded)
        self.auth_service.auth_error.connect(self.error_occurred.emit)
        self.auth_service.login_success.connect(self.on_login_success)

        # Work service signals (threaded)
        self.work_service.work_started.connect(self.on_work_started_success)
        self.work_service.work_completed.connect(self.on_work_completed_success)
        self.work_service.stats_ready.connect(self.on_stats_ready)
        self.work_service.error_occurred.connect(self.on_work_service_error)

    def on_barcode_scanned(self, lot_number: str):
        """
        Handle valid LOT barcode scan (initiates threaded operation).

        Args:
            lot_number: LOT number from barcode
        """
        # Get current user
        worker_id = self.auth_service.get_current_user_id()

        logger.info(f"Processing barcode: {lot_number}, Worker: {worker_id}")

        # Store for when work starts successfully
        self.current_lot = lot_number
        self.current_worker = worker_id

        # Start work (threaded - result will come via signal)
        self.work_service.start_work(lot_number, worker_id)

    def on_barcode_invalid(self, barcode: str):
        """
        Handle invalid barcode format.

        Args:
            barcode: Invalid barcode string
        """
        error_msg = f"잘못된 바코드 형식: {barcode}"
        logger.warning(error_msg)
        self.error_occurred.emit(error_msg)

    def on_completion_detected(self, json_data: dict):
        """
        Handle JSON completion file detected (initiates threaded operation).

        Args:
            json_data: Completion data from JSON file
        """
        lot_number = json_data.get("lot_number", "UNKNOWN")
        logger.info(f"Processing completion for LOT: {lot_number}")

        # Submit completion to backend (threaded - result will come via signal)
        self.work_service.complete_work(json_data)

    def on_file_processed(self, filename: str):
        """
        Handle file processed successfully.

        Args:
            filename: Processed filename
        """
        logger.info(f"File processed: {filename}")

    def on_completion_error(self, error_msg: str):
        """
        Handle completion processing error.

        Args:
            error_msg: Error message
        """
        logger.error(f"Completion error: {error_msg}")
        self.error_occurred.emit(error_msg)

    def refresh_stats(self):
        """Refresh daily statistics (threaded - result will come via signal)."""
        logger.debug("Initiating stats refresh (threaded)")
        self.work_service.get_today_stats()

    def clear_current_lot(self):
        """Clear current LOT information."""
        self.current_lot = None
        self.current_worker = None
        self.lot_updated.emit({})
        logger.info("Current LOT cleared")

    # --- Threaded operation callbacks ---

    def on_login_success(self, user_data: dict):
        """Handle successful login from threaded operation."""
        logger.info(f"Login successful (threaded callback): {user_data.get('username')}")

    def on_work_started_success(self, response: dict):
        """Handle successful work start from threaded operation."""
        logger.info(f"Work started successfully (threaded callback): {response}")

        # Emit signals
        self.work_started.emit(self.current_lot)
        self.lot_updated.emit({
            "lot_number": self.current_lot,
            "worker_id": self.current_worker,
            "start_time": datetime.now().strftime("%H:%M:%S")
        })

        # Update connection status
        self.is_online = True
        self.connection_status_changed.emit(True)

        # Refresh stats
        self.refresh_stats()

    def on_work_completed_success(self, response: dict):
        """Handle successful work completion from threaded operation."""
        lot_number = response.get("lot_number", self.current_lot or "UNKNOWN")
        logger.info(f"Work completed successfully (threaded callback): {lot_number}")

        # Emit signal
        self.work_completed.emit(f"완공: {lot_number}")

        # Clear current LOT if matches
        if self.current_lot == lot_number:
            self.current_lot = None
            self.current_worker = None
            self.lot_updated.emit({})

        # Update connection status
        self.is_online = True
        self.connection_status_changed.emit(True)

        # Refresh stats
        self.refresh_stats()

    def on_stats_ready(self, stats: dict):
        """Handle statistics ready from threaded operation."""
        logger.debug(f"Stats ready (threaded callback): {stats}")
        self.stats_updated.emit(stats)

        # Update connection status if successful
        if not self.is_online:
            self.is_online = True
            self.connection_status_changed.emit(True)

    def on_work_service_error(self, error_msg: str):
        """Handle work service error from threaded operation."""
        logger.error(f"Work service error (threaded callback): {error_msg}")
        self.error_occurred.emit(error_msg)

        # Check if connection error
        if "연결" in error_msg or "Connection" in error_msg or "백엔드 서버에 연결" in error_msg:
            self.is_online = False
            self.connection_status_changed.emit(False)

    def cleanup(self):
        """Clean up resources and cancel pending operations."""
        logger.info("MainViewModel cleanup initiated")

        # Stop timers
        if self.stats_timer.isActive():
            self.stats_timer.stop()

        # Cancel work service operations
        self.work_service.cancel_all_operations()

        # Cancel auth service operations
        self.auth_service.cancel_all_operations()

        # Stop completion watcher
        self.completion_watcher.stop()

        logger.info("MainViewModel cleanup completed")
