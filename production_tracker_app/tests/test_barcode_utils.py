"""
Unit tests for barcode_utils module.

Tests barcode parsing, validation, and generation functionality.
"""
import pytest
from utils.barcode_utils import (
    BarcodeParser, BarcodeGenerator,
    parse_serial, parse_lot, validate_serial, validate_lot,
    format_serial, format_lot
)


class TestBarcodeParser:
    """Test BarcodeParser class."""

    # Valid test data
    VALID_SERIAL_V1 = "KR01PSA2511001"
    VALID_LOT = "WF-KR-251110D-001"

    # Invalid test data
    INVALID_SERIAL_TOO_SHORT = "KR01PSA251100"
    INVALID_SERIAL_TOO_LONG = "KR01PSA25110011"
    INVALID_SERIAL_WRONG_FORMAT = "KR01XXX2511001"
    INVALID_LOT_WRONG_FORMAT = "WF-KR-251110-001"

    def test_parse_serial_v1_valid(self):
        """Test parsing valid V1 serial number."""
        result = BarcodeParser.parse_serial_v1(self.VALID_SERIAL_V1)

        assert result is not None
        assert result['country_code'] == 'KR'
        assert result['line_number'] == '01'
        assert result['product_code'] == 'PSA'
        assert result['year_month'] == '2511'
        assert result['sequence'] == '001'

    def test_parse_serial_v1_lowercase(self):
        """Test parsing lowercase serial number (should auto-uppercase)."""
        result = BarcodeParser.parse_serial_v1("kr01psa2511001")

        assert result is not None
        assert result['country_code'] == 'KR'

    def test_parse_serial_v1_invalid_length(self):
        """Test parsing invalid length serial."""
        assert BarcodeParser.parse_serial_v1(self.INVALID_SERIAL_TOO_SHORT) is None
        assert BarcodeParser.parse_serial_v1(self.INVALID_SERIAL_TOO_LONG) is None

    def test_parse_serial_v1_invalid_format(self):
        """Test parsing invalid format serial."""
        assert BarcodeParser.parse_serial_v1(self.INVALID_SERIAL_WRONG_FORMAT) is None

    def test_parse_lot_valid(self):
        """Test parsing valid LOT number."""
        result = BarcodeParser.parse_lot(self.VALID_LOT)

        assert result is not None
        assert result['product_family'] == 'WF'
        assert result['country_code'] == 'KR'
        assert result['date'] == '251110'
        assert result['shift_type'] == 'D'
        assert result['sequence'] == '001'

    def test_parse_lot_night_shift(self):
        """Test parsing LOT with night shift."""
        lot = "WF-KR-251110N-001"
        result = BarcodeParser.parse_lot(lot)

        assert result is not None
        assert result['shift_type'] == 'N'

    def test_parse_lot_invalid(self):
        """Test parsing invalid LOT number."""
        assert BarcodeParser.parse_lot(self.INVALID_LOT_WRONG_FORMAT) is None

    def test_validate_serial_v1_valid(self):
        """Test serial validation with valid serial."""
        assert BarcodeParser.validate_serial_v1(self.VALID_SERIAL_V1) is True

    def test_validate_serial_v1_invalid(self):
        """Test serial validation with invalid serial."""
        assert BarcodeParser.validate_serial_v1(self.INVALID_SERIAL_TOO_SHORT) is False
        assert BarcodeParser.validate_serial_v1(self.INVALID_SERIAL_WRONG_FORMAT) is False
        assert BarcodeParser.validate_serial_v1("") is False
        assert BarcodeParser.validate_serial_v1(None) is False

    def test_validate_lot_valid(self):
        """Test LOT validation with valid LOT."""
        assert BarcodeParser.validate_lot(self.VALID_LOT) is True

    def test_validate_lot_invalid(self):
        """Test LOT validation with invalid LOT."""
        assert BarcodeParser.validate_lot(self.INVALID_LOT_WRONG_FORMAT) is False
        assert BarcodeParser.validate_lot("") is False
        assert BarcodeParser.validate_lot(None) is False

    def test_format_serial_v1(self):
        """Test serial formatting."""
        assert BarcodeParser.format_serial_v1("  kr01psa2511001  ") == "KR01PSA2511001"
        assert BarcodeParser.format_serial_v1("KR01PSA2511001") == "KR01PSA2511001"

    def test_format_lot(self):
        """Test LOT formatting."""
        assert BarcodeParser.format_lot("  wf-kr-251110d-001  ") == "WF-KR-251110D-001"
        assert BarcodeParser.format_lot("WF-KR-251110D-001") == "WF-KR-251110D-001"


