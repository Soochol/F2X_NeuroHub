"""
Unit tests for zebra_printer module.

Tests network printer communication and ZPL command building.
"""
import pytest
import socket
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import QObject, Signal

from utils.zebra_printer import ZebraPrinter, ZPLBuilder


class TestZebraPrinter:
    """Test ZebraPrinter class."""

    def test_init_default(self):
        """Test ZebraPrinter initialization with defaults."""
        printer = ZebraPrinter()

        assert printer.ip_address == ""
        assert printer.port == ZebraPrinter.DEFAULT_PORT
        assert printer.timeout == ZebraPrinter.DEFAULT_TIMEOUT
        assert printer.is_configured is False
        assert printer.is_connected is False

    def test_init_with_params(self):
        """Test ZebraPrinter initialization with parameters."""
        printer = ZebraPrinter(ip_address="192.168.1.100", port=9200)

        assert printer.ip_address == "192.168.1.100"
        assert printer.port == 9200
        assert printer.is_configured is True

    def test_set_printer(self):
        """Test setting printer IP and port."""
        printer = ZebraPrinter()
        printer.set_printer("10.0.0.50", 9100)

        assert printer.ip_address == "10.0.0.50"
        assert printer.port == 9100
        assert printer.is_configured is True
        assert printer.is_connected is False

    def test_is_configured_property(self):
        """Test is_configured property."""
        printer = ZebraPrinter()
        assert printer.is_configured is False

        printer.set_printer("192.168.1.100")
        assert printer.is_configured is True

    @patch('socket.socket')
    def test_test_connection_success(self, mock_socket_class):
        """Test successful connection test."""
        # Setup mock socket
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = b"Status OK"

        printer = ZebraPrinter(ip_address="192.168.1.100", port=9100)

        # Capture signal
        signal_received = []
        printer.status_changed.connect(lambda status: signal_received.append(status))

        success, message = printer.test_connection()

        assert success is True
        assert "연결 성공" in message
        assert printer.is_connected is True
        assert signal_received == [True]

        # Verify socket operations
        mock_socket.settimeout.assert_called_once_with(printer.timeout)
        mock_socket.connect.assert_called_once_with(("192.168.1.100", 9100))
        mock_socket.sendall.assert_called_once_with(b"~HQES\n")

    @patch('socket.socket')
    def test_test_connection_timeout(self, mock_socket_class):
        """Test connection test with timeout."""
        # Setup mock socket to raise timeout
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = socket.timeout()

        printer = ZebraPrinter(ip_address="192.168.1.100")

        # Capture signal
        signal_received = []
        printer.status_changed.connect(lambda status: signal_received.append(status))

        success, message = printer.test_connection()

        assert success is False
        assert "시간 초과" in message
        assert printer.is_connected is False
        assert signal_received == [False]

    @patch('socket.socket')
    def test_test_connection_error(self, mock_socket_class):
        """Test connection test with socket error."""
        # Setup mock socket to raise error
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.connect.side_effect = socket.error("Connection refused")

        printer = ZebraPrinter(ip_address="192.168.1.100")
        success, message = printer.test_connection()

        assert success is False
        assert "연결 실패" in message
        assert printer.is_connected is False

    def test_test_connection_no_ip(self):
        """Test connection test without IP configured."""
        printer = ZebraPrinter()
        success, message = printer.test_connection()

        assert success is False
        assert "설정되지 않았습니다" in message

    @patch('socket.socket')
    def test_send_zpl_success(self, mock_socket_class):
        """Test successful ZPL sending."""
        # Setup mock socket
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        printer = ZebraPrinter(ip_address="192.168.1.100")

        # Capture signals
        success_data = []
        status_data = []
        printer.print_success.connect(lambda data: success_data.append(data))
        printer.status_changed.connect(lambda status: status_data.append(status))

        zpl = "^XA^FO50,50^A0N,40^FDTEST^FS^XZ"
        result = printer.send_zpl(zpl)

        assert result is True
        assert printer.is_connected is True
        assert success_data == [zpl]
        assert status_data == [True]

        # Verify socket operations
        mock_socket.connect.assert_called_once_with(("192.168.1.100", 9100))
        mock_socket.sendall.assert_called_once_with(zpl.encode('utf-8'))

    @patch('socket.socket')
    def test_send_zpl_timeout(self, mock_socket_class):
        """Test ZPL sending with timeout."""
        # Setup mock socket to raise timeout
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.sendall.side_effect = socket.timeout()

        printer = ZebraPrinter(ip_address="192.168.1.100")

        # Capture error signal
        error_msgs = []
        printer.print_error.connect(lambda msg: error_msgs.append(msg))

        result = printer.send_zpl("^XA^XZ")

        assert result is False
        assert len(error_msgs) == 1
        assert "시간 초과" in error_msgs[0]

    @patch('socket.socket')
    def test_send_zpl_error(self, mock_socket_class):
        """Test ZPL sending with socket error."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.sendall.side_effect = socket.error("Network error")

        printer = ZebraPrinter(ip_address="192.168.1.100")

        # Capture error signal
        error_msgs = []
        printer.print_error.connect(lambda msg: error_msgs.append(msg))

        result = printer.send_zpl("^XA^XZ")

        assert result is False
        assert len(error_msgs) == 1
        assert "전송 실패" in error_msgs[0]

    def test_send_zpl_no_ip(self):
        """Test ZPL sending without IP configured."""
        printer = ZebraPrinter()

        # Capture error signal
        error_msgs = []
        printer.print_error.connect(lambda msg: error_msgs.append(msg))

        result = printer.send_zpl("^XA^XZ")

        assert result is False
        assert len(error_msgs) == 1
        assert "설정되지 않았습니다" in error_msgs[0]

    @patch('socket.socket')
    @patch('utils.zebra_printer.BarcodeGenerator')
    def test_print_label_code128(self, mock_barcode_gen, mock_socket_class):
        """Test printing label with Code128 barcode."""
        # Setup mocks
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_barcode_gen.generate_zpl_label.return_value = "^XA^FDTEST^FS^XZ"

        printer = ZebraPrinter(ip_address="192.168.1.100")
        result = printer.print_label("KR01PSA2511001", barcode_type='code128', include_text=True)

        assert result is True
        mock_barcode_gen.generate_zpl_label.assert_called_once_with(
            "KR01PSA2511001",
            barcode_type='code128',
            include_text=True
        )
        mock_socket.sendall.assert_called_once()

    @patch('socket.socket')
    @patch('utils.zebra_printer.BarcodeGenerator')
    def test_print_label_qr(self, mock_barcode_gen, mock_socket_class):
        """Test printing label with QR code."""
        # Setup mocks
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_barcode_gen.generate_zpl_label.return_value = "^XA^BQTEST^XZ"

        printer = ZebraPrinter(ip_address="192.168.1.100")
        result = printer.print_label("WF-KR-251110D-001", barcode_type='qr', include_text=False)

        assert result is True
        mock_barcode_gen.generate_zpl_label.assert_called_once_with(
            "WF-KR-251110D-001",
            barcode_type='qr',
            include_text=False
        )

    @patch('socket.socket')
    def test_print_custom_zpl_success(self, mock_socket_class):
        """Test printing custom ZPL template."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        printer = ZebraPrinter(ip_address="192.168.1.100")
        template = "^XA^FO50,50^A0N,40^FD{SERIAL}^FS^XZ"

        result = printer.print_custom_zpl(template, SERIAL="KR01PSA2511001")

        assert result is True
        sent_data = mock_socket.sendall.call_args[0][0].decode('utf-8')
        assert "KR01PSA2511001" in sent_data

    @patch('socket.socket')
    def test_print_custom_zpl_missing_variable(self, mock_socket_class):
        """Test custom ZPL with missing template variable."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        printer = ZebraPrinter(ip_address="192.168.1.100")

        # Capture error signal
        error_msgs = []
        printer.print_error.connect(lambda msg: error_msgs.append(msg))

        template = "^XA^FO50,50^FD{SERIAL}^FS^FD{LOT}^FS^XZ"
        result = printer.print_custom_zpl(template, SERIAL="KR01PSA2511001")  # Missing LOT

        assert result is False
        assert len(error_msgs) == 1
        assert "변수 누락" in error_msgs[0]

    @patch('socket.socket')
    def test_get_printer_status_success(self, mock_socket_class):
        """Test getting printer status."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.return_value = b"STATUS:READY"

        printer = ZebraPrinter(ip_address="192.168.1.100")
        status = printer.get_printer_status()

        assert "READY" in status
        mock_socket.sendall.assert_called_once_with(b"~HS\n")

    @patch('socket.socket')
    def test_get_printer_status_error(self, mock_socket_class):
        """Test getting printer status with error."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket
        mock_socket.recv.side_effect = socket.error("Connection lost")

        printer = ZebraPrinter(ip_address="192.168.1.100")
        status = printer.get_printer_status()

        assert "실패" in status

    def test_get_printer_status_no_ip(self):
        """Test getting status without IP configured."""
        printer = ZebraPrinter()
        status = printer.get_printer_status()

        assert "미설정" in status

    @patch('socket.socket')
    def test_calibrate(self, mock_socket_class):
        """Test printer calibration."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        printer = ZebraPrinter(ip_address="192.168.1.100")
        result = printer.calibrate()

        assert result is True
        sent_data = mock_socket.sendall.call_args[0][0].decode('utf-8')
        assert "~JC" in sent_data

    @patch('socket.socket')
    def test_reset(self, mock_socket_class):
        """Test printer reset."""
        mock_socket = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        printer = ZebraPrinter(ip_address="192.168.1.100")
        result = printer.reset()

        assert result is True
        sent_data = mock_socket.sendall.call_args[0][0].decode('utf-8')
        assert "~JR" in sent_data


