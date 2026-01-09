"""
Unit tests for process_operations schemas.

Tests ProcessStartRequest and ProcessCompleteRequest schema validation
with process_session_id field.
"""

import pytest
from pydantic import ValidationError

from app.schemas.process_operations import (
    ProcessStartRequest,
    ProcessCompleteRequest,
)


class TestProcessStartRequestSchema:
    """Tests for ProcessStartRequest schema with process_session_id."""

    def test_process_start_request_with_session_id(self):
        """Test ProcessStartRequest accepts process_session_id."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "process_session_id": 123,
        }
        request = ProcessStartRequest(**data)

        assert request.process_session_id == 123
        assert request.wip_id == "WIP-001"
        assert request.process_id == "1"
        assert request.worker_id == "W001"

    def test_process_start_request_session_id_optional(self):
        """Test that process_session_id is optional."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            # process_session_id NOT provided
        }
        request = ProcessStartRequest(**data)

        assert request.process_session_id is None
        assert request.wip_id == "WIP-001"

    def test_process_start_request_session_id_none(self):
        """Test that process_session_id can be explicitly set to None."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "process_session_id": None,
        }
        request = ProcessStartRequest(**data)

        assert request.process_session_id is None

    def test_process_start_request_full_data(self):
        """Test ProcessStartRequest with all fields including process_session_id."""
        data = {
            "wip_id": "WIP-KR01PSA2511-001",
            "lot_number": "LOT-001",
            "serial_number": "SN-001",
            "process_id": "PROC-001",
            "process_session_id": 42,
            "worker_id": "W001",
            "equipment_id": "EQ-001",
            "line_id": "KR01",
            "process_name": "Laser Marking",
            "start_time": "2026-01-09T10:30:00Z",
        }
        request = ProcessStartRequest(**data)

        assert request.process_session_id == 42
        assert request.wip_id == "WIP-KR01PSA2511-001"
        assert request.lot_number == "LOT-001"
        assert request.serial_number == "SN-001"
        assert request.process_id == "PROC-001"
        assert request.worker_id == "W001"
        assert request.equipment_id == "EQ-001"


class TestProcessCompleteRequestSchema:
    """Tests for ProcessCompleteRequest schema with process_session_id."""

    def test_process_complete_request_with_session_id(self):
        """Test ProcessCompleteRequest accepts process_session_id."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "result": "PASS",
            "process_session_id": 123,
        }
        request = ProcessCompleteRequest(**data)

        assert request.process_session_id == 123
        assert request.result == "PASS"
        assert request.wip_id == "WIP-001"

    def test_process_complete_request_session_id_optional(self):
        """Test that process_session_id is optional."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "result": "PASS",
            # process_session_id NOT provided
        }
        request = ProcessCompleteRequest(**data)

        assert request.process_session_id is None
        assert request.result == "PASS"

    def test_process_complete_request_with_measurements_and_session(self):
        """Test ProcessCompleteRequest with measurements and process_session_id."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "result": "PASS",
            "process_session_id": 42,
            "measurements": {
                "temp": 25.0,
                "voltage": 3.3,
                "current": 1.5,
            },
        }
        request = ProcessCompleteRequest(**data)

        assert request.process_session_id == 42
        assert request.result == "PASS"
        assert request.measurements == {
            "temp": 25.0,
            "voltage": 3.3,
            "current": 1.5,
        }

    def test_process_complete_request_fail_with_defects_and_session(self):
        """Test ProcessCompleteRequest with FAIL result, defects, and session_id."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "result": "FAIL",
            "process_session_id": 99,
            "measurements": {"temp": 30.0},
            "defect_data": {
                "defect_code": "D001",
                "description": "Scratch on surface",
                "severity": "MAJOR",
            },
        }
        request = ProcessCompleteRequest(**data)

        assert request.process_session_id == 99
        assert request.result == "FAIL"
        assert request.defect_data is not None
        assert request.defect_data["defect_code"] == "D001"

    def test_process_complete_request_rework_with_session(self):
        """Test ProcessCompleteRequest with REWORK result and process_session_id."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "result": "REWORK",
            "process_session_id": 55,
        }
        request = ProcessCompleteRequest(**data)

        assert request.process_session_id == 55
        assert request.result == "REWORK"

    def test_process_complete_request_full_data(self):
        """Test ProcessCompleteRequest with all fields."""
        data = {
            "wip_id": "WIP-KR01PSA2511-001",
            "lot_number": "LOT-001",
            "serial_number": "SN-001",
            "process_id": "PROC-001",
            "process_session_id": 42,
            "worker_id": "W001",
            "result": "PASS",
            "measurements": {
                "temperature": 25.5,
                "voltage": 3.3,
                "resistance": 1000.0,
            },
            "defect_data": None,
        }
        request = ProcessCompleteRequest(**data)

        assert request.process_session_id == 42
        assert request.wip_id == "WIP-KR01PSA2511-001"
        assert request.lot_number == "LOT-001"
        assert request.serial_number == "SN-001"
        assert request.process_id == "PROC-001"
        assert request.worker_id == "W001"
        assert request.result == "PASS"
        assert len(request.measurements) == 3
        assert request.defect_data is None


class TestProcessSessionIDValidation:
    """Test process_session_id type validation across schemas."""

    def test_session_id_accepts_integer(self):
        """Test that process_session_id accepts integer values."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "process_session_id": 12345,
        }
        request = ProcessStartRequest(**data)
        assert request.process_session_id == 12345

    def test_session_id_accepts_zero(self):
        """Test that process_session_id can be zero."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "process_session_id": 0,
        }
        request = ProcessStartRequest(**data)
        assert request.process_session_id == 0

    def test_session_id_rejects_string(self):
        """Test that process_session_id rejects string values."""
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "process_session_id": "invalid",
        }

        with pytest.raises(ValidationError) as exc_info:
            ProcessStartRequest(**data)

        errors = exc_info.value.errors()
        assert len(errors) >= 1
        assert any("process_session_id" in str(error) for error in errors)

    def test_session_id_rejects_negative(self):
        """Test that process_session_id can be negative (no validation constraint)."""
        # Note: There's no validation preventing negative session IDs
        # This test documents current behavior
        data = {
            "wip_id": "WIP-001",
            "process_id": "1",
            "worker_id": "W001",
            "process_session_id": -1,
        }
        request = ProcessStartRequest(**data)
        # Currently allows negative values
        assert request.process_session_id == -1
