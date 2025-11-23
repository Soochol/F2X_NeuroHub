"""
Tests for Serial Number Validation and Formatting Utilities.
"""
import pytest
from datetime import datetime

from utils.serial_validator import (
    validate_serial_number_v1,
    validate_serial_number_v0,
    validate_serial_number,
    detect_serial_version,
    parse_serial_number_v1,
    parse_serial_number_v0,
    format_serial_number_v1,
    format_serial_number,
    parse_production_month,
    get_serial_info,
)


class TestSerialV1Validation:
    """Test V1 serial number validation (14 chars)."""

    def test_validate_v1_format_valid(self):
        """Test valid V1 serial numbers."""
        assert validate_serial_number_v1("KR01PSA2511001") == True
        assert validate_serial_number_v1("US02ABC2512999") == True
        assert validate_serial_number_v1("CN03XYZ2601123") == True

    def test_validate_v1_format_invalid(self):
        """Test invalid V1 serial numbers."""
        assert validate_serial_number_v1("INVALID") == False
        assert validate_serial_number_v1("KR01PSA251100") == False  # Too short (13 chars)
        assert validate_serial_number_v1("KR01PSA25110001") == False  # Too long (15 chars)
        assert validate_serial_number_v1("kr01psa2511001") == False  # Lowercase
        assert validate_serial_number_v1("KR-01-PSA-2511-001") == False  # With hyphens
        assert validate_serial_number_v1("") == False
        assert validate_serial_number_v1(None) == False

    def test_validate_v1_format_boundary(self):
        """Test boundary cases for V1 validation."""
        # Invalid structure
        assert validate_serial_number_v1("1234567890ABCD") == False  # Wrong format
        assert validate_serial_number_v1("KRABCDEF123456") == False  # Wrong pattern


class TestSerialV0Validation:
    """Test V0 serial number validation (legacy with hyphens)."""

    def test_validate_v0_format_valid(self):
        """Test valid V0 serial numbers."""
        assert validate_serial_number_v0("WF-KR-251119D-003-0038") == True
        assert validate_serial_number_v0("AB-US-251220N-999-9999") == True

    def test_validate_v0_format_invalid(self):
        """Test invalid V0 serial numbers."""
        assert validate_serial_number_v0("INVALID") == False
        assert validate_serial_number_v0("KR01PSA2511001") == False  # V1 format
        assert validate_serial_number_v0("") == False
        assert validate_serial_number_v0(None) == False


class TestSerialVersionDetection:
    """Test serial version auto-detection."""

    def test_detect_version_v1(self):
        """Test detecting V1 format."""
        assert detect_serial_version("KR01PSA2511001") == 1
        assert detect_serial_version("US02ABC2512999") == 1

    def test_detect_version_v0(self):
        """Test detecting V0 format."""
        assert detect_serial_version("WF-KR-251119D-003-0038") == 0
        assert detect_serial_version("AB-US-251220N-999-9999") == 0

    def test_detect_version_invalid(self):
        """Test detecting invalid format."""
        assert detect_serial_version("INVALID") is None
        assert detect_serial_version("") is None


class TestSerialV1Parsing:
    """Test V1 serial number parsing."""

    def test_parse_v1_components(self):
        """Test parsing V1 serial into components."""
        result = parse_serial_number_v1("KR01PSA2511001")
        assert result.country_code == "KR"
        assert result.line_number == "01"
        assert result.model_code == "PSA"
        assert result.production_month == "2511"
        assert result.sequence == "001"

    def test_parse_v1_invalid(self):
        """Test parsing invalid V1 serial raises error."""
        with pytest.raises(ValueError, match="Invalid V1 serial number format"):
            parse_serial_number_v1("INVALID")

        with pytest.raises(ValueError, match="Invalid V1 serial number format"):
            parse_serial_number_v1("WF-KR-251119D-003-0038")  # V0 format


class TestSerialV0Parsing:
    """Test V0 serial number parsing."""

    def test_parse_v0_components(self):
        """Test parsing V0 serial into components."""
        result = parse_serial_number_v0("WF-KR-251119D-003-0038")
        assert result.model_code == "WF"
        assert result.country_code == "KR"
        assert result.production_date == "251119"
        assert result.shift == "D"
        assert result.lot_sequence == "003"
        assert result.serial_sequence == "0038"

    def test_parse_v0_invalid(self):
        """Test parsing invalid V0 serial raises error."""
        with pytest.raises(ValueError, match="Invalid V0 serial number format"):
            parse_serial_number_v0("KR01PSA2511001")  # V1 format


