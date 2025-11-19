"""
Zebra Label Printer Service.

Handles USB Zebra printer communication for label printing in Process 7.
Uses caching for reprint functionality.
"""
import logging
from typing import Optional, List
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

# Try to import zebra library
try:
    from zebra import Zebra
    ZEBRA_AVAILABLE = True
except ImportError:
    ZEBRA_AVAILABLE = False
    logger.warning("zebra library not installed. Run: pip install zebra")


class PrintService(QObject):
    """Zebra label printer service with caching for reprints."""

    # Signals
    print_success = Signal(str)  # serial_number
    print_error = Signal(str)    # error message
    printer_status_changed = Signal(bool)  # is_ready

    def __init__(self, config):
        """
        Initialize PrintService.

        Args:
            config: AppConfig instance with printer settings
        """
        super().__init__()
        self.config = config
        self.printer: Optional['Zebra'] = None
        self.last_serial: Optional[str] = None
        self.last_lot: Optional[str] = None
        self._is_ready = False

        if ZEBRA_AVAILABLE:
            self._initialize_printer()
        else:
            logger.error("Zebra library not available")

    def _initialize_printer(self):
        """Initialize connection to Zebra printer."""
        try:
            self.printer = Zebra()

            # Get configured printer queue
            printer_queue = self.config.printer_queue

            if printer_queue:
                self.printer.setqueue(printer_queue)
                self._is_ready = True
                logger.info(f"Printer initialized: {printer_queue}")
            else:
                # Try to use first available printer
                queues = self.get_available_printers()
                if queues:
                    self.printer.setqueue(queues[0])
                    self._is_ready = True
                    logger.info(f"Printer auto-selected: {queues[0]}")
                else:
                    logger.warning("No printers available")
                    self._is_ready = False

            self.printer_status_changed.emit(self._is_ready)

        except Exception as e:
            logger.error(f"Printer initialization failed: {e}")
            self._is_ready = False
            self.printer_status_changed.emit(False)

    def get_available_printers(self) -> List[str]:
        """
        Get list of available printer queues.

        Returns:
            List of printer queue names
        """
        if not ZEBRA_AVAILABLE or not self.printer:
            return []

        try:
            queues = self.printer.getqueues()
            return queues if queues else []
        except Exception as e:
            logger.error(f"Failed to get printer list: {e}")
            return []

    def set_printer(self, queue_name: str) -> bool:
        """
        Set the active printer queue.

        Args:
            queue_name: Printer queue name

        Returns:
            True if successful
        """
        if not ZEBRA_AVAILABLE or not self.printer:
            return False

        try:
            self.printer.setqueue(queue_name)
            self._is_ready = True
            logger.info(f"Printer set to: {queue_name}")
            self.printer_status_changed.emit(True)
            return True
        except Exception as e:
            logger.error(f"Failed to set printer: {e}")
            self._is_ready = False
            self.printer_status_changed.emit(False)
            return False

    @property
    def is_ready(self) -> bool:
        """Check if printer is ready."""
        return self._is_ready and ZEBRA_AVAILABLE

    def print_label(self, serial_number: str, lot_number: str = "") -> bool:
        """
        Print label with serial number.

        Args:
            serial_number: Serial number to print
            lot_number: LOT number (optional, for caching)

        Returns:
            True if print successful
        """
        if not self.is_ready:
            error_msg = "프린터가 준비되지 않았습니다"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

        try:
            # Generate ZPL
            zpl = self._generate_zpl(serial_number)

            # Send to printer
            self.printer.output(zpl)

            # Cache for reprint
            self.last_serial = serial_number
            self.last_lot = lot_number

            logger.info(f"Label printed: {serial_number}")
            self.print_success.emit(serial_number)
            return True

        except Exception as e:
            error_msg = f"프린트 실패: {str(e)}"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

    def reprint(self) -> bool:
        """
        Reprint last label (no server request).

        Returns:
            True if reprint successful
        """
        if not self.last_serial:
            error_msg = "재출력할 라벨이 없습니다"
            logger.warning(error_msg)
            self.print_error.emit(error_msg)
            return False

        logger.info(f"Reprinting label: {self.last_serial}")
        return self.print_label(self.last_serial, self.last_lot or "")

    def _generate_zpl(self, serial_number: str) -> str:
        """
        Generate ZPL commands for label.

        Args:
            serial_number: Serial number to encode

        Returns:
            ZPL command string
        """
        # Check for custom template
        template_path = self.config.zpl_template_path

        if template_path:
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                    # Replace placeholder with serial number
                    return template.replace("{SERIAL}", serial_number)
            except Exception as e:
                logger.warning(f"Failed to load ZPL template: {e}")

        # Default ZPL template
        return f"""^XA
^FO50,50^A0N,40,40^FD{serial_number}^FS
^FO50,120^BY2^BCN,80,Y,N,N^FD{serial_number}^FS
^XZ"""

    def test_print(self) -> bool:
        """
        Print a test label.

        Returns:
            True if test print successful
        """
        test_serial = "TEST-PRINT-001"
        logger.info("Printing test label")
        return self.print_label(test_serial, "TEST-LOT")

    def clear_cache(self):
        """Clear cached serial number."""
        self.last_serial = None
        self.last_lot = None
        logger.debug("Print cache cleared")

    def get_printer_status(self) -> dict:
        """
        Get current printer status.

        Returns:
            Status dictionary
        """
        return {
            "is_ready": self.is_ready,
            "zebra_available": ZEBRA_AVAILABLE,
            "last_serial": self.last_serial,
            "last_lot": self.last_lot,
            "available_printers": self.get_available_printers()
        }
