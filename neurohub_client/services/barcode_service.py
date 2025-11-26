"""
Barcode Service for HID barcode reader input handling.
"""
import logging
import re
from typing import Optional

from PySide6.QtCore import QObject, Signal

from utils.serial_validator import validate_serial_number_v1

logger = logging.getLogger(__name__)


class BarcodeService(QObject):
    """Handle barcode input from HID keyboard emulation scanners."""

    barcode_valid = Signal(str)      # Valid LOT barcode scanned
    serial_valid = Signal(str)       # Valid SERIAL barcode scanned
    wip_valid = Signal(str)          # Valid WIP barcode scanned
    barcode_invalid = Signal(str)    # Invalid barcode format

    # LOT number pattern: WF-KR-251110D-001
    LOT_PATTERN = r'^[A-Z]{2}-[A-Z]{2}-\d{6}[DN]-\d{3}$'

    # WIP ID pattern: WIP-{LOT}-{SEQ:03d} (19 characters)
    # Example: WIP-KR01PSA2511-001
    WIP_PATTERN = r'^WIP-([A-Z0-9]{11})-(\d{3})$'

    # Serial number pattern (V1): KR01PSA2511001 (14 characters)
    SERIAL_PATTERN = r'^[A-Z]{2}\d{2}[A-Z]{3}\d{4}\d{3}$'

    def __init__(self) -> None:
        super().__init__()
        self.buffer: str = ""
        self.last_key_time: int = 0

    def process_key(self, key: str) -> None:
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

    def _process_barcode(self, barcode: str) -> None:
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
        elif self._is_valid_wip_format(barcode):
            logger.info(f"Valid WIP barcode: {barcode}")
            self.wip_valid.emit(barcode)
        elif self._is_valid_serial_format(barcode):
            logger.info(f"Valid SERIAL barcode: {barcode}")
            self.serial_valid.emit(barcode)
        else:
            logger.warning(f"Invalid barcode format: {barcode}")
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

    def _is_valid_wip_format(self, barcode: str) -> bool:
        """
        Check if barcode matches WIP format (19 characters).

        WIP ID Format: WIP-{LOT}-{SEQ:03d}
        Example: WIP-KR01PSA2511-001

        Args:
            barcode: Barcode string to validate

        Returns:
            True if valid WIP format (19 chars, correct pattern, sequence 1-100)
        """
        if len(barcode) != 19:
            return False

        match = re.match(self.WIP_PATTERN, barcode)
        if not match:
            return False

        _lot_number, sequence_str = match.groups()
        sequence = int(sequence_str)

        # Validate sequence range (1-100)
        if sequence < 1 or sequence > 100:
            return False

        return True

    def _is_valid_serial_format(self, barcode: str) -> bool:
        """
        Check if barcode matches SERIAL format (V1).

        Args:
            barcode: Barcode string to validate

        Returns:
            True if valid SERIAL format (V1: 14 chars)
        """
        return validate_serial_number_v1(barcode)

    def clear_buffer(self) -> None:
        """Clear the input buffer."""
        self.buffer = ""
