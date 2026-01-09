"""
Unit tests for ProductionLine schema validation.

Tests the line_code validation rules including:
- Alphanumeric characters
- Hyphens and underscores
- Uppercase conversion
- Rejection of spaces and special characters
"""

import pytest
from pydantic import ValidationError

from app.schemas.production_line import ProductionLineCreate, ProductionLineUpdate


class TestProductionLineCreateValidation:
    """Test ProductionLineCreate schema validation"""

    def test_valid_line_code_with_hyphen(self):
        """Valid line_code with hyphen"""
        obj = ProductionLineCreate(
            line_code="LINE-A",
            line_name="Test Line A"
        )
        assert obj.line_code == "LINE-A"
        assert obj.line_name == "Test Line A"

    def test_valid_line_code_with_underscore(self):
        """Valid line_code with underscore"""
        obj = ProductionLineCreate(
            line_code="LINE_A",
            line_name="Test Line A"
        )
        assert obj.line_code == "LINE_A"

    def test_valid_line_code_with_both_hyphen_and_underscore(self):
        """Valid line_code with both hyphen and underscore"""
        obj = ProductionLineCreate(
            line_code="TEST-LINE_A1",
            line_name="Test Line"
        )
        assert obj.line_code == "TEST-LINE_A1"

    def test_valid_line_code_numbers_only(self):
        """Valid line_code with numbers"""
        obj = ProductionLineCreate(
            line_code="LINE01",
            line_name="Test Line"
        )
        assert obj.line_code == "LINE01"

    def test_valid_line_code_complex(self):
        """Valid line_code with complex combination"""
        obj = ProductionLineCreate(
            line_code="LINE-01_A-B2",
            line_name="Test Line"
        )
        assert obj.line_code == "LINE-01_A-B2"

    def test_uppercase_conversion(self):
        """Lowercase line_code automatically converted to uppercase"""
        obj = ProductionLineCreate(
            line_code="line-a_01",
            line_name="Test Line"
        )
        assert obj.line_code == "LINE-A_01"

    def test_uppercase_conversion_mixed_case(self):
        """Mixed case line_code converted to uppercase"""
        obj = ProductionLineCreate(
            line_code="LiNe-TeSt_01",
            line_name="Test Line"
        )
        assert obj.line_code == "LINE-TEST_01"

    def test_invalid_line_code_with_space(self):
        """line_code with space should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters, hyphens, and underscores" in error_msg

    def test_invalid_line_code_with_at_sign(self):
        """line_code with @ should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE@A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters, hyphens, and underscores" in error_msg

    def test_invalid_line_code_with_hash(self):
        """line_code with # should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE#01",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters, hyphens, and underscores" in error_msg

    def test_invalid_line_code_with_dollar_sign(self):
        """line_code with $ should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE$A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters, hyphens, and underscores" in error_msg

    def test_invalid_line_code_with_dot(self):
        """line_code with . should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE.A",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "alphanumeric characters, hyphens, and underscores" in error_msg

    def test_invalid_line_code_empty_string(self):
        """Empty line_code should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="",
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "line_code cannot be empty" in error_msg

    def test_invalid_line_code_too_long(self):
        """line_code exceeding max length should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="A" * 51,  # Max is 50
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "at most 50 characters" in error_msg or "ensure this value has at most 50 characters" in error_msg

    def test_required_fields(self):
        """line_code and line_name are required"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_name="Test Line"
            )
        error_msg = str(exc_info.value)
        assert "line_code" in error_msg

        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE-A"
            )
        error_msg = str(exc_info.value)
        assert "line_name" in error_msg

    def test_optional_fields(self):
        """Optional fields can be omitted"""
        obj = ProductionLineCreate(
            line_code="LINE-A",
            line_name="Test Line"
        )
        assert obj.description is None
        assert obj.cycle_time_sec is None
        assert obj.location is None
        assert obj.is_active is True  # Default value


class TestProductionLineUpdateValidation:
    """Test ProductionLineUpdate schema validation"""

    def test_update_valid_line_code_with_underscore(self):
        """Update schema accepts underscore"""
        obj = ProductionLineUpdate(line_code="NEW_LINE-01")
        assert obj.line_code == "NEW_LINE-01"

    def test_update_uppercase_conversion(self):
        """Update schema converts to uppercase"""
        obj = ProductionLineUpdate(line_code="new_line")
        assert obj.line_code == "NEW_LINE"

    def test_update_invalid_line_code_with_space(self):
        """Update schema rejects space"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineUpdate(line_code="NEW LINE")
        error_msg = str(exc_info.value)
        assert "alphanumeric characters, hyphens, and underscores" in error_msg

    def test_update_all_fields_optional(self):
        """All fields are optional in update schema"""
        obj = ProductionLineUpdate()
        assert obj.line_code is None
        assert obj.line_name is None
        assert obj.description is None
        assert obj.cycle_time_sec is None
        assert obj.location is None
        assert obj.is_active is None

    def test_update_partial_update(self):
        """Partial update with only some fields"""
        obj = ProductionLineUpdate(
            line_name="Updated Name",
            is_active=False
        )
        assert obj.line_code is None
        assert obj.line_name == "Updated Name"
        assert obj.is_active is False

    def test_update_empty_string_rejected(self):
        """Empty string for line_code should be rejected even in update"""
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

    def test_line_code_numbers_hyphens_underscores_only(self):
        """line_code with only numbers, hyphens, and underscores"""
        obj = ProductionLineCreate(
            line_code="123-456_789",
            line_name="Test"
        )
        assert obj.line_code == "123-456_789"

    def test_cycle_time_negative_rejected(self):
        """Negative cycle time should be rejected"""
        with pytest.raises(ValidationError) as exc_info:
            ProductionLineCreate(
                line_code="LINE-A",
                line_name="Test",
                cycle_time_sec=-1
            )
        error_msg = str(exc_info.value)
        assert "greater than or equal to 0" in error_msg

    def test_cycle_time_zero_valid(self):
        """Zero cycle time should be valid"""
        obj = ProductionLineCreate(
            line_code="LINE-A",
            line_name="Test",
            cycle_time_sec=0
        )
        assert obj.cycle_time_sec == 0

    def test_is_active_default_true(self):
        """is_active defaults to True"""
        obj = ProductionLineCreate(
            line_code="LINE-A",
            line_name="Test"
        )
        assert obj.is_active is True

    def test_is_active_can_be_set_false(self):
        """is_active can be explicitly set to False"""
        obj = ProductionLineCreate(
            line_code="LINE-A",
            line_name="Test",
            is_active=False
        )
        assert obj.is_active is False