class TestZPLBuilder:
    """Test ZPLBuilder class."""

    def test_init(self):
        """Test ZPLBuilder initialization."""
        builder = ZPLBuilder()
        assert builder.commands == []

    def test_start_end(self):
        """Test start and end commands."""
        builder = ZPLBuilder()
        builder.start().end()

        zpl = builder.get_zpl()
        assert "^XA" in zpl
        assert "^XZ" in zpl

    def test_add_text(self):
        """Test adding text field."""
        builder = ZPLBuilder()
        builder.start()
        builder.add_text("Serial Number", x=50, y=50, font_height=40)
        builder.end()

        zpl = builder.get_zpl()
        assert "^FO50,50" in zpl
        assert "^A0N,40" in zpl
        assert "^FDSerial Number^FS" in zpl

    def test_add_text_with_orientation(self):
        """Test adding text with rotation."""
        builder = ZPLBuilder()
        builder.add_text("Rotated", x=100, y=100, orientation="R", font_height=30)

        zpl = builder.get_zpl()
        assert "^FO100,100" in zpl
        assert "^A0R,30" in zpl
        assert "^FDRotated^FS" in zpl

    def test_add_barcode_code128(self):
        """Test adding Code128 barcode."""
        builder = ZPLBuilder()
        builder.start()
        builder.add_barcode_code128("KR01PSA2511001", x=50, y=100, height=80)
        builder.end()

        zpl = builder.get_zpl()
        assert "^FO50,100" in zpl
        assert "^BCN,80" in zpl
        assert "^FDKR01PSA2511001^FS" in zpl

    def test_add_barcode_code128_no_interpretation(self):
        """Test Code128 without human-readable text."""
        builder = ZPLBuilder()
        builder.add_barcode_code128("TEST123", x=50, y=100, print_interpretation=False)

        zpl = builder.get_zpl()
        assert "^BCN,80,N,N,N" in zpl

    def test_add_qr_code(self):
        """Test adding QR code."""
        builder = ZPLBuilder()
        builder.start()
        builder.add_qr_code("WF-KR-251110D-001", x=50, y=50, magnification=5)
        builder.end()

        zpl = builder.get_zpl()
        assert "^FO50,50" in zpl
        assert "^BQN,2,5" in zpl
        assert "^FDQA,WF-KR-251110D-001^FS" in zpl

    def test_add_box(self):
        """Test adding box."""
        builder = ZPLBuilder()
        builder.add_box(x=10, y=10, width=200, height=100, thickness=3)

        zpl = builder.get_zpl()
        assert "^FO10,10" in zpl
        assert "^GB200,100,3^FS" in zpl

    def test_add_line_horizontal(self):
        """Test adding horizontal line."""
        builder = ZPLBuilder()
        builder.add_line(x=50, y=100, length=300, thickness=2, orientation='H')

        zpl = builder.get_zpl()
        assert "^FO50,100" in zpl
        assert "^GB300,2,^FS" in zpl

    def test_add_line_vertical(self):
        """Test adding vertical line."""
        builder = ZPLBuilder()
        builder.add_line(x=50, y=100, length=300, thickness=2, orientation='V')

        zpl = builder.get_zpl()
        assert "^FO50,100" in zpl
        assert "^GB2,300,^FS" in zpl

    def test_add_raw(self):
        """Test adding raw ZPL command."""
        builder = ZPLBuilder()
        builder.add_raw("^FWN")  # Field orientation
        builder.add_raw("^CFD,30")  # Change default font

        zpl = builder.get_zpl()
        assert "^FWN" in zpl
        assert "^CFD,30" in zpl

    def test_clear(self):
        """Test clearing commands."""
        builder = ZPLBuilder()
        builder.start()
        builder.add_text("Test", 50, 50)
        builder.clear()

        assert builder.commands == []
        assert builder.get_zpl() == ""

    def test_method_chaining(self):
        """Test method chaining."""
        builder = ZPLBuilder()
        result = builder.start().add_text("Title", 50, 50).add_barcode_code128("12345", 50, 100).end()

        assert result is builder
        zpl = builder.get_zpl()
        assert "^XA" in zpl
        assert "Title" in zpl
        assert "12345" in zpl
        assert "^XZ" in zpl

    def test_str_method(self):
        """Test string representation."""
        builder = ZPLBuilder()
        builder.start().add_text("Test", 50, 50).end()

        assert str(builder) == builder.get_zpl()

    def test_complete_label_example(self):
        """Test building a complete label."""
        builder = ZPLBuilder()
        builder.start()
        builder.add_text("Serial Number:", x=50, y=30, font_height=25)
        builder.add_barcode_code128("KR01PSA2511001", x=50, y=70, height=80)
        builder.add_box(x=10, y=10, width=400, height=200, thickness=2)
        builder.end()

        zpl = builder.get_zpl()

        # Verify all elements present
        assert "^XA" in zpl
        assert "Serial Number:" in zpl
        assert "KR01PSA2511001" in zpl
        assert "^BCN" in zpl
        assert "^GB400,200,2^FS" in zpl
        assert "^XZ" in zpl


