"""
Main ViewModel for Production Tracker App.
"""
from PySide6.QtCore import QObject, Signal
from datetime import datetime
from typing import Dict, Optional
import logging

from utils.exception_handler import (
    SignalConnector, CleanupManager, safe_slot, safe_cleanup
)
from utils.serial_validator import validate_serial_number_v1

logger = logging.getLogger(__name__)


class MainViewModel(QObject):
    """Business logic for main window."""

    # Signals
    lot_updated = Signal(dict)        # LOT information updated
    work_started = Signal(str)        # Work started (lot_number)
    work_completed = Signal(str)      # Work completed (message)
    error_occurred = Signal(str)      # Error message
    connection_status_changed = Signal(bool)  # Connection status (True=online)

    # Process 7 (Label Printing) signals
    serial_received = Signal(str)     # Serial number received from server

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
        self.current_wip_id: Optional[int] = None  # Store WIP ID
        self.current_worker: Optional[str] = None
        self.current_serial: Optional[str] = None  # For SERIAL-level work
        self.is_online: bool = True

        # Connect signals
        self._connect_signals()

        # Check if already logged in and emit connection status
        if self.auth_service.current_user:
            logger.info("User already authenticated, setting connection status to online")
            self.is_online = True
            # Emit connection status after a short delay to ensure UI is ready
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.connection_status_changed.emit(True))

        logger.info("MainViewModel initialized")

    def _connect_signals(self):
        """Connect internal signals."""
        connector = SignalConnector()

        # Barcode signals
        connector.connect(
            self.barcode_service.barcode_valid,
            self.on_barcode_scanned,
            "barcode_valid -> on_barcode_scanned"
        ).connect(
            self.barcode_service.serial_valid,
            self.on_serial_barcode_scanned,
            "serial_valid -> on_serial_barcode_scanned"
        ).connect(
            self.barcode_service.barcode_invalid,
            self.on_barcode_invalid,
            "barcode_invalid -> on_barcode_invalid"
        )

        # Completion watcher signals
        connector.connect(
            self.completion_watcher.completion_detected,
            self.on_completion_detected,
            "completion_detected -> on_completion_detected"
        ).connect(
            self.completion_watcher.file_processed,
            self.on_file_processed,
            "file_processed -> on_file_processed"
        ).connect(
            self.completion_watcher.error_occurred,
            self.on_completion_error,
            "watcher_error -> on_completion_error"
        )

        # Auth signals (threaded)
        connector.connect(
            self.auth_service.auth_error,
            self.error_occurred.emit,
            "auth_error -> error_occurred"
        ).connect(
            self.auth_service.login_success,
            self.on_login_success,
            "login_success -> on_login_success"
        )

        # Work service signals (threaded)
        connector.connect(
            self.work_service.work_started,
            self.on_work_started_success,
            "work_started -> on_work_started_success"
        ).connect(
            self.work_service.work_completed,
            self.on_work_completed_success,
            "work_completed -> on_work_completed_success"
        ).connect(
            self.work_service.serial_converted,
            self.on_serial_converted,
            "serial_converted -> on_serial_converted"
        ).connect(
            self.work_service.error_occurred,
            self.on_work_service_error,
            "work_error -> on_work_service_error"
        )

        if not connector.all_connected():
            logger.error(
                f"일부 시그널 연결 실패: {connector.failed_connections}"
            )

    def on_barcode_scanned(self, lot_number: str):
        """
        Handle valid LOT barcode scan (initiates threaded operation).

        Args:
            lot_number: LOT number from barcode
        """
        self.start_work(lot_number)

    def start_work(self, lot_number: str, serial_number: Optional[str] = None):
        """
        Start work for the given LOT number (and optionally Serial number).

        Args:
            lot_number: LOT number to start work for
            serial_number: Serial number (optional - for SERIAL-level work)
        """
        # Get current user
        worker_id = self.auth_service.get_current_user_id()

        if serial_number:
            logger.info(f"Processing LOT: {lot_number}, Serial: {serial_number}, Worker: {worker_id}")
        else:
            logger.info(f"Processing LOT: {lot_number}, Worker: {worker_id}")

        # Store for when work starts successfully
        self.current_lot = lot_number
        self.current_worker = worker_id
        self.current_serial = serial_number  # Store serial if provided

        # Start work (threaded - result will come via signal)
        self.work_service.start_work(lot_number, worker_id, serial_number)

    def complete_work(self, completion_data: dict):
        """
        Complete work with the given completion data.

        Args:
            completion_data: Completion data including result and process_data
        """
        lot_number = completion_data.get("lot_number", "UNKNOWN")
        logger.info(f"Completing work for LOT: {lot_number}")

        # Submit completion to backend (threaded - result will come via signal)
        self.work_service.complete_work(completion_data)

    def on_barcode_invalid(self, barcode: str):
        """
        Handle invalid barcode format.

        Args:
            barcode: Invalid barcode string
        """
        error_msg = f"잘못된 바코드 형식: {barcode}"
        logger.warning(error_msg)
        self.error_occurred.emit(error_msg)

    def on_serial_barcode_scanned(self, serial_number: str):
        """
        Handle valid SERIAL barcode scan.

        Args:
            serial_number: Serial number from barcode
        """
        logger.info(f"Serial barcode scanned: {serial_number}")
        # Emit signal for UI to update (MainWindow will handle this)
        self.serial_received.emit(serial_number)

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

    def clear_current_lot(self):
        """Clear current LOT information."""
        self.current_lot = None
        self.current_wip_id = None
        self.current_worker = None
        self.lot_updated.emit({})
        logger.info("Current LOT cleared")

    # --- Threaded operation callbacks ---

    def on_login_success(self, user_data: dict):
        """Handle successful login from threaded operation."""
        logger.info(f"Login successful (threaded callback): {user_data.get('username')}")

        # Update connection status
        self.is_online = True
        self.connection_status_changed.emit(True)

    def on_work_started_success(self, response: dict):
        """Handle successful work start from threaded operation."""
        logger.info(f"Work started successfully (threaded callback): {response}")

        # Store WIP ID if available
        self.current_wip_id = response.get("wip_id")

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

    def on_work_completed_success(self, response: dict):
        """Handle successful work completion from threaded operation."""
        lot_number = response.get("lot_number", self.current_lot or "UNKNOWN")
        logger.info(f"Work completed successfully (threaded callback): {lot_number}")

        # Emit signal
        self.work_completed.emit(f"완공: {lot_number}")

        # Clear current LOT if matches
        if self.current_lot == lot_number:
            self.clear_current_lot()

        # Update connection status
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

    def on_serial_converted(self, result: dict):
        """Handle successful serial conversion."""
        serial_dict = result.get("serial", {})
        serial_number = serial_dict.get("serial_number")

        if not serial_number:
            self.error_occurred.emit("시리얼 번호를 받지 못했습니다.")
            self.clear_current_lot() # Clear even on error to reset state
            return

        logger.info(f"Serial converted successfully: {serial_number}")

        # Emit signal for UI update
        self.serial_received.emit(serial_number)

        # Clear state after successful conversion
        self.clear_current_lot()

    @safe_cleanup("ViewModel 정리 실패")
    def cleanup(self):
        """Clean up resources and cancel pending operations."""
        logger.info("MainViewModel cleanup initiated")

        cleanup = CleanupManager()

        # Cancel service operations
        cleanup.add(
            self.work_service.cancel_all_operations,
            "작업 서비스 작업 취소"
        )
        cleanup.add(
            self.auth_service.cancel_all_operations,
            "인증 서비스 작업 취소"
        )
        cleanup.add(self.completion_watcher.stop, "완료 감시자 정지")

        failed = cleanup.execute()
        if failed:
            logger.warning(f"일부 정리 작업 실패: {failed}")

        logger.info("MainViewModel cleanup completed")
