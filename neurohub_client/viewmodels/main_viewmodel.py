"""
Main ViewModel for Production Tracker App.
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

from utils.exception_handler import (
    SignalConnector, CleanupManager, safe_slot, safe_cleanup
)

logger = logging.getLogger(__name__)


# TCP Server default port
DEFAULT_TCP_PORT = 9000


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

    # TCP Server / Equipment measurement signals
    measurement_received = Signal(object)  # EquipmentData from TCP
    tcp_server_status = Signal(bool, str)  # (is_running, status_message)

    def __init__(
        self,
        config: Any,
        api_client: Any,
        auth_service: Any,
        work_service: Any,
        barcode_service: Any,
        completion_watcher: Any,
        tcp_server: Optional[Any] = None
    ) -> None:
        super().__init__()
        self.config = config
        self.api_client = api_client
        self.auth_service = auth_service
        self.work_service = work_service
        self.barcode_service = barcode_service
        self.completion_watcher = completion_watcher
        self.tcp_server = tcp_server

        # State
        self.current_wip_id: Optional[str] = None  # Store WIP ID (e.g., WIP-KR01PSA2511-001)
        self.current_worker: Optional[str] = None
        self.is_online: bool = True

        # Equipment measurement data (from TCP)
        self.pending_measurement: Optional[Any] = None

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

    def _connect_signals(self) -> None:
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

        # TCP Server signals
        if self.tcp_server:
            connector.connect(
                self.tcp_server.signals.data_received,
                self.on_measurement_received,
                "tcp_data_received -> on_measurement_received"
            ).connect(
                self.tcp_server.signals.start_received,
                self.on_start_received,
                "tcp_start_received -> on_start_received"
            ).connect(
                self.tcp_server.signals.server_started,
                lambda port: self.tcp_server_status.emit(True, f"TCP 서버 시작 (포트: {port})"),
                "tcp_server_started -> tcp_server_status"
            ).connect(
                self.tcp_server.signals.server_stopped,
                lambda: self.tcp_server_status.emit(False, "TCP 서버 중지"),
                "tcp_server_stopped -> tcp_server_status"
            ).connect(
                self.tcp_server.signals.error_occurred,
                lambda msg: self.error_occurred.emit(f"TCP 오류: {msg}"),
                "tcp_error -> error_occurred"
            )

        if not connector.all_connected():
            logger.error(
                f"일부 시그널 연결 실패: {connector.failed_connections}"
            )

    def on_barcode_scanned(self, wip_id: str) -> None:
        """
        Handle valid WIP barcode scan (initiates threaded operation).

        Args:
            wip_id: WIP ID from barcode
        """
        self.start_work(wip_id)

    def start_work(self, wip_id: str) -> None:
        """
        Start work for the given WIP ID.

        Args:
            wip_id: WIP ID (required)
        """
        if not wip_id:
            logger.error("No WIP ID provided")
            self.error_occurred.emit("WIP ID가 필요합니다.")
            return

        # Get current user
        worker_id = self.auth_service.get_current_user_id()

        logger.info(f"Starting work: WIP={wip_id}, Worker={worker_id}")

        # Store for when work starts successfully
        self.current_wip_id = wip_id
        self.current_worker = worker_id

        # Start work (threaded - result will come via signal)
        self.work_service.start_work(wip_id, worker_id)

    def complete_work(self, completion_data: Dict[str, Any]) -> None:
        """
        Complete work with the given completion data.

        Args:
            completion_data: Completion data including wip_id (required), result, and measurements
        """
        wip_id = completion_data.get("wip_id", "UNKNOWN")
        logger.info(f"Completing work for WIP: {wip_id}")

        # Add worker_id if not present
        if "worker_id" not in completion_data:
            completion_data["worker_id"] = self.auth_service.get_current_user_id()

        # Submit completion to backend (threaded - result will come via signal)
        self.work_service.complete_work(completion_data)

    def on_barcode_invalid(self, barcode: str) -> None:
        """
        Handle invalid barcode format.

        Args:
            barcode: Invalid barcode string
        """
        error_msg = f"잘못된 바코드 형식: {barcode}"
        logger.warning(error_msg)
        self.error_occurred.emit(error_msg)

    def on_serial_barcode_scanned(self, serial_number: str) -> None:
        """
        Handle valid SERIAL barcode scan.

        Args:
            serial_number: Serial number from barcode
        """
        logger.info(f"Serial barcode scanned: {serial_number}")
        # Emit signal for UI to update (MainWindow will handle this)
        self.serial_received.emit(serial_number)

    def on_completion_detected(self, json_data: Dict[str, Any]) -> None:
        """
        Handle JSON completion file detected (initiates threaded operation).

        Args:
            json_data: Completion data from JSON file (must contain wip_id)
        """
        wip_id = json_data.get("wip_id", "UNKNOWN")
        logger.info(f"Processing completion for WIP: {wip_id}")

        # Add worker_id if not present
        if "worker_id" not in json_data:
            json_data["worker_id"] = self.auth_service.get_current_user_id()

        # Submit completion to backend (threaded - result will come via signal)
        self.work_service.complete_work(json_data)

    def on_file_processed(self, filename: str) -> None:
        """
        Handle file processed successfully.

        Args:
            filename: Processed filename
        """
        logger.info(f"File processed: {filename}")

    def on_completion_error(self, error_msg: str) -> None:
        """
        Handle completion processing error.

        Args:
            error_msg: Error message
        """
        logger.error(f"Completion error: {error_msg}")
        self.error_occurred.emit(error_msg)

    def clear_current_wip(self) -> None:
        """Clear current WIP information."""
        self.current_wip_id = None
        self.current_worker = None
        self.lot_updated.emit({})
        logger.info("Current WIP cleared")

    # --- Threaded operation callbacks ---

    def on_login_success(self, user_data: Dict[str, Any]) -> None:
        """Handle successful login from threaded operation."""
        logger.info(f"Login successful (threaded callback): {user_data.get('username')}")

        # Update connection status
        self.is_online = True
        self.connection_status_changed.emit(True)

    def on_work_started_success(self, response: Dict[str, Any]) -> None:
        """Handle successful work start from threaded operation."""
        logger.info(f"Work started successfully (threaded callback): {response}")

        # Store WIP ID from response if available
        wip_id_str = response.get("wip_id_str") or self.current_wip_id

        # Emit signals
        self.work_started.emit(wip_id_str)
        self.lot_updated.emit({
            "wip_id": wip_id_str,
            "worker_id": self.current_worker,
            "start_time": datetime.now().strftime("%H:%M:%S")
        })

        # Update connection status
        self.is_online = True
        self.connection_status_changed.emit(True)

    def on_work_completed_success(self, response: Dict[str, Any]) -> None:
        """Handle successful work completion from threaded operation."""
        wip_id = response.get("wip_id_str", self.current_wip_id or "UNKNOWN")
        logger.info(f"Work completed successfully (threaded callback): {wip_id}")

        # Emit signal
        self.work_completed.emit(f"완공: {wip_id}")

        # Clear current WIP
        self.clear_current_wip()

        # Update connection status
        self.is_online = True
        self.connection_status_changed.emit(True)

    def on_work_service_error(self, error_msg: str) -> None:
        """Handle work service error from threaded operation."""
        logger.error(f"Work service error (threaded callback): {error_msg}")
        self.error_occurred.emit(error_msg)

        # Check if connection error
        if "연결" in error_msg or "Connection" in error_msg or "백엔드 서버에 연결" in error_msg:
            self.is_online = False
            self.connection_status_changed.emit(False)

    def on_serial_converted(self, result: Dict[str, Any]) -> None:
        """Handle successful serial conversion."""
        serial_dict = result.get("serial", {})
        serial_number = serial_dict.get("serial_number")

        if not serial_number:
            self.error_occurred.emit("시리얼 번호를 받지 못했습니다.")
            self.clear_current_wip() # Clear even on error to reset state
            return

        logger.info(f"Serial converted successfully: {serial_number}")

        # Emit signal for UI update
        self.serial_received.emit(serial_number)

        # Clear state after successful conversion
        self.clear_current_wip()

    # --- TCP Server / Equipment Measurement Methods ---

    def on_start_received(self, start_data: Any) -> None:
        """
        Handle successful start work notification from TCP server.

        Note: Backend API call is already done by TCP server synchronously.
        This handler is for UI updates only.

        Args:
            start_data: StartData object from TCP server
        """
        wip_id = start_data.wip_id
        logger.info(f"Start work completed via TCP: wip_id={wip_id}")

        # Update state for UI
        self.current_wip_id = wip_id
        self.current_worker = self.auth_service.get_current_user_id()

        # Emit signal for UI update (work started successfully)
        self.work_started.emit(wip_id)

    def on_measurement_received(self, equipment_data: Any) -> None:
        """
        Handle measurement data received from equipment via TCP.

        Args:
            equipment_data: EquipmentData object from TCP server
        """
        logger.info(
            f"Measurement received: result={equipment_data.result}, "
            f"items={len(equipment_data.measurements)}"
        )

        # Store pending measurement for later use in complete_work
        self.pending_measurement = equipment_data

        # Emit signal for UI to display measurement data
        self.measurement_received.emit(equipment_data)

    def complete_with_measurement(self) -> None:
        """
        Complete work with pending measurement data.

        Called when user confirms completion after receiving measurement.
        """
        if not self.current_wip_id:
            self.error_occurred.emit("착공된 작업이 없습니다.")
            return

        if not self.pending_measurement:
            self.error_occurred.emit("측정 데이터가 없습니다.")
            return

        # Build completion data (wip_id only, no lot_number)
        completion_data = {
            "wip_id": self.current_wip_id,
            "worker_id": self.auth_service.get_current_user_id(),
            "result": self.pending_measurement.result,
            "measurements": self.pending_measurement.to_api_format(),
        }

        # Add defects if FAIL
        if self.pending_measurement.result == "FAIL":
            completion_data["defect_data"] = {
                "defects": [
                    {"code": d.code, "reason": d.reason}
                    for d in self.pending_measurement.defects
                ]
            }

        logger.info(f"Completing work: WIP={self.current_wip_id}")

        # Submit completion
        self.work_service.complete_work(completion_data)

        # Clear pending measurement
        self.pending_measurement = None

    def clear_pending_measurement(self) -> None:
        """Clear pending measurement data without completing."""
        self.pending_measurement = None
        logger.info("Pending measurement cleared")

    def start_tcp_server(self, port: int = DEFAULT_TCP_PORT) -> bool:
        """
        Start TCP server for receiving equipment data.

        Args:
            port: TCP port to listen on

        Returns:
            True if server started successfully
        """
        if not self.tcp_server:
            from services.tcp_server import TCPServer
            self.tcp_server = TCPServer(port=port)
            # Connect signals
            self.tcp_server.signals.data_received.connect(
                self.on_measurement_received
            )
            self.tcp_server.signals.error_occurred.connect(
                lambda msg: self.error_occurred.emit(f"TCP 오류: {msg}")
            )

        return self.tcp_server.start()

    def stop_tcp_server(self) -> None:
        """Stop TCP server."""
        if self.tcp_server:
            self.tcp_server.stop()

    @safe_cleanup("ViewModel 정리 실패")
    def cleanup(self) -> None:
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

        # Stop TCP server if running
        if self.tcp_server:
            cleanup.add(self.tcp_server.stop, "TCP 서버 정지")

        failed = cleanup.execute()
        if failed:
            logger.warning(f"일부 정리 작업 실패: {failed}")

        logger.info("MainViewModel cleanup completed")
