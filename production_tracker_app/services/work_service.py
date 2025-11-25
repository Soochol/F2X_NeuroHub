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

from utils.exception_handler import safe_cleanup
from utils.serial_validator import validate_serial_number_v1

logger = logging.getLogger(__name__)


class WorkService(QObject):
    """Handle work start and completion API calls with non-blocking threading."""

    # Signals for threaded operations
    work_started = Signal(dict)     # Work started successfully
    work_completed = Signal(dict)   # Work completed successfully
    serial_converted = Signal(dict) # Serial converted successfully
    error_occurred = Signal(str)    # Operation failed

    def __init__(self, api_client: APIClient, config):
        super().__init__()
        self.api_client = api_client
        self.config = config
        self._active_workers = []

    def start_work(
        self, lot_number: str, worker_id: str, serial_number: str = None
    ):
        """
        Start work for LOT or Serial - POST /api/v1/process-operations/start

        Args:
            lot_number: LOT number
            worker_id: Worker ID
            serial_number: Serial number (optional - only for SERIAL-level work)

        Note:
            - If serial_number is provided → SERIAL-level work (backend requires Serial record)
            - If serial_number is None → LOT-level work (backend does not require Serial record)
        """
        try:
            # Validate serial_number format if provided
            if serial_number:
                if not validate_serial_number_v1(serial_number):
                    error_msg = f"잘못된 Serial 번호 형식: {serial_number}. V1 형식 필요 (14자)"
                    logger.error(error_msg)
                    self.error_occurred.emit(error_msg)
                    return

                logger.info(f"Starting SERIAL work (threaded) for Serial: {serial_number}, LOT: {lot_number}")
            else:
                logger.info(f"Starting LOT work (threaded) for LOT: {lot_number}")

            # Build base request data
            data = {
                "lot_number": lot_number,
                # Database PK as string
                "process_id": str(self.config.process_db_id),
                "worker_id": worker_id,
                "equipment_id": self.config.equipment_code,
                "line_id": self.config.line_code,
                "start_time": datetime.now().isoformat()
            }

            # Only include serial_number if provided (SERIAL-level work)
            if serial_number:
                data["serial_number"] = serial_number

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
        Complete work from JSON file.

        POST /api/v1/process-operations/complete (non-blocking)

        Note:
            - If json_data contains 'serial_number' → SERIAL-level work completion
            - If json_data does NOT contain 'serial_number' → LOT-level work completion
        """
        try:
            lot_number = json_data.get('lot_number', 'UNKNOWN')
            serial_number = json_data.get('serial_number')  # May be None

            # Validate serial_number format if provided
            if serial_number:
                if not validate_serial_number_v1(serial_number):
                    error_msg = f"잘못된 Serial 번호 형식: {serial_number}. V1 형식 필요 (14자)"
                    logger.error(error_msg)
                    self.error_occurred.emit(error_msg)
                    return

                logger.info(
                    f"Completing SERIAL work (threaded) for Serial: {serial_number}, LOT: {lot_number}"
                )
            else:
                logger.info(
                    f"Completing LOT work (threaded) for LOT: {lot_number}"
                )

            # Build base complete data with process_id from config
            data = {
                "lot_number": lot_number,
                # Database PK as integer
                "process_id": str(self.config.process_db_id),
                "worker_id": json_data.get('worker_id', 'W001'),
                "result": json_data.get('result', 'PASS'),
                "measurements": json_data.get('measurements') or json_data.get('measurement_data'),
                "defect_data": json_data.get('defect_data')
            }

            # Only include serial_number if provided (SERIAL-level work)
            if serial_number:
                data["serial_number"] = serial_number

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

    def convert_wip_to_serial(self, wip_id: int, operator_id: int):
        """
        Convert WIP to Serial - POST /api/v1/wip-items/{wip_id}/convert-to-serial

        Args:
            wip_id: WIP item ID
            operator_id: Operator ID
        """
        try:
            logger.info(f"Converting WIP {wip_id} to Serial (threaded)")

            data = {
                "operator_id": operator_id,
                "notes": "Converted via Production Tracker App"
            }

            worker = APIWorker(
                api_client=self.api_client,
                operation="convert_serial",
                method="POST",
                endpoint=f"/api/v1/wip-items/{wip_id}/convert-to-serial",
                data=data
            )
            worker.success.connect(self._on_api_success)
            worker.error.connect(self._on_api_error)
            worker.finished.connect(lambda: self._cleanup_worker(worker))

            self._active_workers.append(worker)
            worker.start()
        except Exception as e:
            error_msg = f"시리얼 변환 요청 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def _on_api_success(self, operation: str, result: dict):
        """Handle successful API call based on operation type."""
        logger.info(f"API success [{operation}]: {result}")

        if operation == "start_work":
            self.work_started.emit(result)
        elif operation == "complete_work":
            self.work_completed.emit(result)
        elif operation == "convert_serial":
            self.serial_converted.emit(result)

    def _on_api_error(self, operation: str, error_msg: str):
        """Handle API error with user-friendly messages."""
        logger.error(f"API error [{operation}]: {error_msg}")

        # Parse and enhance error messages for better UX
        friendly_msg = self._make_user_friendly_message(error_msg)

        if operation == "start_work":
            self.error_occurred.emit(f"착공 등록 실패: {friendly_msg}")
        elif operation == "complete_work":
            self.error_occurred.emit(f"완공 처리 실패: {friendly_msg}")
        elif operation == "convert_serial":
            self.error_occurred.emit(f"시리얼 변환 실패: {friendly_msg}")

    def _make_user_friendly_message(self, error_msg: str) -> str:
        """
        Convert technical error messages to user-friendly Korean messages.

        Args:
            error_msg: Raw error message from API client

        Returns:
            User-friendly error message in Korean
        """
        error_lower = error_msg.lower()

        # Duplicate work start (most common)
        if "already exists" in error_lower or "duplicate" in error_lower:
            return "이미 착공된 작업입니다. 다른 LOT 번호를 사용하세요."

        # Already in progress
        if "already in progress" in error_lower or "이미 처리된" in error_lower:
            return "이미 진행 중인 작업입니다. 완공 후 다시 시도하세요."

        # LOT not found
        if ("not found" in error_lower and "lot" in error_lower):
            return "LOT가 등록되지 않았습니다. 먼저 LOT를 발행하세요."

        # Serial not found
        if ("not found" in error_lower and "serial" in error_lower):
            return "시리얼 번호가 존재하지 않습니다. LOT 정보를 확인하세요."

        # Process not found
        if ("not found" in error_lower and "process" in error_lower):
            return "공정 정보를 찾을 수 없습니다. 설정을 확인하세요."

        # Worker/User not found
        if ("not found" in error_lower and
            ("worker" in error_lower or "user" in error_lower)):
            return "작업자 정보를 찾을 수 없습니다. 다시 로그인하세요."

        # Process sequence validation
        if "previous process" in error_lower or "process sequence" in error_lower:
            return "이전 공정이 완료되지 않았습니다. 공정 순서를 확인하세요."

        # Connection errors
        if "연결할 수 없습니다" in error_msg or "connection" in error_lower:
            return "서버에 연결할 수 없습니다. 네트워크를 확인하세요."

        # Timeout errors
        if "timeout" in error_lower or "시간이 초과" in error_msg:
            return "서버 응답 시간이 초과되었습니다. 다시 시도하세요."

        # Authentication errors
        if "인증" in error_msg or "unauthorized" in error_lower:
            return "인증이 만료되었습니다. 다시 로그인하세요."

        # Return original message if no pattern matched
        # (api_client already converted it to Korean)
        return error_msg


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