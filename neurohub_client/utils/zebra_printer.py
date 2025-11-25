"""
Zebra Network Printer Utility.

Handles TCP/IP communication with Zebra label printers using ZPL commands.
Supports both USB (via print_service.py) and network printers.
"""
import socket
import logging
from typing import Optional, Tuple
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ZebraPrinter(QObject):
    """
    Network Zebra printer communication using ZPL over TCP/IP.

    For USB printers, use PrintService instead.
    """

    # Signals
    print_success = Signal(str)  # Printed data
    print_error = Signal(str)    # Error message
    status_changed = Signal(bool)  # Connection status

    # Default settings
    DEFAULT_PORT = 9100
    DEFAULT_TIMEOUT = 5.0  # seconds

    def __init__(self, ip_address: str = "", port: int = DEFAULT_PORT):
        """
        Initialize ZebraPrinter.

        Args:
            ip_address: Printer IP address
            port: Printer port (default: 9100 for raw ZPL)
        """
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.timeout = self.DEFAULT_TIMEOUT
        self._is_connected = False

    def set_printer(self, ip_address: str, port: int = DEFAULT_PORT):
        """
        Set printer IP and port.

        Args:
            ip_address: Printer IP address
            port: Printer port
        """
        self.ip_address = ip_address
        self.port = port
        self._is_connected = False
        logger.info(f"Printer configured: {ip_address}:{port}")

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to printer.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.ip_address:
            return False, "IP 주소가 설정되지 않았습니다"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.ip_address, self.port))

                # Send status request
                sock.sendall(b"~HQES\n")  # Host Query Extended Status

                # Try to receive response
                try:
                    response = sock.recv(1024)
                    logger.info(f"Printer status response: {response.decode('utf-8', errors='ignore')}")
                except socket.timeout:
                    logger.warning("No response from printer (might be normal)")

                self._is_connected = True
                self.status_changed.emit(True)
                return True, f"연결 성공: {self.ip_address}:{self.port}"

        except socket.timeout:
            error_msg = f"연결 시간 초과: {self.ip_address}:{self.port}"
            logger.error(error_msg)
            self._is_connected = False
            self.status_changed.emit(False)
            return False, error_msg

        except socket.error as e:
            error_msg = f"연결 실패: {e}"
            logger.error(error_msg)
            self._is_connected = False
            self.status_changed.emit(False)
            return False, error_msg

        except Exception as e:
            error_msg = f"예상치 못한 오류: {e}"
            logger.error(error_msg)
            self._is_connected = False
            self.status_changed.emit(False)
            return False, error_msg

    def send_zpl(self, zpl_command: str) -> bool:
        """
        Send ZPL command to printer.

        Args:
            zpl_command: ZPL command string

        Returns:
            True if successful
        """
        if not self.ip_address:
            error_msg = "프린터 IP가 설정되지 않았습니다"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.ip_address, self.port))

                # Send ZPL command
                sock.sendall(zpl_command.encode('utf-8'))

                logger.info(f"ZPL sent to {self.ip_address}:{self.port}")
                logger.debug(f"ZPL command: {zpl_command}")

                self._is_connected = True
                self.status_changed.emit(True)
                self.print_success.emit(zpl_command)
                return True

        except socket.timeout:
            error_msg = f"전송 시간 초과: {self.ip_address}:{self.port}"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

        except socket.error as e:
            error_msg = f"전송 실패: {e}"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

        except Exception as e:
            error_msg = f"예상치 못한 오류: {e}"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

    def print_label(
        self,
        data: str,
        barcode_type: str = 'code128',
        include_text: bool = True
    ) -> bool:
        """
        Print label with barcode.

        Args:
            data: Data to encode (serial number, LOT number, etc.)
            barcode_type: 'code128' or 'qr'
            include_text: Include human-readable text

        Returns:
            True if successful
        """
        from utils.barcode_utils import BarcodeGenerator

        zpl = BarcodeGenerator.generate_zpl_label(
            data,
            barcode_type=barcode_type,
            include_text=include_text
        )

        return self.send_zpl(zpl)

    def print_custom_zpl(self, zpl_template: str, **kwargs) -> bool:
        """
        Print using custom ZPL template with variable substitution.

        Args:
            zpl_template: ZPL template with {VARIABLE} placeholders
            **kwargs: Variables to substitute

        Returns:
            True if successful

        Example:
            template = "^XA^FO50,50^A0N,40^FD{SERIAL}^FS^XZ"
            printer.print_custom_zpl(template, SERIAL="KR01PSA2511001")
        """
        try:
            zpl = zpl_template.format(**kwargs)
            return self.send_zpl(zpl)
        except KeyError as e:
            error_msg = f"템플릿 변수 누락: {e}"
            logger.error(error_msg)
            self.print_error.emit(error_msg)
            return False

    def get_printer_status(self) -> str:
        """
        Request printer status using ZPL.

        Returns:
            Status string from printer or error message
        """
        if not self.ip_address:
            return "프린터 IP 미설정"

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.ip_address, self.port))

                # Request host status
                sock.sendall(b"~HS\n")

                # Read response
                response = sock.recv(1024)
                status = response.decode('utf-8', errors='ignore')
                logger.info(f"Printer status: {status}")
                return status

        except Exception as e:
            error_msg = f"상태 조회 실패: {e}"
            logger.error(error_msg)
            return error_msg

    def calibrate(self) -> bool:
        """
        Send calibration command to printer.

        Returns:
            True if successful
        """
        calibrate_zpl = "^XA~JC^XZ"  # Calibrate media
        return self.send_zpl(calibrate_zpl)

    def reset(self) -> bool:
        """
        Reset printer (soft reset).

        Returns:
            True if successful
        """
        reset_zpl = "^XA~JR^XZ"  # Reset printer
        return self.send_zpl(reset_zpl)

    @property
    def is_configured(self) -> bool:
        """Check if printer IP is configured."""
        return bool(self.ip_address)

    @property
    def is_connected(self) -> bool:
        """Check if last operation was successful."""
        return self._is_connected


