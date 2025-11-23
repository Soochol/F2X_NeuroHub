import logging
from typing import Optional
from app.config import settings

# Try to import zebra, but don't fail if not installed (for dev/test environments)
try:
    from zebra import Zebra
    ZEBRA_AVAILABLE = True
except ImportError:
    ZEBRA_AVAILABLE = False

logger = logging.getLogger(__name__)

class PrinterService:
    """
    Service for printing ZPL labels to Zebra printers.
    """

    def __init__(self, queue_name: Optional[str] = None):
        self.queue_name = queue_name or settings.PRINTER_QUEUE_NAME
        self.zebra = Zebra(self.queue_name) if ZEBRA_AVAILABLE else None

    def print_label(self, serial_number: str, model_code: str, production_date: str) -> bool:
        """
        Print a label for the given serial number.

        Args:
            serial_number: The serial number to print (e.g., KR01PSA2511001)
            model_code: Product model code (e.g., PSA)
            production_date: Production date string

        Returns:
            True if printing was successful (or mocked), False otherwise.
        """
        zpl = self._generate_zpl(serial_number, model_code, production_date)
        
        if not ZEBRA_AVAILABLE:
            logger.warning(f"Zebra library not available. Mocking print for: {serial_number}")
            logger.debug(f"ZPL Content:\n{zpl}")
            return True

        try:
            # Check if queue exists (optional, depending on zebra lib behavior)
            queues = self.zebra.getqueues()
            if self.queue_name not in queues:
                logger.error(f"Printer queue '{self.queue_name}' not found. Available: {queues}")
                return False

            self.zebra.output(zpl)
            logger.info(f"Label printed for {serial_number} on {self.queue_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to print label for {serial_number}: {e}")
            return False

    def _generate_zpl(self, serial_number: str, model_code: str, production_date: str) -> str:
        """
        Generate ZPL code for the label.
        
        Label Size: 40mm x 20mm (approx)
        Content:
        - Data Matrix Code (Serial Number)
        - Text: Serial Number
        - Text: Model Code
        """
        # Basic ZPL template
        # ^XA: Start Format
        # ^FO: Field Origin
        # ^BX: Data Matrix Barcode
        # ^ADN: Font
        # ^FD: Field Data
        # ^FS: Field Separator
        # ^XZ: End Format
        
        zpl = f"""
^XA
^FO20,20^BXN,4,200^FD{serial_number}^FS
^FO100,30^ADN,36,20^FD{serial_number}^FS
^FO100,70^ADN,36,20^FDModel: {model_code}^FS
^FO100,110^ADN,36,20^FDDate: {production_date}^FS
^XZ
"""
        return zpl.strip()

# Global instance
printer_service = PrinterService()
