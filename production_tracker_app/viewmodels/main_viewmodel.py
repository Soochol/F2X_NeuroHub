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
        self.current_worker: Optional[str] = None
        self.is_online: bool = True

        # Connect signals
        self._connect_signals()

        # Connect print service signals if available (Process 7)
        if self.print_service:
            self.print_service.print_success.connect(self._on_print_success)
            self.print_service.print_error.connect(self._on_print_error)

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
        self.start_work(lot_number)

    def start_work(self, lot_number: str):
        """
        Start work for the given LOT number.

        Args:
            lot_number: LOT number to start work for
        """
        # Get current user
        worker_id = self.auth_service.get_current_user_id()

        logger.info(f"Processing barcode: {lot_number}, Worker: {worker_id}")

        # Store for when work starts successfully
        self.current_lot = lot_number
        self.current_worker = worker_id

        # Start work (threaded - result will come via signal)
        self.work_service.start_work(lot_number, worker_id)

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

    # --- Process 7 (Label Printing) methods ---

    def request_serial_and_print(self):
        """Request serial number from server and print label (Process 7 only)."""
        if not self.current_lot:
            self.error_occurred.emit("LOT 정보가 없습니다. 먼저 바코드를 스캔하세요.")
            return

        if not self.print_service:
            self.error_occurred.emit("프린트 서비스가 초기화되지 않았습니다.")
            return

        logger.info(f"Requesting serial for LOT: {self.current_lot}")

        try:
            # Request next serial from server
            response = self.api_client.get(f"/api/v1/lots/{self.current_lot}/next-serial")

            if response and "serial_number" in response:
                serial_number = response["serial_number"]
                logger.info(f"Serial received: {serial_number}")

                # Emit signal for UI update
                self.serial_received.emit(serial_number)

                # Print label
                if self.print_service.print_label(serial_number, self.current_lot):
                    # Success handled by _on_print_success signal
                    pass
                else:
                    # Error handled by _on_print_error signal
                    pass
            else:
                self.error_occurred.emit("시리얼 번호를 받지 못했습니다.")

        except Exception as e:
            error_msg = f"시리얼 요청 실패: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

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

        # Auto-complete work after successful print
        if self.current_lot:
            completion_data = {
                "lot_number": self.current_lot,
                "serial_number": serial_number,
                "process_id": self.config.process_id,
                "result": "PASS",
                "completed_at": datetime.now().isoformat()
            }
            self.work_service.complete_work(completion_data)

    def _on_print_error(self, error_msg: str):
        """Handle label print error."""
        logger.error(f"Label print error: {error_msg}")
        self.error_occurred.emit(error_msg)

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