class TestSerialFormatting:
    """Test serial number formatting."""

    def test_format_v1_with_hyphens(self):
        """Test formatting V1 serial with hyphens."""
        assert format_serial_number_v1("KR01PSA2511001") == "KR01-PSA-2511-001"
        assert format_serial_number_v1("US02ABC2512999") == "US02-ABC-2512-999"

    def test_format_v1_with_custom_separator(self):
        """Test formatting V1 serial with custom separator."""
        assert format_serial_number_v1("KR01PSA2511001", " ") == "KR01 PSA 2511 001"
        assert format_serial_number_v1("KR01PSA2511001", "_") == "KR01_PSA_2511_001"

    def test_format_v1_invalid_returns_original(self):
        """Test formatting invalid V1 serial returns original."""
        assert format_serial_number_v1("INVALID") == "INVALID"
        assert format_serial_number_v1("WF-KR-251119D-003-0038") == "WF-KR-251119D-003-0038"

    def test_format_auto_detect(self):
        """Test auto-detect formatting."""
        assert format_serial_number("KR01PSA2511001") == "KR01-PSA-2511-001"
        assert format_serial_number("WF-KR-251119D-003-0038") == "WF-KR-251119D-003-0038"
        assert format_serial_number("INVALID") == "INVALID"


class TestProductionMonthParsing:
    """Test production month parsing."""

    def test_parse_production_month_valid(self):
        """Test parsing valid production month."""
        result = parse_production_month("2511")
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 1

        result = parse_production_month("2601")
        assert result.year == 2026
        assert result.month == 1

    def test_parse_production_month_invalid_format(self):
        """Test parsing invalid month format."""
        with pytest.raises(ValueError, match="Invalid month format"):
            parse_production_month("251")  # Too short

        with pytest.raises(ValueError, match="Invalid month format"):
            parse_production_month("25111")  # Too long

    def test_parse_production_month_invalid_month(self):
        """Test parsing invalid month value."""
        with pytest.raises(ValueError, match="Invalid month value"):
            parse_production_month("2513")  # Month 13

        with pytest.raises(ValueError, match="Invalid month value"):
            parse_production_month("2500")  # Month 00


class TestSerialInfo:
    """Test get_serial_info comprehensive function."""

    def test_get_serial_info_v1(self):
        """Test getting info for V1 serial."""
        info = get_serial_info("KR01PSA2511001")
        assert info['valid'] == True
        assert info['version'] == 1
        assert info['serial'] == "KR01PSA2511001"
        assert info['formatted'] == "KR01-PSA-2511-001"
        assert 'components' in info
        assert info['components'].country_code == "KR"
        assert 'production_date' in info

    def test_get_serial_info_v0(self):
        """Test getting info for V0 serial."""
        info = get_serial_info("WF-KR-251119D-003-0038")
        assert info['valid'] == True
        assert info['version'] == 0
        assert info['serial'] == "WF-KR-251119D-003-0038"
        assert info['formatted'] == "WF-KR-251119D-003-0038"  # V0 already formatted
        assert 'components' in info
        assert info['components'].model_code == "WF"

    def test_get_serial_info_invalid(self):
        """Test getting info for invalid serial."""
        info = get_serial_info("INVALID")
        assert info['valid'] == False
        assert info['version'] is None
        assert info['serial'] == "INVALID"
        assert 'error' in info


class TestSerialValidation:
    """Test generic serial validation (any version)."""

    def test_validate_any_version(self):
        """Test validating any serial version."""
        # V1 valid
        assert validate_serial_number("KR01PSA2511001") == True

        # V0 valid
        assert validate_serial_number("WF-KR-251119D-003-0038") == True

        # Invalid
        assert validate_serial_number("INVALID") == False
        assert validate_serial_number("") == False


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_strings(self):
        """Test handling empty strings."""
        assert validate_serial_number_v1("") == False
        assert validate_serial_number_v0("") == False
        assert validate_serial_number("") == False

    def test_none_values(self):
        """Test handling None values."""
        assert validate_serial_number_v1(None) == False
        assert validate_serial_number_v0(None) == False

    def test_whitespace_handling(self):
        """Test whitespace is not auto-trimmed."""
        # Validation does not trim whitespace - caller must strip
        assert validate_serial_number_v1(" KR01PSA2511001") == False
        assert validate_serial_number_v1("KR01PSA2511001 ") == False

    def test_case_sensitivity(self):
        """Test case sensitivity."""
        # V1 requires uppercase
        assert validate_serial_number_v1("kr01psa2511001") == False
        assert validate_serial_number_v1("Kr01Psa2511001") == False
        assert validate_serial_number_v1("KR01PSA2511001") == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