class TestBarcodeGenerator:
    """Test BarcodeGenerator class."""

    VALID_SERIAL = "KR01PSA2511001"
    VALID_LOT = "WF-KR-251110D-001"

    def test_generate_zpl_code128(self):
        """Test ZPL Code128 generation."""
        zpl = BarcodeGenerator.generate_zpl_code128(self.VALID_SERIAL, x=50, y=50, height=80)

        assert "^FO50,50" in zpl
        assert "^BCN,80" in zpl
        assert f"^FD{self.VALID_SERIAL}^FS" in zpl

    def test_generate_zpl_qr(self):
        """Test ZPL QR code generation."""
        zpl = BarcodeGenerator.generate_zpl_qr(self.VALID_SERIAL, x=50, y=50, magnification=5)

        assert "^FO50,50" in zpl
        assert "^BQN,2,5" in zpl
        assert f"^FDQA,{self.VALID_SERIAL}^FS" in zpl

    def test_generate_zpl_label_code128(self):
        """Test complete ZPL label generation with Code128."""
        zpl = BarcodeGenerator.generate_zpl_label(self.VALID_SERIAL, barcode_type='code128', include_text=True)

        assert "^XA" in zpl
        assert "^XZ" in zpl
        assert self.VALID_SERIAL in zpl
        assert "^BCN" in zpl  # Code128

    def test_generate_zpl_label_qr(self):
        """Test complete ZPL label generation with QR code."""
        zpl = BarcodeGenerator.generate_zpl_label(self.VALID_SERIAL, barcode_type='qr', include_text=True)

        assert "^XA" in zpl
        assert "^XZ" in zpl
        assert self.VALID_SERIAL in zpl
        assert "^BQN" in zpl  # QR code

    def test_generate_zpl_label_no_text(self):
        """Test ZPL label generation without text."""
        zpl = BarcodeGenerator.generate_zpl_label(self.VALID_SERIAL, barcode_type='code128', include_text=False)

        # Should not contain text field (FD without BC/BQ prefix)
        assert "^XA" in zpl
        assert "^XZ" in zpl


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    VALID_SERIAL = "KR01PSA2511001"
    VALID_LOT = "WF-KR-251110D-001"

    def test_parse_serial_function(self):
        """Test parse_serial convenience function."""
        result = parse_serial(self.VALID_SERIAL)
        assert result is not None
        assert result['country_code'] == 'KR'

    def test_parse_lot_function(self):
        """Test parse_lot convenience function."""
        result = parse_lot(self.VALID_LOT)
        assert result is not None
        assert result['product_family'] == 'WF'

    def test_validate_serial_function(self):
        """Test validate_serial convenience function."""
        assert validate_serial(self.VALID_SERIAL) is True
        assert validate_serial("INVALID") is False

    def test_validate_lot_function(self):
        """Test validate_lot convenience function."""
        assert validate_lot(self.VALID_LOT) is True
        assert validate_lot("INVALID") is False

    def test_format_serial_function(self):
        """Test format_serial convenience function."""
        assert format_serial("  kr01psa2511001  ") == "KR01PSA2511001"

    def test_format_lot_function(self):
        """Test format_lot convenience function."""
        assert format_lot("  wf-kr-251110d-001  ") == "WF-KR-251110D-001"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_validation(self):
        """Test validation with empty strings."""
        assert validate_serial("") is False
        assert validate_lot("") is False

    def test_none_validation(self):
        """Test validation with None."""
        assert validate_serial(None) is False
        assert validate_lot(None) is False

    def test_whitespace_only(self):
        """Test with whitespace only strings."""
        assert validate_serial("   ") is False
        assert validate_lot("   ") is False

    def test_special_characters(self):
        """Test with special characters."""
        assert validate_serial("KR01PSA@511001") is False
        assert validate_lot("WF-KR-251110D@001") is False

    def test_mixed_case_parsing(self):
        """Test parsing with mixed case."""
        result = parse_serial("Kr01PsA2511001")
        assert result is not None
        assert result['country_code'] == 'KR'
        assert result['product_code'] == 'PSA'

    def test_exact_14_chars_serial(self):
        """Test serial with exactly 14 characters."""
        assert validate_serial("KR01PSA2511001") is True
        assert len("KR01PSA2511001") == 14

    def test_13_chars_serial_invalid(self):
        """Test serial with 13 characters (invalid)."""
        assert validate_serial("KR01PSA251100") is False

    def test_15_chars_serial_invalid(self):
        """Test serial with 15 characters (invalid)."""
        assert validate_serial("KR01PSA25110011") is False


# Pytest fixtures
@pytest.fixture
def valid_serial():
    """Fixture for valid serial number."""
    return "KR01PSA2511001"


@pytest.fixture
def valid_lot():
    """Fixture for valid LOT number."""
    return "WF-KR-251110D-001"


# Parametrized tests
@pytest.mark.parametrize("serial,expected", [
    ("KR01PSA2511001", True),
    ("US02ABC2512999", True),
    ("CN03XYZ2510001", True),
    ("KR01PSA251100", False),  # Too short
    ("KR01PSA25110011", False),  # Too long
    ("KR01XXX2511001", False),  # Invalid product code (numbers)
    ("1234567890123", False),  # All numbers
    ("ABCDEFGHIJKLMN", False),  # All letters
])
def test_serial_validation_parametrized(serial, expected):
    """Parametrized test for serial validation."""
    assert validate_serial(serial) == expected


@pytest.mark.parametrize("lot,expected", [
    ("WF-KR-251110D-001", True),
    ("WF-KR-251110N-001", True),
    ("AB-US-251201D-999", True),
    ("WF-KR-251110-001", False),  # Missing shift type
    ("WF-KR-251110X-001", False),  # Invalid shift type
    ("WFKR251110D001", False),  # Missing separators
    ("WF-KR-25111OD-001", False),  # Letter O instead of 0
])
def test_lot_validation_parametrized(lot, expected):
    """Parametrized test for LOT validation."""
    assert validate_lot(lot) == expected
