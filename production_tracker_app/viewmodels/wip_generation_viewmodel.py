"""
ViewModel for WIP Generation.

Handles LOT selection and WIP generation with barcode printing.
"""
import logging
from typing import List, Optional, Dict
from PySide6.QtCore import QObject, Signal, QThread

logger = logging.getLogger(__name__)


class WIPGenerationWorker(QThread):
    """Background worker for WIP generation."""

    progress = Signal(int, str)  # progress percentage, message
    finished = Signal(dict)      # generation result
    error = Signal(str)          # error message

    def __init__(self, api_client, lot_id: int, print_service=None):
        super().__init__()
        self.api_client = api_client
        self.lot_id = lot_id
        self.print_service = print_service

    def run(self):
        """Execute WIP generation."""
        try:
            # Step 1: Request WIP generation (50%)
            self.progress.emit(10, "WIP 생성 요청 중...")
            result = self.api_client.start_wip_generation(self.lot_id)

            generated_serials = result.get("generated_serials", [])
            total_count = len(generated_serials)

            if total_count == 0:
                self.error.emit("생성된 Serial이 없습니다")
                return

            self.progress.emit(50, f"{total_count}개 Serial 생성 완료")

            # Step 2: Print barcodes (50% ~ 100%)
            if self.print_service:
                for idx, serial_data in enumerate(generated_serials):
                    serial_number = serial_data.get("serial_number", "")
                    lot_number = serial_data.get("lot_number", "")

                    # Print label
                    success = self.print_service.print_label(serial_number, lot_number)

                    if not success:
                        logger.warning(f"Failed to print: {serial_number}")

                    # Update progress
                    progress_pct = 50 + int((idx + 1) / total_count * 50)
                    self.progress.emit(progress_pct, f"바코드 출력 중 ({idx + 1}/{total_count})")

            self.progress.emit(100, "WIP 생성 완료")
            self.finished.emit(result)

        except Exception as e:
            error_msg = f"WIP 생성 실패: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)


class WIPGenerationViewModel(QObject):
    """ViewModel for WIP Generation screen."""

    # Signals
    lots_loaded = Signal(list)                  # LOT list loaded
    wip_generation_started = Signal()           # Generation started
    wip_generation_progress = Signal(int, str)  # Progress (%, message)
    wip_generation_completed = Signal(dict)     # Generation result
    error_occurred = Signal(str)                # Error message

    def __init__(self, api_client, print_service=None):
        """
        Initialize WIPGenerationViewModel.

        Args:
            api_client: APIClient instance
            print_service: PrintService instance (optional)
        """
        super().__init__()
        self.api_client = api_client
        self.print_service = print_service
        self.worker: Optional[WIPGenerationWorker] = None
        self.current_lots: List[Dict] = []

    def load_lots(self, status: str = "CREATED"):
        """
        Load LOTs with specified status.

        Args:
            status: LOT status filter (default: CREATED)
        """
        try:
            logger.info(f"Loading LOTs with status: {status}")
            lots = self.api_client.get_lots(status=status)
            self.current_lots = lots
            self.lots_loaded.emit(lots)
            logger.info(f"Loaded {len(lots)} LOTs")

        except Exception as e:
            error_msg = f"LOT 목록 조회 실패: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def start_wip_generation(self, lot_id: int):
        """
        Start WIP generation for selected LOT.

        Args:
            lot_id: LOT database ID
        """
        if self.worker and self.worker.isRunning():
            logger.warning("WIP generation already in progress")
            return

        logger.info(f"Starting WIP generation for LOT ID: {lot_id}")
        self.wip_generation_started.emit()

        # Create and start worker
        self.worker = WIPGenerationWorker(
            self.api_client,
            lot_id,
            self.print_service
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, percentage: int, message: str):
        """Handle progress update."""
        logger.debug(f"Progress: {percentage}% - {message}")
        self.wip_generation_progress.emit(percentage, message)

    def _on_finished(self, result: dict):
        """Handle generation completion."""
        generated_count = len(result.get("generated_serials", []))
        logger.info(f"WIP generation completed: {generated_count} serials")
        self.wip_generation_completed.emit(result)

        # Reload LOT list
        self.load_lots("CREATED")

    def _on_error(self, error_msg: str):
        """Handle generation error."""
        logger.error(f"WIP generation error: {error_msg}")
        self.error_occurred.emit(error_msg)

    def get_lot_by_id(self, lot_id: int) -> Optional[Dict]:
        """
        Get LOT from current list by ID.

        Args:
            lot_id: LOT database ID

        Returns:
            LOT dict or None
        """
        for lot in self.current_lots:
            if lot.get("id") == lot_id:
                return lot
        return None

    def cleanup(self):
        """Clean up resources."""
        if self.worker and self.worker.isRunning():
            logger.info("Stopping WIP generation worker")
            self.worker.terminate()
            self.worker.wait(3000)
