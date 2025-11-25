"""
Barcode Utility Functions for Production Tracker.

Provides barcode parsing, validation, and generation utilities.
"""
import re
from typing import Optional, Dict, Tuple
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# Try to import barcode libraries
try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False
    logger.warning("python-barcode not installed. Run: pip install python-barcode")

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("qrcode not installed. Run: pip install qrcode[pil]")


# Serial Number V1 Format: 14 characters
# Example: KR01PSA2511001
# Structure: CC NN PPP YYMM SSS
#   CC: Country Code (2 chars) - KR
#   NN: Line Number (2 digits) - 01
#   PPP: Product Code (3 chars) - PSA
#   YYMM: Year Month (4 digits) - 2511
#   SSS: Sequence (3 digits) - 001
SERIAL_V1_PATTERN = r'^([A-Z]{2})(\d{2})([A-Z]{3})(\d{4})(\d{3})$'
SERIAL_V1_LENGTH = 14

# LOT Number Format
# Example: WF-KR-251110D-001
# Structure: PP-CC-YYMMDDT-SSS
#   PP: Product Family (2 chars) - WF
#   CC: Country Code (2 chars) - KR
#   YYMMDD: Date (6 digits) - 251110
#   T: Type (1 char) - D (Day) or N (Night)
#   SSS: Sequence (3 digits) - 001
LOT_PATTERN = r'^([A-Z]{2})-([A-Z]{2})-(\d{6})([DN])-(\d{3})$'


class BarcodeParser:
    """Parser for barcode strings."""

    @staticmethod
    def parse_serial_v1(serial: str) -> Optional[Dict[str, str]]:
        """
        Parse V1 serial number format.

        Args:
            serial: Serial number string (14 chars)

        Returns:
            Dictionary with parsed components or None if invalid:
                - country_code: Country code (2 chars)
                - line_number: Line number (2 digits)
                - product_code: Product code (3 chars)
                - year_month: Year-month (4 digits)
                - sequence: Sequence number (3 digits)
        """
        match = re.match(SERIAL_V1_PATTERN, serial.upper())
        if not match:
            return None

        return {
            'country_code': match.group(1),
            'line_number': match.group(2),
            'product_code': match.group(3),
            'year_month': match.group(4),
            'sequence': match.group(5)
        }

    @staticmethod
    def parse_lot(lot: str) -> Optional[Dict[str, str]]:
        """
        Parse LOT number format.

        Args:
            lot: LOT number string

        Returns:
            Dictionary with parsed components or None if invalid:
                - product_family: Product family (2 chars)
                - country_code: Country code (2 chars)
                - date: Date (6 digits YYMMDD)
                - shift_type: D (Day) or N (Night)
                - sequence: Sequence number (3 digits)
        """
        match = re.match(LOT_PATTERN, lot.upper())
        if not match:
            return None

        return {
            'product_family': match.group(1),
            'country_code': match.group(2),
            'date': match.group(3),
            'shift_type': match.group(4),
            'sequence': match.group(5)
        }

    @staticmethod
    def validate_serial_v1(serial: str) -> bool:
        """
        Validate V1 serial number format.

        Args:
            serial: Serial number string

        Returns:
            True if valid V1 format
        """
        if not serial or len(serial) != SERIAL_V1_LENGTH:
            return False
        return bool(re.match(SERIAL_V1_PATTERN, serial.upper()))

    @staticmethod
    def validate_lot(lot: str) -> bool:
        """
        Validate LOT number format.

        Args:
            lot: LOT number string

        Returns:
            True if valid LOT format
        """
        if not lot:
            return False
        return bool(re.match(LOT_PATTERN, lot.upper()))

    @staticmethod
    def format_serial_v1(serial: str) -> str:
        """
        Format serial number to V1 format (uppercase, no spaces).

        Args:
            serial: Serial number string

        Returns:
            Formatted serial number
        """
        return serial.upper().strip()

    @staticmethod
    def format_lot(lot: str) -> str:
        """
        Format LOT number (uppercase, no spaces).

        Args:
            lot: LOT number string

        Returns:
            Formatted LOT number
        """
        return lot.upper().strip()