class TestZPLBuilderAdvanced:
    """Test advanced ZPLBuilder scenarios."""

    def test_multi_line_label(self):
        """Test building multi-line label."""
        builder = ZPLBuilder()
        builder.start()
        builder.add_text("LOT: WF-KR-251110D-001", x=50, y=30)
        builder.add_text("Serial: KR01PSA2511001", x=50, y=70)
        builder.add_text("Date: 2025-11-21", x=50, y=110)
        builder.add_qr_code("KR01PSA2511001", x=300, y=30)
        builder.end()

        zpl = builder.get_zpl()
        lines = zpl.split('\n')

        # Should have 5 commands: start, 3 texts, qr, end
        assert len(lines) >= 5
        assert lines[0] == "^XA"
        assert lines[-1] == "^XZ"

    def test_empty_builder(self):
        """Test getting ZPL from empty builder."""
        builder = ZPLBuilder()
        zpl = builder.get_zpl()

        assert zpl == ""

    def test_builder_reuse(self):
        """Test reusing builder after clear."""
        builder = ZPLBuilder()

        # First label
        builder.start().add_text("First", 50, 50).end()
        first_zpl = builder.get_zpl()
        assert "First" in first_zpl

        # Clear and create second label
        builder.clear()
        builder.start().add_text("Second", 50, 50).end()
        second_zpl = builder.get_zpl()

        assert "Second" in second_zpl
        assert "First" not in second_zpl


