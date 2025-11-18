"""
Unit tests for LOT schema validation (app/schemas/lot.py).

Tests cover:
    - LotStatus enum validation and conversion
    - Shift enum validation and conversion
    - LotBase field validators (shift, status, target_quantity)
    - LotCreate schema validation
    - LotUpdate schema validation with all field validators
    - LotUpdate model validator for quantity consistency
    - LotInDB computed fields (defect_rate, pass_rate)
    - Edge cases and error conditions

Coverage Goals:
    - Test all field validators with valid and invalid inputs
    - Test enum conversions (string to enum, enum to value)
    - Test cross-field validation in model_validator
    - Test boundary conditions (min/max values)
    - Test type validation errors
    - Increase LOT schema coverage from 53% to 70%+
"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.lot import (
    LotStatus,
    Shift,
    LotBase,
    LotCreate,
    LotUpdate,
    LotInDB,
    ProductModelSchema
)


class TestLotStatusEnum:
    """Test LotStatus enumeration."""

    def test_lot_status_values(self):
        """Test that LotStatus enum has correct values."""
        assert LotStatus.CREATED.value == "CREATED"
        assert LotStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert LotStatus.COMPLETED.value == "COMPLETED"
        assert LotStatus.CLOSED.value == "CLOSED"

    def test_lot_status_from_string(self):
        """Test creating LotStatus from string."""
        assert LotStatus("CREATED") == LotStatus.CREATED
        assert LotStatus("IN_PROGRESS") == LotStatus.IN_PROGRESS
        assert LotStatus("COMPLETED") == LotStatus.COMPLETED
        assert LotStatus("CLOSED") == LotStatus.CLOSED

    def test_lot_status_invalid_value(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError):
            LotStatus("INVALID_STATUS")


class TestShiftEnum:
    """Test Shift enumeration."""

    def test_shift_values(self):
        """Test that Shift enum has correct values."""
        assert Shift.DAY.value == "D"
        assert Shift.NIGHT.value == "N"

    def test_shift_from_string(self):
        """Test creating Shift from string."""
        assert Shift("D") == Shift.DAY
        assert Shift("N") == Shift.NIGHT

    def test_shift_invalid_value(self):
        """Test that invalid shift raises ValueError."""
        with pytest.raises(ValueError):
            Shift("X")


class TestLotBaseValidation:
    """Test LotBase schema validation."""

    def test_create_valid_lot_base(self):
        """Test creating valid LotBase instance."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50,
            status="CREATED"
        )
        assert lot.product_model_id == 1
        assert lot.shift == "D"
        assert lot.target_quantity == 50
        assert lot.status == "CREATED"

    def test_shift_validator_uppercase_conversion(self):
        """Test that shift validator converts lowercase to uppercase."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="d",  # lowercase
            target_quantity=50
        )
        assert lot.shift == "D"  # Should be uppercase

    def test_shift_validator_night_shift(self):
        """Test shift validator with night shift."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="n",  # lowercase night
            target_quantity=50
        )
        assert lot.shift == "N"

    def test_shift_validator_enum_name(self):
        """Test shift validator with enum name (DAY, NIGHT)."""
        lot_day = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="DAY",
            target_quantity=50
        )
        assert lot_day.shift == "D"

        lot_night = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="NIGHT",
            target_quantity=50
        )
        assert lot_night.shift == "N"

    def test_shift_validator_from_shift_enum(self):
        """Test shift validator with Shift enum instance."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift=Shift.DAY,
            target_quantity=50
        )
        assert lot.shift == "D"

    def test_shift_validator_invalid_value(self):
        """Test shift validator with invalid value."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="X",  # Invalid shift
                target_quantity=50
            )
        assert "shift must be 'D' (Day) or 'N' (Night)" in str(exc_info.value)

    def test_shift_validator_invalid_type(self):
        """Test shift validator with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift=123,  # Integer instead of string
                target_quantity=50
            )
        assert "shift must be a string" in str(exc_info.value)

    def test_status_validator_uppercase_conversion(self):
        """Test that status validator converts to uppercase."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50,
            status="created"  # lowercase
        )
        assert lot.status == "CREATED"

    def test_status_validator_all_valid_statuses(self):
        """Test status validator with all valid status values."""
        for status_value in ["CREATED", "IN_PROGRESS", "COMPLETED", "CLOSED"]:
            lot = LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity=50,
                status=status_value
            )
            assert lot.status == status_value

    def test_status_validator_from_lot_status_enum(self):
        """Test status validator with LotStatus enum instance."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50,
            status=LotStatus.IN_PROGRESS
        )
        assert lot.status == "IN_PROGRESS"

    def test_status_validator_invalid_value(self):
        """Test status validator with invalid value."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity=50,
                status="INVALID_STATUS"
            )
        assert "status must be one of" in str(exc_info.value)

    def test_status_validator_invalid_type(self):
        """Test status validator with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity=50,
                status=999  # Integer instead of string
            )
        assert "status must be a string" in str(exc_info.value)

    def test_target_quantity_minimum_value(self):
        """Test target_quantity validator with minimum value (1)."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=1  # Minimum
        )
        assert lot.target_quantity == 1

    def test_target_quantity_maximum_value(self):
        """Test target_quantity validator with maximum value (100)."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=100  # Maximum
        )
        assert lot.target_quantity == 100

    def test_target_quantity_below_minimum(self):
        """Test target_quantity validator rejects value below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity=0  # Below minimum
            )
        assert "target_quantity must be at least 1" in str(exc_info.value)

    def test_target_quantity_above_maximum(self):
        """Test target_quantity validator rejects value above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity=101  # Above maximum
            )
        assert "target_quantity cannot exceed 100 units per LOT" in str(exc_info.value)

    def test_target_quantity_invalid_type(self):
        """Test target_quantity validator with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            LotBase(
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity="fifty"  # String instead of int
            )
        assert "target_quantity must be an integer" in str(exc_info.value)

    def test_product_model_id_validation(self):
        """Test product_model_id field validation (must be > 0)."""
        with pytest.raises(ValidationError):
            LotBase(
                product_model_id=0,  # Must be > 0
                production_date=date.today(),
                shift="D",
                target_quantity=50
            )

    def test_status_default_value(self):
        """Test that status defaults to CREATED."""
        lot = LotBase(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50
            # status not provided
        )
        assert lot.status == "CREATED"