class BarcodeGenerator:
    """Generate barcode images and ZPL commands."""

    @staticmethod
    def generate_code128_image(data: str, width: int = 300, height: int = 100) -> Optional[bytes]:
        """
        Generate Code128 barcode image (PNG).

        Args:
            data: Data to encode
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            PNG image bytes or None if generation failed
        """
        if not BARCODE_AVAILABLE:
            logger.error("python-barcode not available")
            return None

        try:
            # Generate Code128 barcode
            code128 = barcode.get('code128', data, writer=ImageWriter())

            # Render to BytesIO
            buffer = BytesIO()
            code128.write(buffer, options={
                'module_width': 0.2,
                'module_height': height / 10,
                'quiet_zone': 6.5,
                'font_size': 10,
                'text_distance': 5,
                'write_text': True
            })

            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to generate Code128 barcode: {e}")
            return None

    @staticmethod
    def generate_qr_image(data: str, size: int = 300) -> Optional[bytes]:
        """
        Generate QR code image (PNG).

        Args:
            data: Data to encode
            size: Image size in pixels (square)

        Returns:
            PNG image bytes or None if generation failed
        """
        if not QRCODE_AVAILABLE:
            logger.error("qrcode not available")
            return None

        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Render to image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return None

    @staticmethod
    def generate_zpl_code128(data: str, x: int = 50, y: int = 50, height: int = 80) -> str:
        """
        Generate ZPL command for Code128 barcode.

        Args:
            data: Data to encode
            x: X position in dots
            y: Y position in dots
            height: Barcode height in dots

        Returns:
            ZPL command string
        """
        # ^BCN - Code128 barcode
        # Parameters: orientation (N=normal), height, print interpretation line (Y/N),
        #             print interpretation line above (Y/N), UCC check digit (Y/N)
        return f"^FO{x},{y}^BY2^BCN,{height},Y,N,N^FD{data}^FS"

    @staticmethod
    def generate_zpl_qr(data: str, x: int = 50, y: int = 50, magnification: int = 5) -> str:
        """
        Generate ZPL command for QR code.

        Args:
            data: Data to encode
            x: X position in dots
            y: Y position in dots
            magnification: QR code magnification factor (1-10)

        Returns:
            ZPL command string
        """
        # ^BQN - QR code
        # Parameters: orientation (N=normal), model (2=enhanced), magnification
        return f"^FO{x},{y}^BQN,2,{magnification}^FDQA,{data}^FS"

    @staticmethod
    def generate_zpl_label(
        serial: str,
        barcode_type: str = 'code128',
        include_text: bool = True
    ) -> str:
        """
        Generate complete ZPL label with serial number.

        Args:
            serial: Serial number to encode
            barcode_type: 'code128' or 'qr'
            include_text: Include human-readable text

        Returns:
            Complete ZPL command string
        """
        zpl_parts = ["^XA"]  # Start format

        # Add text if requested
        if include_text:
            zpl_parts.append(f"^FO50,30^A0N,30,30^FDSerial: {serial}^FS")

        # Add barcode
        if barcode_type.lower() == 'qr':
            zpl_parts.append(BarcodeGenerator.generate_zpl_qr(serial, x=50, y=80, magnification=5))
        else:  # code128
            zpl_parts.append(BarcodeGenerator.generate_zpl_code128(serial, x=50, y=80, height=80))

        zpl_parts.append("^XZ")  # End format

        return "\n".join(zpl_parts)


# Convenience functions
def parse_serial(serial: str) -> Optional[Dict[str, str]]:
    """Parse serial number. Alias for BarcodeParser.parse_serial_v1."""
    return BarcodeParser.parse_serial_v1(serial)


def parse_lot(lot: str) -> Optional[Dict[str, str]]:
    """Parse LOT number. Alias for BarcodeParser.parse_lot."""
    return BarcodeParser.parse_lot(lot)


def validate_serial(serial: str) -> bool:
    """Validate serial number. Alias for BarcodeParser.validate_serial_v1."""
    return BarcodeParser.validate_serial_v1(serial)


def validate_lot(lot: str) -> bool:
    """Validate LOT number. Alias for BarcodeParser.validate_lot."""
    return BarcodeParser.validate_lot(lot)


def format_serial(serial: str) -> str:
    """Format serial number. Alias for BarcodeParser.format_serial_v1."""
    return BarcodeParser.format_serial_v1(serial)


def format_lot(lot: str) -> str:
    """Format LOT number. Alias for BarcodeParser.format_lot."""
    return BarcodeParser.format_lot(lot)
