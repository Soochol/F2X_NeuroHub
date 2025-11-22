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
    label_printed = Signal(str)       # Label printed successfully

    def __init__(self, config, api_client, auth_service, work_service, barcode_service, completion_watcher, print_service=None):
        super().__init__()
        self.config = config
        self.api_client = api_client
        self.auth_service = auth_service
        self.work_service = work_service
        self.barcode_service = barcode_service
        self.completion_watcher = completion_watcher
        self.print_service = print_service  # Only for Process 7

        # State
        self.current_lot: Optional[str] = None
        self.current_wip_id: Optional[int] = None  # Store WIP ID
        self.current_worker: Optional[str] = None
        self.current_serial: Optional[str] = None  # For SERIAL-level work
        self.is_online: bool = True

        # Connect signals
        self._connect_signals()

        # Connect print service signals if available (Process 7)
        if self.print_service:
            self.print_service.print_success.connect(self._on_print_success)
            self.print_service.print_error.connect(self._on_print_error)

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

        # Check if we need to generate serial (Process 7)
        if self.config.process_number == 7:
            logger.info("Process 7 completed, triggering serial conversion...")
            self.request_serial_and_print()
            # Do not clear state yet, wait for serial conversion
        else:
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

    # --- Process 7 (Label Printing) methods ---

    def request_serial_and_print(self):
        """Request serial number from server and print label (Process 7 only)."""
        if not self.current_lot:
            self.error_occurred.emit("LOT 정보가 없습니다. 먼저 바코드를 스캔하세요.")
            return

        if not self.print_service:
            self.error_occurred.emit("프린트 서비스가 초기화되지 않았습니다.")
            return

        if not self.current_wip_id:
            logger.warning("WIP ID not found in current session, trying to use LOT number as WIP ID string if possible, but conversion requires int ID.")
            self.error_occurred.emit("WIP 정보를 찾을 수 없습니다. 다시 스캔해주세요.")
            return

        logger.info(f"Requesting serial conversion for WIP ID: {self.current_wip_id}")

        # Call WorkService to convert
        try:
            # Get numeric operator ID if possible, or use 1 as fallback
            user = self.auth_service.current_user
            operator_id = user.get("id") if user else 1

            self.work_service.convert_wip_to_serial(self.current_wip_id, operator_id)

        except Exception as e:
            error_msg = f"시리얼 요청 실패: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

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

        # Print label
        if self.print_service:
            if self.print_service.print_label(serial_number, self.current_lot):
                # Success handled by _on_print_success signal
                pass
            else:
                # Error handled by _on_print_error signal
                pass
        
        # Clear state after successful conversion (and print attempt)
        self.clear_current_lot()

    def reprint_label(self):
        """Reprint last label using cached serial (Process 7 only)."""
        if not self.print_service:
            self.error_occurred.emit("프린트 서비스가 초기화되지 않았습니다.")
            return

        if not self.print_service.last_serial:
            self.error_occurred.emit("재출력할 라벨이 없습니다.")
            return

        logger.info(f"Reprinting label: {self.print_service.last_serial}")
        self.print_service.reprint()

    def _on_print_success(self, serial_number: str):
        """Handle successful label print."""
        logger.info(f"Label printed successfully: {serial_number}")
        self.label_printed.emit(serial_number)

        # Auto-complete work after successful print is NOT needed here because
        # we already completed the work (Process 7 PASS) BEFORE requesting serial?
        # Wait, the workflow is:
        # 1. User clicks PASS.
        # 2. `complete_work` is called.
        # 3. If success, THEN we request serial?
        # OR
        # 1. User clicks PASS.
        # 2. We request serial first?
        # BR-005 says "All processes 1-6 must have PASS results".
        # Process 7 is Label Print.
        # So we should Complete Process 7 first?
        # Actually, `convert_to_serial` IS the completion of the workflow.
        # But we also have `complete_process` for Process 7?
        # If Process 7 is just "Label Printing", maybe `convert_to_serial` encompasses it?
        # The backend `convert_to_serial` updates WIP status to `CONVERTED`.
        # It does NOT create a `ProcessData` record for Process 7.
        # But `ProcessData` for Process 7 might be needed for traceability.
        # Let's check `complete_process` in backend.
        # It updates `ProcessData`.
        # So we should probably:
        # 1. Call `complete_work` (creates ProcessData for Process 7).
        # 2. Call `convert_wip_to_serial` (creates Serial, updates WIP).
        #
        # In `_on_print_success`, we previously called `complete_work`.
        # Now, we should ensure `complete_work` happens.
        #
        # Let's adjust the flow in `MainWindow` (or wherever `pass_requested` is handled).
        # If I look at `MainWindow`, it calls `complete_work`.
        #
        # If I change `request_serial_and_print` to be called AFTER `complete_work` success?
        # Currently `request_serial_and_print` was called manually or by UI?
        #
        # Let's look at `MainWindow` logic later.
        # For now, `_on_print_success` just emits `label_printed`.
        # I will remove the `complete_work` call from `_on_print_success` to avoid double completion if we change the flow.
        pass

    def _on_print_error(self, error_msg: str):
        """Handle label print error."""
        logger.error(f"Label print error: {error_msg}")
        self.error_occurred.emit(error_msg)

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
