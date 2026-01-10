"""
Unit tests for ProductionLine schema validation.

Tests the line_code validation rules including:
- Alphanumeric characters only
- Uppercase conversion
- Rejection of hyphens, underscores, spaces, and special characters
"""

import pytest
from pydantic import ValidationError

from app.schemas.production_line import ProductionLineCreate, ProductionLineUpdate


class TestProductionLineCreateValidation:
    """Test ProductionLineCreate schema validation"""

    def test_valid_line_code_alphanumeric(self):
        """Valid line_code with alphanumeric characters"""
        obj = ProductionLineCreate(
            line_code="LINEA",
            line_name="Test Line A"
        )
        assert obj.line_code == "LINEA"
        assert obj.line_name == "Test Line A"

    def test_valid_line_code_with_numbers(self):
        """Valid line_code with numbers"""
        obj = ProductionLineCreate(
            line_code="LINE01",
            line_name="Test Line"
        )
        assert obj.line_code == "LINE01"

    def test_valid_line_code_numbers_only(self):
        """Valid line_code with numbers only"""
        obj = ProductionLineCreate(
            line_code="12345",
            line_name="Test Line"
        )
        assert obj.line_code == "12345"

    def test_valid_line_code_kr_format(self):
        """Valid line_code in KR format"""
        obj = ProductionLineCreate(
            line_code="KR001",
            line_name="Test Line"
        )
        assert obj.line_code == "KR001"

    def test_uppercase_conversion(self):
        """Lowercase line_code automatically converted to uppercase"""
        obj = ProductionLineCreate(
            line_code="linea01",
            line_name="Test Line"
        )
        assert obj.line_code == "LINEA01"

    def test_uppercase_conversion_mixed_case(self):
        """Mixed case line_code converted to uppercase"""
        obj = ProductionLineCreate(
            line_code="LiNeTeSt01",
            line_name="Test Line"
        )
        assert obj.line_code == "LINETEST01"

    def test_invalid_line_code_with_hyphen(self):
        """line_code with hyphen should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE-A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters" in error_msg

    def test_invalid_line_code_with_underscore(self):
        """line_code with underscore should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE_A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters" in error_msg

    def test_invalid_line_code_with_space(self):
        """line_code with space should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters" in error_msg

    def test_invalid_line_code_with_at_sign(self):
        """line_code with @ should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE@A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters" in error_msg

    def test_invalid_line_code_empty_string(self):
        """Empty line_code should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "line_code cannot be empty" in error_msg

    def test_required_fields(self):
        """line_code and line_name are required"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "line_code" in error_msg

    def test_optional_fields(self):
        """Optional fields can be omitted"""
        obj = ProductionLineCreate(
            line_code="LINEA",
            line_name="Test Line"
        )
        assert obj.description is None
        assert obj.cycle_time_sec is None
        assert obj.location is None
        assert obj.is_active is True


class TestProductionLineUpdateValidation:
    """Test ProductionLineUpdate schema validation"""

    def test_update_valid_line_code_alphanumeric(self):
        """Update schema accepts alphanumeric"""
        obj = ProductionLineUpdate(line_code="NEWLINE01")
        assert obj.line_code == "NEWLINE01"

    def test_update_uppercase_conversion(self):
        """Update schema converts to uppercase"""
        obj = ProductionLineUpdate(line_code="newline")
        assert obj.line_code == "NEWLINE"

    def test_update_invalid_line_code_with_underscore(self):
        """Update schema rejects underscore"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineUpdate(line_code="NEW_LINE")
        error_msg = str(exc_info.value)
        assert "alphanumeric characters" in error_msg

    def test_update_all_fields_optional(self):
        """All fields are optional in update schema"""
        obj = ProductionLineUpdate()
        assert obj.line_code is None
        assert obj.line_name is None

    def test_update_empty_string_rejected(self):
        """Empty string for line_code should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineUpdate(line_code="")
        error_msg = str(exc_info.value)
        assert "line_code cannot be empty" in error_msg


class TestProductionLineEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_line_code_single_character(self):
        """Single character line_code should be valid"""
        obj = ProductionLineCreate(
            line_code="A",
            line_name="Test"
        )
        assert obj.line_code == "A"

    def test_line_code_max_length(self):
        """line_code at max length (50) should be valid"""
        long_code = "A" * 50
        obj = ProductionLineCreate(
            line_code=long_code,
            line_name="Test"
        )
        assert obj.line_code == long_code
        assert len(obj.line_code) == 50

    def test_is_active_default_true(self):
        """is_active defaults to True"""
        obj = ProductionLineCreate(
            line_code="LINEA",
            line_name="Test"
        )
        assert obj.is_active is True
