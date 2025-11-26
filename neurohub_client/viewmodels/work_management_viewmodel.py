"""
ViewModel for Work Management (Start Work & Complete Work).

Handles process start and completion for both LOT-level and Serial-level work.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, QTimer, Signal

logger = logging.getLogger(__name__)


class WorkManagementViewModel(QObject):
    """ViewModel for Work Management screens."""

    # Signals
    work_started = Signal(dict)         # Work start result
    work_completed = Signal(dict)       # Work completion result
    work_info_updated = Signal(dict)    # Current work info updated
    elapsed_time_updated = Signal(str)  # Elapsed time string (formatted)
    error_occurred = Signal(str)        # Error message

    # Update interval for elapsed time (1 second)
    TIMER_INTERVAL_MS = 1000

    def __init__(self, api_client: Any, config: Any) -> None:
        """
        Initialize WorkManagementViewModel.

        Args:
            api_client: APIClient instance
            config: AppConfig instance (for worker_id, equipment_id, etc.)
        """
        super().__init__()
        self.api_client = api_client
        self.config = config

        # Current work state
        self.current_work: Optional[Dict[str, Any]] = None
        self.work_start_time: Optional[datetime] = None
        self.is_serial_level: bool = False

        # Elapsed time timer
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self._update_elapsed_time)

    def start_work_lot_level(self, lot_number: str) -> None:
        """
        Start LOT-level work.

        Args:
            lot_number: LOT number to start work on
        """
        try:
            logger.info(f"Starting LOT-level work: {lot_number}")

            # Get process and equipment info from config
            process_number = self.config.process_number
            line_code = self.config.line_code
            equipment_code = self.config.equipment_code

            if not process_number:
                error_msg = "공정 번호가 설정되지 않았습니다. 설정 메뉴에서 공정을 선택하세요."
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # Prepare process data
            process_data = {
                "lot_number": lot_number,
                "process_number": process_number,
                "line_code": line_code,
                "equipment_code": equipment_code,
                "start_time": datetime.now().isoformat(),
                "level": "LOT"  # LOT-level work
            }

            # Call API to start LOT work
            result = self.api_client.post(
                f"/api/v1/lots/start-work",
                process_data
            )

            # Store current work
            self.current_work = {
                "lot_number": lot_number,
                "serial_number": None,
                "process_number": process_number,
                "line_code": line_code,
                "equipment_code": equipment_code,
                "level": "LOT",
                "work_id": result.get("work_id")
            }
            self.work_start_time = datetime.now()
            self.is_serial_level = False

            # Start elapsed time timer
            self.elapsed_timer.start(self.TIMER_INTERVAL_MS)

            # Emit signals
            self.work_started.emit(result)
            self.work_info_updated.emit(self.current_work)

            logger.info(f"LOT-level work started successfully: {lot_number}")

        except Exception as e:
            error_msg = f"작업 시작 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def start_work_serial_level(self, lot_number: str, serial_number: str) -> None:
        """
        Start Serial-level work.

        Args:
            lot_number: LOT number
            serial_number: Serial number to start work on
        """
        try:
            logger.info(f"Starting Serial-level work: {serial_number} (LOT: {lot_number})")

            # Get process and equipment info from config
            process_number = self.config.process_number
            line_code = self.config.line_code
            equipment_code = self.config.equipment_code

            if not process_number:
                error_msg = "공정 번호가 설정되지 않았습니다. 설정 메뉴에서 공정을 선택하세요."
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # Prepare process data
            process_data = {
                "process_number": process_number,
                "line_code": line_code,
                "equipment_code": equipment_code,
                "start_time": datetime.now().isoformat(),
                "level": "SERIAL"  # Serial-level work
            }

            # Call API to start serial work
            result = self.api_client.start_process(serial_number, process_data)

            # Store current work
            self.current_work = {
                "lot_number": lot_number,
                "serial_number": serial_number,
                "process_number": process_number,
                "line_code": line_code,
                "equipment_code": equipment_code,
                "level": "SERIAL",
                "work_id": result.get("work_id")
            }
            self.work_start_time = datetime.now()
            self.is_serial_level = True

            # Start elapsed time timer
            self.elapsed_timer.start(self.TIMER_INTERVAL_MS)

            # Emit signals
            self.work_started.emit(result)
            self.work_info_updated.emit(self.current_work)

            logger.info(f"Serial-level work started successfully: {serial_number}")

        except Exception as e:
            error_msg = f"작업 시작 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def complete_work_pass(self, measurements: Optional[Dict[str, Any]] = None) -> None:
        """
        Complete current work with PASS result.

        Args:
            measurements: Optional process measurements
        """
        self._complete_work("PASS", measurements=measurements)

    def complete_work_fail(
        self,
        defect_type: Optional[str] = None,
        defect_description: Optional[str] = None
    ) -> None:
        """
        Complete current work with FAIL result.

        Args:
            defect_type: Type of defect
            defect_description: Description of defect
        """
        self._complete_work(
            "FAIL",
            defect_type=defect_type,
            defect_description=defect_description
        )

    def _complete_work(
        self,
        result: str,
        measurements: Optional[Dict[str, Any]] = None,
        defect_type: Optional[str] = None,
        defect_description: Optional[str] = None
    ) -> None:
        """
        Complete current work.

        Args:
            result: PASS or FAIL
            measurements: Optional measurements
            defect_type: Defect type if FAIL
            defect_description: Defect description if FAIL
        """
        if not self.current_work:
            error_msg = "진행 중인 작업이 없습니다."
            logger.warning(error_msg)
            self.error_occurred.emit(error_msg)
            return

        try:
            logger.info(f"Completing work: {result}")

            # Prepare completion data
            completion_data = {
                "process_number": self.current_work["process_number"],
                "result": result,
                "complete_time": datetime.now().isoformat(),
            }

            # Add optional fields
            if measurements:
                completion_data["measurements"] = measurements
            if defect_type:
                completion_data["defect_type"] = defect_type
            if defect_description:
                completion_data["defect_description"] = defect_description

            # Call appropriate API based on work level
            if self.is_serial_level:
                # Serial-level completion
                serial_number = self.current_work["serial_number"]
                api_result = self.api_client.complete_process(serial_number, completion_data)
            else:
                # LOT-level completion
                lot_number = self.current_work["lot_number"]
                completion_data["lot_number"] = lot_number
                api_result = self.api_client.post(
                    f"/api/v1/lots/complete-work",
                    completion_data
                )

            # Stop timer
            self.elapsed_timer.stop()

            # Emit completion signal
            self.work_completed.emit(api_result)

            # Reset work state
            self.current_work = None
            self.work_start_time = None
            self.is_serial_level = False

            logger.info(f"Work completed successfully: {result}")

        except Exception as e:
            error_msg = f"작업 완료 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

    def _update_elapsed_time(self) -> None:
        """Update elapsed time and emit signal."""
        if self.work_start_time:
            elapsed = datetime.now() - self.work_start_time
            elapsed_str = self._format_timedelta(elapsed)
            self.elapsed_time_updated.emit(elapsed_str)

    def _format_timedelta(self, td: timedelta) -> str:
        """
        Format timedelta as HH:MM:SS.

        Args:
            td: Timedelta to format

        Returns:
            Formatted time string
        """
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_current_work(self) -> Optional[Dict[str, Any]]:
        """
        Get current work information.

        Returns:
            Current work dict or None
        """
        return self.current_work

    def has_active_work(self) -> bool:
        """
        Check if there is active work.

        Returns:
            True if work is in progress
        """
        return self.current_work is not None

    def get_elapsed_time(self) -> str:
        """
        Get current elapsed time.

        Returns:
            Formatted elapsed time string
        """
        if self.work_start_time:
            elapsed = datetime.now() - self.work_start_time
            return self._format_timedelta(elapsed)
        return "00:00:00"

    def cancel_work(self) -> None:
        """
        Cancel current work without completing it.

        This stops the timer but doesn't send completion to API.
        Use carefully - typically for error recovery.
        """
        logger.warning("Work cancelled manually")
        self.elapsed_timer.stop()
        self.current_work = None
        self.work_start_time = None
        self.is_serial_level = False

    def cleanup(self) -> None:
        """Clean up resources."""
        self.elapsed_timer.stop()
        self.current_work = None
        self.work_start_time = None
