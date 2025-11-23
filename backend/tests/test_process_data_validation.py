"""
Comprehensive test cases for ProcessData schema validation.

This module tests all validation rules and business logic in the ProcessData schemas,
including edge cases, error messages, and warnings.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
import warnings

from app.schemas.process_data import (
    DataLevel,
    ProcessResult,
    ProcessDataBase,
    ProcessDataCreate,
    ProcessDataUpdate,
    ProcessDataInDB,
    validate_process_data_context
)


class TestDataLevelValidation:
    """Test cases for DataLevel enum validation."""

    def test_valid_data_levels(self):
        """Test all valid data level values."""
        assert DataLevel("LOT") == DataLevel.LOT
        assert DataLevel("WIP") == DataLevel.WIP
        assert DataLevel("SERIAL") == DataLevel.SERIAL

    def test_case_insensitive_data_level(self):
        """Test that data level is case-insensitive."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "lot",  # lowercase
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.data_level == DataLevel.LOT

    def test_invalid_data_level(self):
        """Test invalid data level raises error with context."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "INVALID",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "Invalid data_level 'INVALID'" in error_msg
        assert "Must be one of ['LOT', 'WIP', 'SERIAL']" in error_msg


class TestProcessResultValidation:
    """Test cases for ProcessResult enum validation."""

    def test_valid_results(self):
        """Test all valid result values."""
        assert ProcessResult("PASS") == ProcessResult.PASS
        assert ProcessResult("FAIL") == ProcessResult.FAIL
        assert ProcessResult("REWORK") == ProcessResult.REWORK

    def test_case_insensitive_result(self):
        """Test that result is case-insensitive."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "pass",  # lowercase
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.result == ProcessResult.PASS

    def test_invalid_result(self):
        """Test invalid result raises error with context."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "SUCCESS",  # Invalid
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "Invalid result 'SUCCESS'" in error_msg
        assert "Must be one of ['PASS', 'FAIL', 'REWORK']" in error_msg


class TestLOTLevelValidation:
    """Test cases for LOT-level data validation."""

    def test_valid_lot_level_data(self):
        """Test valid LOT-level process data."""
        data = {
            "lot_id": 1,
            "serial_id": None,
            "wip_id": None,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "PASS",
            "measurements": {"temperature": 25.5},
            "started_at": datetime.now(),
            "completed_at": datetime.now() + timedelta(minutes=10)
        }
        schema = ProcessDataCreate(**data)
        assert schema.data_level == DataLevel.LOT
        assert schema.serial_id is None
        assert schema.wip_id is None

    def test_lot_level_with_serial_id_error(self):
        """Test LOT-level data with serial_id raises error."""
        data = {
            "lot_id": 1,
            "serial_id": 100,  # Should be None for LOT level
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "serial_id must be None when data_level='LOT'" in error_msg
        assert "Current: serial_id=100" in error_msg

    def test_lot_level_with_wip_id_error(self):
        """Test LOT-level data with wip_id raises error."""
        data = {
            "lot_id": 1,
            "wip_id": 50,  # Should be None for LOT level
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "wip_id must be None when data_level='LOT'" in error_msg
        assert "Current: wip_id=50" in error_msg


class TestWIPLevelValidation:
    """Test cases for WIP-level data validation."""

    def test_valid_wip_level_data(self):
        """Test valid WIP-level process data."""
        data = {
            "lot_id": 1,
            "serial_id": None,
            "wip_id": 50,
            "process_id": 3,
            "operator_id": 1,
            "data_level": "WIP",
            "result": "PASS",
            "measurements": {"pressure": 1.5},
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.data_level == DataLevel.WIP
        assert schema.wip_id == 50
        assert schema.serial_id is None

    def test_wip_level_without_wip_id_error(self):
        """Test WIP-level data without wip_id raises error."""
        data = {
            "lot_id": 1,
            "wip_id": None,  # Required for WIP level
            "process_id": 3,
            "operator_id": 1,
            "data_level": "WIP",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "wip_id is required when data_level='WIP'" in error_msg

    def test_wip_level_with_serial_id_error(self):
        """Test WIP-level data with serial_id raises error."""
        data = {
            "lot_id": 1,
            "serial_id": 100,  # Should be None for WIP level
            "wip_id": 50,
            "process_id": 3,
            "operator_id": 1,
            "data_level": "WIP",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "serial_id must be None when data_level='WIP'" in error_msg


class TestSERIALLevelValidation:
    """Test cases for SERIAL-level data validation."""

    def test_valid_serial_level_data(self):
        """Test valid SERIAL-level process data."""
        data = {
            "lot_id": 1,
            "serial_id": 100,
            "process_id": 7,
            "operator_id": 1,
            "data_level": "SERIAL",
            "result": "PASS",
            "measurements": {"voltage": 3.3},
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.data_level == DataLevel.SERIAL
        assert schema.serial_id == 100

    def test_serial_level_with_wip_id(self):
        """Test SERIAL-level data can have optional wip_id."""
        data = {
            "lot_id": 1,
            "serial_id": 100,
            "wip_id": 50,  # Optional for SERIAL level
            "process_id": 5,
            "operator_id": 1,
            "data_level": "SERIAL",
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.data_level == DataLevel.SERIAL
        assert schema.serial_id == 100
        assert schema.wip_id == 50

    def test_serial_level_without_serial_id_error(self):
        """Test SERIAL-level data without serial_id raises error."""
        data = {
            "lot_id": 1,
            "serial_id": None,  # Required for SERIAL level
            "process_id": 7,
            "operator_id": 1,
            "data_level": "SERIAL",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "serial_id is required when data_level='SERIAL'" in error_msg


class TestDefectsResultConsistency:
    """Test cases for defects and result consistency validation."""

    def test_pass_result_without_defects(self):
        """Test PASS result without defects is valid."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "PASS",
            "defects": None,
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.result == ProcessResult.PASS
        assert schema.defects is None

    def test_pass_result_with_empty_defects(self):
        """Test PASS result with empty defects dict is valid."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "PASS",
            "defects": {},  # Empty dict treated as None
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.result == ProcessResult.PASS
        assert schema.defects is None

    def test_pass_result_with_defects_error(self):
        """Test PASS result with defects raises error."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "PASS",
            "defects": {"type": "crack"},  # Should be None for PASS
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "defects should be None or empty when result='PASS'" in error_msg

    def test_fail_result_with_defects(self):
        """Test FAIL result with defects is valid."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "FAIL",
            "defects": {
                "type": "crack",
                "location": "edge",
                "severity": "critical"
            },
            "notes": "Visual inspection failed",
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.result == ProcessResult.FAIL
        assert schema.defects["type"] == "crack"

    def test_fail_result_without_defects_error(self):
        """Test FAIL result without defects raises error."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "FAIL",
            "defects": None,  # Required for FAIL
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "defects information is required when result='FAIL'" in error_msg
        assert "Please provide defect details" in error_msg

    def test_fail_result_without_notes_warning(self):
        """Test FAIL result without notes issues warning."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "FAIL",
            "defects": {"type": "crack"},
            "notes": None,  # Should trigger warning
            "started_at": datetime.now()
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ProcessDataCreate(**data)

            assert len(w) >= 1
            warning_msg = str(w[0].message)
            assert "Notes are recommended when result='FAIL'" in warning_msg

    def test_rework_result_with_defects(self):
        """Test REWORK result with defects is valid."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "REWORK",
            "defects": {"reason": "alignment issue"},
            "notes": "Requires realignment",
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.result == ProcessResult.REWORK
        assert schema.defects["reason"] == "alignment issue"

    def test_rework_result_without_defects(self):
        """Test REWORK result without defects is valid."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "REWORK",
            "defects": None,
            "notes": "Preventive rework",
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.result == ProcessResult.REWORK
        assert schema.defects is None


class TestTimestampValidation:
    """Test cases for timestamp validation."""

    def test_valid_timestamps(self):
        """Test valid timestamp order."""
        start = datetime.now()
        end = start + timedelta(minutes=15)

        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": start,
            "completed_at": end
        }
        schema = ProcessDataCreate(**data)
        assert schema.started_at == start
        assert schema.completed_at == end

    def test_same_start_and_end_timestamps(self):
        """Test same start and end timestamps is valid (instant process)."""
        timestamp = datetime.now()

        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": timestamp,
            "completed_at": timestamp
        }
        schema = ProcessDataCreate(**data)
        assert schema.started_at == timestamp
        assert schema.completed_at == timestamp

    def test_invalid_timestamp_order(self):
        """Test completed_at before started_at raises error."""
        start = datetime.now()
        end = start - timedelta(minutes=15)  # Before start

        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": start,
            "completed_at": end
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "completed_at must be greater than or equal to started_at" in error_msg
        assert "invalid duration=" in error_msg

    def test_optional_completed_at(self):
        """Test that completed_at is optional."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": datetime.now(),
            "completed_at": None
        }
        schema = ProcessDataCreate(**data)
        assert schema.completed_at is None