class TestLotCreateSchema:
    """Test LotCreate schema."""

    def test_lot_create_inherits_validation(self):
        """Test that LotCreate inherits all LotBase validation."""
        lot = LotCreate(
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=75
        )
        assert lot.product_model_id == 1
        assert lot.target_quantity == 75

    def test_lot_create_with_all_fields(self):
        """Test creating LotCreate with all fields."""
        lot = LotCreate(
            product_model_id=2,
            production_date=date(2025, 11, 20),
            shift="N",
            target_quantity=50,
            status="CREATED"
        )
        assert lot.shift == "N"
        assert lot.status == "CREATED"


class TestLotUpdateValidation:
    """Test LotUpdate schema validation."""

    def test_create_empty_lot_update(self):
        """Test creating LotUpdate with no fields (all optional)."""
        lot_update = LotUpdate()
        assert lot_update.production_date is None
        assert lot_update.shift is None
        assert lot_update.target_quantity is None

    def test_update_shift_validation(self):
        """Test LotUpdate shift validator."""
        lot_update = LotUpdate(shift="d")
        assert lot_update.shift == "D"

    def test_update_shift_none(self):
        """Test LotUpdate shift validator with None."""
        lot_update = LotUpdate(shift=None)
        assert lot_update.shift is None

    def test_update_status_validation(self):
        """Test LotUpdate status validator."""
        lot_update = LotUpdate(status="in_progress")
        assert lot_update.status == "IN_PROGRESS"

    def test_update_status_none(self):
        """Test LotUpdate status validator with None."""
        lot_update = LotUpdate(status=None)
        assert lot_update.status is None

    def test_update_target_quantity_validation(self):
        """Test LotUpdate target_quantity validator."""
        lot_update = LotUpdate(target_quantity=75)
        assert lot_update.target_quantity == 75

    def test_update_target_quantity_none(self):
        """Test LotUpdate target_quantity validator with None."""
        lot_update = LotUpdate(target_quantity=None)
        assert lot_update.target_quantity is None

    def test_update_target_quantity_below_minimum(self):
        """Test LotUpdate target_quantity validator rejects below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(target_quantity=0)
        assert "target_quantity must be at least 1" in str(exc_info.value)

    def test_update_actual_quantity_validation(self):
        """Test LotUpdate actual_quantity validator."""
        lot_update = LotUpdate(actual_quantity=45)
        assert lot_update.actual_quantity == 45

    def test_update_actual_quantity_zero(self):
        """Test LotUpdate actual_quantity validator accepts zero."""
        lot_update = LotUpdate(actual_quantity=0)
        assert lot_update.actual_quantity == 0

    def test_update_actual_quantity_negative(self):
        """Test LotUpdate actual_quantity validator rejects negative."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(actual_quantity=-5)
        assert "actual_quantity cannot be negative" in str(exc_info.value)

    def test_update_actual_quantity_invalid_type(self):
        """Test LotUpdate actual_quantity validator with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(actual_quantity="forty")
        assert "actual_quantity must be an integer" in str(exc_info.value)

    def test_update_passed_quantity_validation(self):
        """Test LotUpdate passed_quantity validator."""
        lot_update = LotUpdate(passed_quantity=40)
        assert lot_update.passed_quantity == 40

    def test_update_passed_quantity_zero(self):
        """Test LotUpdate passed_quantity validator accepts zero."""
        lot_update = LotUpdate(passed_quantity=0)
        assert lot_update.passed_quantity == 0

    def test_update_passed_quantity_negative(self):
        """Test LotUpdate passed_quantity validator rejects negative."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(passed_quantity=-10)
        assert "passed_quantity cannot be negative" in str(exc_info.value)

    def test_update_passed_quantity_invalid_type(self):
        """Test LotUpdate passed_quantity validator with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(passed_quantity="thirty")
        assert "passed_quantity must be an integer" in str(exc_info.value)

    def test_update_failed_quantity_validation(self):
        """Test LotUpdate failed_quantity validator."""
        lot_update = LotUpdate(failed_quantity=5)
        assert lot_update.failed_quantity == 5

    def test_update_failed_quantity_zero(self):
        """Test LotUpdate failed_quantity validator accepts zero."""
        lot_update = LotUpdate(failed_quantity=0)
        assert lot_update.failed_quantity == 0

    def test_update_failed_quantity_negative(self):
        """Test LotUpdate failed_quantity validator rejects negative."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(failed_quantity=-3)
        assert "failed_quantity cannot be negative" in str(exc_info.value)

    def test_update_failed_quantity_invalid_type(self):
        """Test LotUpdate failed_quantity validator with invalid type."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(failed_quantity="five")
        assert "failed_quantity must be an integer" in str(exc_info.value)


class TestLotUpdateQuantityConsistency:
    """Test LotUpdate model validator for quantity consistency."""

    def test_quantity_consistency_valid_quantities(self):
        """Test quantity consistency with valid quantities."""
        lot_update = LotUpdate(
            target_quantity=50,
            actual_quantity=45,
            passed_quantity=40,
            failed_quantity=5
        )
        assert lot_update.actual_quantity == 45
        assert lot_update.passed_quantity == 40
        assert lot_update.failed_quantity == 5

    def test_quantity_consistency_actual_exceeds_target(self):
        """Test quantity consistency rejects actual > target."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(
                target_quantity=50,
                actual_quantity=55  # Exceeds target
            )
        assert "actual_quantity cannot exceed target_quantity" in str(exc_info.value)

    def test_quantity_consistency_passed_exceeds_actual(self):
        """Test quantity consistency rejects passed > actual."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(
                actual_quantity=45,
                passed_quantity=50  # Exceeds actual
            )
        assert "passed_quantity cannot exceed actual_quantity" in str(exc_info.value)

    def test_quantity_consistency_failed_exceeds_actual(self):
        """Test quantity consistency rejects failed > actual."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(
                actual_quantity=45,
                failed_quantity=50  # Exceeds actual
            )
        assert "failed_quantity cannot exceed actual_quantity" in str(exc_info.value)

    def test_quantity_consistency_passed_plus_failed_exceeds_actual(self):
        """Test quantity consistency rejects passed + failed > actual."""
        with pytest.raises(ValidationError) as exc_info:
            LotUpdate(
                actual_quantity=45,
                passed_quantity=30,
                failed_quantity=20  # 30 + 20 = 50 > 45
            )
        assert "passed_quantity + failed_quantity cannot exceed actual_quantity" in str(exc_info.value)

    def test_quantity_consistency_exact_sum(self):
        """Test quantity consistency accepts passed + failed == actual."""
        lot_update = LotUpdate(
            actual_quantity=50,
            passed_quantity=45,
            failed_quantity=5  # 45 + 5 = 50
        )
        assert lot_update.actual_quantity == 50
        assert lot_update.passed_quantity == 45
        assert lot_update.failed_quantity == 5

    def test_quantity_consistency_partial_update_no_actual(self):
        """Test quantity consistency with partial update (no actual_quantity)."""
        # Should not raise error if actual_quantity is not provided
        lot_update = LotUpdate(
            passed_quantity=40,
            failed_quantity=5
        )
        assert lot_update.passed_quantity == 40
        assert lot_update.failed_quantity == 5

    def test_quantity_consistency_actual_equals_target(self):
        """Test quantity consistency accepts actual == target."""
        lot_update = LotUpdate(
            target_quantity=50,
            actual_quantity=50  # Equal to target
        )
        assert lot_update.actual_quantity == 50


