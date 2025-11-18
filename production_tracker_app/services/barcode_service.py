"""
Barcode Service for HID barcode reader input handling.
"""
from PySide6.QtCore import QObject, Signal
import re
import logging

logger = logging.getLogger(__name__)


class BarcodeService(QObject):
    """Handle barcode input from HID keyboard emulation scanners."""

    barcode_valid = Signal(str)      # Valid LOT barcode scanned
    barcode_invalid = Signal(str)    # Invalid barcode format

    # LOT number pattern: WF-KR-251110D-001
    LOT_PATTERN = r'^[A-Z]{2}-[A-Z]{2}-\d{6}[DN]-\d{3}$'

    def __init__(self):
        super().__init__()
        self.buffer = ""
        self.last_key_time = 0

    def process_key(self, key: str):
        """
        Process keyboard input for barcode scanning.

        Args:
            key: Single character from keyboard
        """
        if key == '\r' or key == '\n':  # Enter key - barcode complete
            if self.buffer:
                self._process_barcode(self.buffer)
                self.buffer = ""
        elif key.isprintable():
            self.buffer += key

    def _process_barcode(self, barcode: str):
        """
        Process complete barcode string.

        Args:
            barcode: Complete barcode string
        """
        barcode = barcode.strip().upper()
        logger.info(f"Processing barcode: {barcode}")

        if self._is_valid_lot_format(barcode):
            logger.info(f"Valid LOT barcode: {barcode}")
            self.barcode_valid.emit(barcode)
        else:
            logger.warning(f"Invalid LOT barcode format: {barcode}")
            self.barcode_invalid.emit(barcode)

    def _is_valid_lot_format(self, barcode: str) -> bool:
        """
        Check if barcode matches LOT format.

        Args:
            barcode: Barcode string to validate

        Returns:
            True if valid LOT format
        """
        return re.match(self.LOT_PATTERN, barcode) is not None

    def clear_buffer(self):
        """Clear the input buffer."""
        self.buffer = ""