class TestMeasurementsValidation:
    """Test cases for measurements field validation."""

    def test_valid_measurements(self):
        """Test valid measurements dictionary."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": {
                "temperature": 25.5,
                "pressure": 1.0,
                "humidity": 45,
                "status": "stable",
                "sensors": ["s1", "s2"],
                "config": {"mode": "auto", "threshold": 0.5}
            },
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.measurements["temperature"] == 25.5
        assert schema.measurements["sensors"] == ["s1", "s2"]

    def test_empty_measurements(self):
        """Test empty measurements dict defaults to empty."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": {},
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.measurements == {}

    def test_none_measurements_defaults_to_empty(self):
        """Test None measurements defaults to empty dict."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": None,
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.measurements == {}

    def test_invalid_measurements_type(self):
        """Test invalid measurements type raises error."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": "not a dict",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "measurements must be a dictionary" in error_msg

    def test_measurements_with_invalid_key_type(self):
        """Test measurements with non-string key raises error."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": {123: "value"},  # Non-string key
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "measurement keys must be strings" in error_msg

    def test_measurements_with_non_serializable_value(self):
        """Test measurements with non-JSON-serializable value raises error."""
        class CustomObject:
            pass

        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": {"obj": CustomObject()},
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "must be JSON-serializable" in error_msg


class TestDefectsValidation:
    """Test cases for defects field validation."""

    def test_valid_defects(self):
        """Test valid defects dictionary."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "FAIL",
            "defects": {
                "type": "crack",
                "location": "edge",
                "severity": "critical",
                "count": 3,
                "images": ["img1.jpg", "img2.jpg"],
                "dimensions": {"width": 2.5, "length": 5.0}
            },
            "started_at": datetime.now()
        }
        schema = ProcessDataCreate(**data)
        assert schema.defects["type"] == "crack"
        assert schema.defects["count"] == 3

    def test_invalid_defects_type(self):
        """Test invalid defects type raises error."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "defects": "not a dict",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "defects must be a dictionary" in error_msg

    def test_defects_with_invalid_key_type(self):
        """Test defects with non-string key raises error."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "result": "FAIL",
            "defects": {456: "value"},  # Non-string key
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        assert "defect keys must be strings" in error_msg


