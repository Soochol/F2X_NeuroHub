"""
Unit tests for SDK OutputProtocol class.
"""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from station_service.sdk.context import ExecutionContext
from station_service.sdk.protocol import OutputProtocol, MessageType


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def context():
    """Create a test execution context."""
    return ExecutionContext(
        execution_id="test-123",
        wip_id="WIP-001",
        sequence_name="test_sequence",
        sequence_version="1.0.0",
        hardware_config={},
        parameters={},
    )


@pytest.fixture
def protocol(context):
    """Create a test output protocol."""
    return OutputProtocol(context)


# ============================================================================
# Tests for OutputProtocol
# ============================================================================


class TestOutputProtocol:
    """Tests for OutputProtocol class."""

    def test_log_message(self, protocol):
        """Test log message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.log("info", "Test message", extra_key="extra_value")
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.LOG.value
        assert data["execution_id"] == "test-123"
        assert data["data"]["level"] == "info"
        assert data["data"]["message"] == "Test message"
        assert data["data"]["extra_key"] == "extra_value"
        assert "timestamp" in data

    def test_status_message(self, protocol):
        """Test status message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.status("running", 50.0, "test_step", "Testing...")
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.STATUS.value
        assert data["data"]["status"] == "running"
        assert data["data"]["progress"] == 50.0
        assert data["data"]["current_step"] == "test_step"
        assert data["data"]["message"] == "Testing..."

    def test_step_start_message(self, protocol):
        """Test step start message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.step_start("init_step", 1, 3, "Initialize hardware")
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.STEP_START.value
        assert data["data"]["step"] == "init_step"
        assert data["data"]["index"] == 1
        assert data["data"]["total"] == 3
        assert data["data"]["description"] == "Initialize hardware"

    def test_step_complete_message(self, protocol):
        """Test step complete message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.step_complete(
                "test_step",
                1,
                True,
                1.5,
                measurements={"voltage": 3.3},
                data={"extra": "data"},
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.STEP_COMPLETE.value
        assert data["data"]["step"] == "test_step"
        assert data["data"]["index"] == 1
        assert data["data"]["passed"] is True
        assert data["data"]["duration"] == 1.5
        assert data["data"]["measurements"]["voltage"] == 3.3
        assert data["data"]["data"]["extra"] == "data"

    def test_step_complete_with_error(self, protocol):
        """Test step complete with error."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.step_complete(
                "failed_step",
                2,
                False,
                2.0,
                error="Test error occurred",
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["data"]["passed"] is False
        assert data["data"]["error"] == "Test error occurred"

    def test_measurement_message(self, protocol):
        """Test measurement message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.measurement(
                "voltage",
                3.28,
                "V",
                passed=True,
                min_value=3.0,
                max_value=3.6,
                step_name="test_step",
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.MEASUREMENT.value
        assert data["data"]["name"] == "voltage"
        assert data["data"]["value"] == 3.28
        assert data["data"]["unit"] == "V"
        assert data["data"]["passed"] is True
        assert data["data"]["min"] == 3.0
        assert data["data"]["max"] == 3.6
        assert data["data"]["step"] == "test_step"

    def test_error_message(self, protocol):
        """Test error message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.error(
                "VOLTAGE_LOW",
                "Voltage below minimum threshold",
                step="test_step",
                recoverable=True,
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.ERROR.value
        assert data["data"]["code"] == "VOLTAGE_LOW"
        assert data["data"]["message"] == "Voltage below minimum threshold"
        assert data["data"]["step"] == "test_step"
        assert data["data"]["recoverable"] is True

    def test_sequence_complete_message(self, protocol):
        """Test sequence complete message output."""
        steps = [
            {"name": "step1", "passed": True, "duration": 1.0},
            {"name": "step2", "passed": True, "duration": 2.0},
        ]
        measurements = {"voltage": 3.3, "temperature": 25.0}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.sequence_complete(
                overall_pass=True,
                duration=3.0,
                steps=steps,
                measurements=measurements,
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.SEQUENCE_COMPLETE.value
        assert data["data"]["overall_pass"] is True
        assert data["data"]["duration"] == 3.0
        assert len(data["data"]["steps"]) == 2
        assert data["data"]["measurements"]["voltage"] == 3.3

    def test_sequence_complete_with_error(self, protocol):
        """Test sequence complete with error."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.sequence_complete(
                overall_pass=False,
                duration=1.5,
                steps=[],
                measurements={},
                error="Sequence failed due to hardware error",
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["data"]["overall_pass"] is False
        assert data["data"]["error"] == "Sequence failed due to hardware error"

    def test_input_request_message(self, protocol):
        """Test input request message output."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            protocol.input_request(
                request_id="input-1",
                prompt="Enter serial number:",
                input_type="text",
                timeout=60.0,
            )
            output = mock_stdout.getvalue().strip()

        data = json.loads(output)
        assert data["type"] == MessageType.INPUT_REQUEST.value
        assert data["data"]["id"] == "input-1"
        assert data["data"]["prompt"] == "Enter serial number:"
        assert data["data"]["input_type"] == "text"
        assert data["data"]["timeout"] == 60.0


class TestMessageType:
    """Tests for MessageType enum."""

    def test_message_types(self):
        """Test all message types are defined."""
        assert MessageType.LOG.value == "log"
        assert MessageType.STATUS.value == "status"
        assert MessageType.STEP_START.value == "step_start"
        assert MessageType.STEP_COMPLETE.value == "step_complete"
        assert MessageType.SEQUENCE_COMPLETE.value == "sequence_complete"
        assert MessageType.MEASUREMENT.value == "measurement"
        assert MessageType.ERROR.value == "error"
        assert MessageType.INPUT_REQUEST.value == "input_request"