class TestLotInDBSchema:
    """Test LotInDB schema with computed fields."""

    def test_defect_rate_calculation(self):
        """Test defect_rate is calculated from failed_quantity / actual_quantity."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-001",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=100,
            actual_quantity=100,
            passed_quantity=90,
            failed_quantity=10,  # 10% defect rate
            status="COMPLETED",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert lot.defect_rate == 10.0

    def test_pass_rate_calculation(self):
        """Test pass_rate is calculated from passed_quantity / actual_quantity."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-002",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=100,
            actual_quantity=100,
            passed_quantity=95,  # 95% pass rate
            failed_quantity=5,
            status="COMPLETED",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert lot.pass_rate == 95.0

    def test_defect_rate_with_zero_actual_quantity(self):
        """Test defect_rate returns None when actual_quantity is zero."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-003",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50,
            actual_quantity=0,  # No production yet
            passed_quantity=0,
            failed_quantity=0,
            status="CREATED",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert lot.defect_rate is None

    def test_pass_rate_with_zero_actual_quantity(self):
        """Test pass_rate returns None when actual_quantity is zero."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-004",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50,
            actual_quantity=0,  # No production yet
            passed_quantity=0,
            failed_quantity=0,
            status="CREATED",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert lot.pass_rate is None

    def test_rates_rounded_to_two_decimals(self):
        """Test that rates are rounded to 2 decimal places."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-005",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=75,
            actual_quantity=75,
            passed_quantity=73,  # 97.333...%
            failed_quantity=2,   # 2.666...%
            status="COMPLETED",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert lot.pass_rate == 97.33
        assert lot.defect_rate == 2.67

    def test_lot_number_pattern_validation(self):
        """Test lot_number field validates against pattern."""
        # Valid lot_number
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-001",  # Valid format
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=50,
            actual_quantity=0,
            passed_quantity=0,
            failed_quantity=0,
            status="CREATED",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert lot.lot_number == "WF-KR-251120D-001"

    def test_lot_number_invalid_pattern(self):
        """Test lot_number field rejects invalid pattern."""
        with pytest.raises(ValidationError):
            LotInDB(
                id=1,
                lot_number="INVALID-LOT-NUMBER",  # Invalid format
                product_model_id=1,
                production_date=date.today(),
                shift="D",
                target_quantity=50,
                actual_quantity=0,
                passed_quantity=0,
                failed_quantity=0,
                status="CREATED",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

    def test_lot_indb_with_product_model(self):
        """Test LotInDB with nested ProductModel schema."""
        product_model = ProductModelSchema(
            id=1,
            model_code="NH-F2X-001",
            model_name="NeuroHub F2X Model",
            category="Electronics",
            production_cycle_days=5,
            status="ACTIVE"
        )

        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120N-001",
            product_model_id=1,
            production_date=date.today(),
            shift="N",
            target_quantity=100,
            actual_quantity=95,
            passed_quantity=90,
            failed_quantity=5,
            status="COMPLETED",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            product_model=product_model
        )
        assert lot.product_model.model_code == "NH-F2X-001"
        assert lot.product_model.status == "ACTIVE"

    def test_defect_rate_provided_directly(self):
        """Test that provided defect_rate is used instead of calculation."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-006",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=100,
            actual_quantity=100,
            passed_quantity=90,
            failed_quantity=10,
            status="COMPLETED",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            defect_rate=15.0  # Provided directly (different from calculation)
        )
        assert lot.defect_rate == 15.0  # Should use provided value

    def test_pass_rate_provided_directly(self):
        """Test that provided pass_rate is used instead of calculation."""
        lot = LotInDB(
            id=1,
            lot_number="WF-KR-251120D-007",
            product_model_id=1,
            production_date=date.today(),
            shift="D",
            target_quantity=100,
            actual_quantity=100,
            passed_quantity=90,
            failed_quantity=10,
            status="COMPLETED",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            pass_rate=85.0  # Provided directly (different from calculation)
        )
        assert lot.pass_rate == 85.0  # Should use provided value


class TestProductModelSchema:
    """Test ProductModelSchema nested in LotInDB."""

    def test_create_product_model_schema(self):
        """Test creating ProductModelSchema."""
        pm = ProductModelSchema(
            id=1,
            model_code="TEST-001",
            model_name="Test Model",
            category="Test Category",
            production_cycle_days=3,
            status="ACTIVE"
        )
        assert pm.id == 1
        assert pm.model_code == "TEST-001"
        assert pm.status == "ACTIVE"

    def test_product_model_schema_optional_fields(self):
        """Test ProductModelSchema with optional fields as None."""
        pm = ProductModelSchema(
            id=1,
            model_code="TEST-002",
            model_name="Test Model 2",
            category=None,  # Optional
            production_cycle_days=None,  # Optional
            status="INACTIVE"
        )
        assert pm.category is None
        assert pm.production_cycle_days is None
