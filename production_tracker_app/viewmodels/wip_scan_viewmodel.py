"""
ViewModel for WIP Scan.

Handles WIP barcode scanning and information retrieval.
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class WIPScanViewModel(QObject):
    """ViewModel for WIP Scan screen."""

    # Signals
    wip_scanned = Signal(dict)      # WIP information
    scan_history_updated = Signal(list)  # Scan history
    error_occurred = Signal(str)    # Error message

    def __init__(self, api_client):
        """
        Initialize WIPScanViewModel.

        Args:
            api_client: APIClient instance
        """
        super().__init__()
        self.api_client = api_client
        self.scan_history: List[Dict] = []
        self.current_wip: Optional[Dict] = None

    def scan_wip(self, wip_id: str):
        """
        Scan WIP barcode and retrieve information.

        Args:
            wip_id: WIP serial number
        """
        try:
            logger.info(f"Scanning WIP: {wip_id}")

            # Validate format
            from utils.barcode_utils import validate_serial
            if not validate_serial(wip_id):
                error_msg = f"잘못된 Serial 번호 형식: {wip_id}"
                logger.warning(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # Call API to get WIP information
            wip_info = self.api_client.scan_wip(wip_id)

            # Store current WIP
            self.current_wip = wip_info

            # Add to scan history
            self._add_to_history(wip_id, wip_info, success=True)

            # Emit signal
            self.wip_scanned.emit(wip_info)
            logger.info(f"WIP scanned successfully: {wip_id}")

        except Exception as e:
            error_msg = f"WIP 스캔 실패: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

            # Add to scan history as failure
            self._add_to_history(wip_id, None, success=False, error=str(e))

    def _add_to_history(
        self,
        wip_id: str,
        wip_info: Optional[Dict],
        success: bool,
        error: str = ""
    ):
        """
        Add scan to history.

        Args:
            wip_id: WIP serial number
            wip_info: WIP information (if successful)
            success: Scan success flag
            error: Error message (if failed)
        """
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "wip_id": wip_id,
            "success": success,
            "error": error
        }

        if wip_info:
            history_entry["lot_number"] = wip_info.get("lot_number", "")
            history_entry["product_name"] = wip_info.get("product_name", "")
            history_entry["current_process"] = wip_info.get("current_process", "")

        # Add to history (keep last 50)
        self.scan_history.insert(0, history_entry)
        if len(self.scan_history) > 50:
            self.scan_history = self.scan_history[:50]

        self.scan_history_updated.emit(self.scan_history)

    def clear_history(self):
        """Clear scan history."""
        self.scan_history.clear()
        self.scan_history_updated.emit(self.scan_history)
        logger.info("Scan history cleared")

    def get_current_wip(self) -> Optional[Dict]:
        """
        Get currently scanned WIP.

        Returns:
            WIP information dict or None
        """
        return self.current_wip

    def cleanup(self):
        """Clean up resources."""
        self.current_wip = None