# Parametrized tests
@pytest.mark.parametrize("ip,port,expected_configured", [
    ("192.168.1.100", 9100, True),
    ("10.0.0.1", 9200, True),
    ("", 9100, False),
    (None, 9100, False),
])
def test_printer_configuration_parametrized(ip, port, expected_configured):
    """Parametrized test for printer configuration."""
    if ip is None:
        printer = ZebraPrinter()
    else:
        printer = ZebraPrinter(ip_address=ip, port=port)

    assert printer.is_configured == expected_configured


@pytest.mark.parametrize("orientation,expected", [
    ("N", "^A0N"),
    ("R", "^A0R"),
    ("I", "^A0I"),
    ("B", "^A0B"),
])
def test_text_orientation_parametrized(orientation, expected):
    """Parametrized test for text orientation."""
    builder = ZPLBuilder()
    builder.add_text("Test", x=50, y=50, orientation=orientation)

    zpl = builder.get_zpl()
    assert expected in zpl


# Fixtures
@pytest.fixture
def printer():
    """Fixture for configured ZebraPrinter."""
    return ZebraPrinter(ip_address="192.168.1.100", port=9100)


@pytest.fixture
def builder():
    """Fixture for ZPLBuilder."""
    return ZPLBuilder()


@pytest.fixture
def mock_socket():
    """Fixture for mocked socket."""
    with patch('socket.socket') as mock:
        mock_instance = MagicMock()
        mock.return_value.__enter__.return_value = mock_instance
        yield mock_instance


# Integration-style tests using fixtures
def test_complete_print_workflow(printer, mock_socket):
    """Test complete print workflow using fixtures."""
    # Configure printer
    assert printer.is_configured is True

    # Build ZPL
    builder = ZPLBuilder()
    builder.start()
    builder.add_text("Serial:", 50, 30)
    builder.add_barcode_code128("KR01PSA2511001", 50, 70)
    builder.end()

    zpl = builder.get_zpl()

    # Send to printer
    result = printer.send_zpl(zpl)

    assert result is True
    mock_socket.sendall.assert_called_once()


def test_builder_produces_valid_zpl(builder):
    """Test that builder produces valid ZPL structure."""
    builder.start()
    builder.add_text("Test Label", 50, 50)
    builder.add_barcode_code128("12345", 50, 100)
    builder.end()

    zpl = builder.get_zpl()

    # Valid ZPL must start with ^XA and end with ^XZ
    lines = [line.strip() for line in zpl.split('\n') if line.strip()]
    assert lines[0] == "^XA"
    assert lines[-1] == "^XZ"

    # Must have field commands
    assert any("^FO" in line for line in lines)
    assert any("^FD" in line for line in lines)