class TestComprehensiveBusinessRules:
    """Test cases for comprehensive business rules validation."""

    def test_invalid_core_fields(self):
        """Test multiple invalid core fields with comprehensive error."""
        data = {
            "lot_id": -1,  # Invalid
            "process_id": 0,  # Invalid
            "operator_id": -5,  # Invalid
            "data_level": "LOT",
            "started_at": datetime.now()
        }
        with pytest.raises(ValidationError) as exc_info:
            ProcessDataCreate(**data)

        error_msg = str(exc_info.value)
        # Check for comprehensive error message
        assert "Business rules validation failed" in error_msg
        assert "Invalid lot_id=-1" in error_msg
        assert "Invalid process_id=0" in error_msg
        assert "Invalid operator_id=-5" in error_msg
        assert "Current data state:" in error_msg

    def test_no_measurements_warning(self):
        """Test that missing measurements generates warning."""
        data = {
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "measurements": {},
            "started_at": datetime.now()
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ProcessDataCreate(**data)

            # Check for measurement warning
            warning_messages = [str(warning.message) for warning in w]
            assert any("No measurements provided" in msg for msg in warning_messages)


class TestProcessDataUpdate:
    """Test cases for ProcessDataUpdate schema."""

    def test_partial_update(self):
        """Test partial update with only some fields."""
        data = {
            "result": "FAIL",
            "defects": {"type": "defect"},
            "notes": "Updated notes"
        }
        schema = ProcessDataUpdate(**data)
        assert schema.result == ProcessResult.FAIL
        assert schema.defects["type"] == "defect"
        assert schema.equipment_id is None  # Not provided

    def test_update_result_to_fail_warning(self):
        """Test updating result to FAIL without defects generates warning."""
        data = {
            "result": "FAIL",
            "defects": None
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ProcessDataUpdate(**data)

            assert len(w) >= 1
            warning_msg = str(w[0].message)
            assert "Updating result to 'FAIL' without providing defects" in warning_msg

    def test_update_result_to_pass_with_defects_warning(self):
        """Test updating result to PASS with defects generates warning."""
        data = {
            "result": "PASS",
            "defects": {"type": "old_defect"}
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            ProcessDataUpdate(**data)

            assert len(w) >= 1
            warning_msg = str(w[0].message)
            assert "Updating result to 'PASS' with defects present" in warning_msg

    def test_empty_update(self):
        """Test empty update is valid."""
        schema = ProcessDataUpdate()
        assert schema.result is None
        assert schema.defects is None
        assert schema.measurements is None


class TestProcessDataInDB:
    """Test cases for ProcessDataInDB schema."""

    def test_duration_calculation(self):
        """Test automatic duration calculation."""
        start = datetime.now()
        end = start + timedelta(minutes=10)

        data = {
            "id": 1,
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": start,
            "completed_at": end,
            "created_at": start
        }

        schema = ProcessDataInDB(**data)
        # Duration should be calculated as 600 seconds (10 minutes)
        assert schema.duration_seconds == 600

    def test_duration_none_when_not_completed(self):
        """Test duration is None when process not completed."""
        data = {
            "id": 1,
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": datetime.now(),
            "completed_at": None,
            "created_at": datetime.now()
        }

        schema = ProcessDataInDB(**data)
        assert schema.duration_seconds is None

    def test_provided_duration_preserved(self):
        """Test that explicitly provided duration is preserved."""
        data = {
            "id": 1,
            "lot_id": 1,
            "process_id": 1,
            "operator_id": 1,
            "data_level": "LOT",
            "started_at": datetime.now(),
            "completed_at": datetime.now() + timedelta(minutes=5),
            "duration_seconds": 999,  # Explicitly provided
            "created_at": datetime.now()
        }

        schema = ProcessDataInDB(**data)
        assert schema.duration_seconds == 999  # Preserved, not calculated


class TestValidateProcessDataContext:
    """Test cases for validate_process_data_context helper function."""

    def test_placeholder_implementation(self):
        """Test the placeholder implementation returns expected structure."""
        result = validate_process_data_context(
            lot_id=1,
            serial_id=100,
            wip_id=None,
            process_id=5,
            operator_id=2,
            equipment_id=3,
            data_level=DataLevel.SERIAL,
            db_session=None  # Placeholder doesn't use it
        )

        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "context" in result
        assert isinstance(result["valid"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["context"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])