class ZPLBuilder:
    """
    Helper class to build ZPL commands programmatically.

    Example:
        builder = ZPLBuilder()
        builder.start()
        builder.add_text("Serial Number", x=50, y=50, font_size=30)
        builder.add_barcode_code128("KR01PSA2511001", x=50, y=100, height=80)
        builder.end()
        zpl = builder.get_zpl()
    """

    def __init__(self):
        self.commands = []

    def start(self):
        """Start ZPL format."""
        self.commands.append("^XA")
        return self

    def end(self):
        """End ZPL format."""
        self.commands.append("^XZ")
        return self

    def add_text(
        self,
        text: str,
        x: int,
        y: int,
        font: str = "0",
        orientation: str = "N",
        font_height: int = 30,
        font_width: int = 30
    ):
        """
        Add text field.

        Args:
            text: Text to print
            x, y: Position in dots
            font: Font identifier (0=default)
            orientation: N=normal, R=90°, I=180°, B=270°
            font_height: Font height in dots
            font_width: Font width in dots
        """
        self.commands.append(f"^FO{x},{y}^A{font}{orientation},{font_height},{font_width}^FD{text}^FS")
        return self

    def add_barcode_code128(
        self,
        data: str,
        x: int,
        y: int,
        height: int = 80,
        print_interpretation: bool = True
    ):
        """
        Add Code128 barcode.

        Args:
            data: Data to encode
            x, y: Position in dots
            height: Barcode height in dots
            print_interpretation: Print human-readable text
        """
        interp = "Y" if print_interpretation else "N"
        self.commands.append(f"^FO{x},{y}^BY2^BCN,{height},{interp},N,N^FD{data}^FS")
        return self

    def add_qr_code(
        self,
        data: str,
        x: int,
        y: int,
        magnification: int = 5
    ):
        """
        Add QR code.

        Args:
            data: Data to encode
            x, y: Position in dots
            magnification: Size multiplier (1-10)
        """
        self.commands.append(f"^FO{x},{y}^BQN,2,{magnification}^FDQA,{data}^FS")
        return self

    def add_box(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        thickness: int = 2
    ):
        """
        Add rectangular box.

        Args:
            x, y: Top-left position
            width, height: Box dimensions in dots
            thickness: Border thickness in dots
        """
        self.commands.append(f"^FO{x},{y}^GB{width},{height},{thickness}^FS")
        return self

    def add_line(
        self,
        x: int,
        y: int,
        length: int,
        thickness: int = 2,
        orientation: str = "H"
    ):
        """
        Add line.

        Args:
            x, y: Start position
            length: Line length in dots
            thickness: Line thickness in dots
            orientation: 'H' for horizontal, 'V' for vertical
        """
        if orientation.upper() == 'H':
            self.commands.append(f"^FO{x},{y}^GB{length},{thickness},^FS")
        else:  # Vertical
            self.commands.append(f"^FO{x},{y}^GB{thickness},{length},^FS")
        return self

    def add_raw(self, command: str):
        """
        Add raw ZPL command.

        Args:
            command: Raw ZPL command string
        """
        self.commands.append(command)
        return self

    def clear(self):
        """Clear all commands."""
        self.commands = []
        return self

    def get_zpl(self) -> str:
        """
        Get complete ZPL command string.

        Returns:
            ZPL command string
        """
        return "\n".join(self.commands)

    def __str__(self):
        return self.get_zpl()
