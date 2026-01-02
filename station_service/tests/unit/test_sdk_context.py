"""
Unit tests for SDK ExecutionContext class.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from station_service.sdk.context import ExecutionContext


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "execution_id": "exec-123",
        "wip_id": "WIP-001",
        "batch_id": "BATCH-001",
        "process_id": 1,
        "operator_id": 42,
        "lot_id": "LOT-2024-001",
        "serial_number": "SN-00001",
        "hardware": {
            "power_supply": {"port": "COM1", "baud_rate": 115200},
            "gpio": {"pin_count": 8},
        },
        "parameters": {
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "timeout": 30,
        },
        "sequence_name": "test_sequence",
        "sequence_version": "1.0.0",
        "station_id": "STATION-001",
    }


# ============================================================================
# Tests for ExecutionContext
# ============================================================================


class TestExecutionContext:
    """Tests for ExecutionContext class."""

    def test_default_init(self):
        """Test default initialization."""
        ctx = ExecutionContext()

        assert ctx.execution_id is not None
        assert len(ctx.execution_id) == 8
        assert ctx.wip_id is None
        assert ctx.batch_id is None
        assert ctx.process_id is None
        assert ctx.operator_id is None
        assert ctx.lot_id is None
        assert ctx.serial_number is None
        assert ctx.hardware_config == {}
        assert ctx.parameters == {}
        assert ctx.started_at is None
        assert ctx.completed_at is None
        assert ctx.sequence_name == ""
        assert ctx.sequence_version == ""
        assert ctx.station_id == ""

    def test_init_with_values(self):
        """Test initialization with values."""
        ctx = ExecutionContext(
            execution_id="custom-id",
            wip_id="WIP-123",
            batch_id="BATCH-001",
            process_id=1,
            operator_id=42,
            hardware_config={"device": {"port": "COM1"}},
            parameters={"timeout": 30},
            sequence_name="my_sequence",
            sequence_version="2.0.0",
        )

        assert ctx.execution_id == "custom-id"
        assert ctx.wip_id == "WIP-123"
        assert ctx.batch_id == "BATCH-001"
        assert ctx.process_id == 1
        assert ctx.operator_id == 42
        assert ctx.hardware_config == {"device": {"port": "COM1"}}
        assert ctx.parameters == {"timeout": 30}
        assert ctx.sequence_name == "my_sequence"
        assert ctx.sequence_version == "2.0.0"

    def test_from_config(self, sample_config):
        """Test creation from config dictionary."""
        ctx = ExecutionContext.from_config(sample_config)

        assert ctx.execution_id == "exec-123"
        assert ctx.wip_id == "WIP-001"
        assert ctx.batch_id == "BATCH-001"
        assert ctx.process_id == 1
        assert ctx.operator_id == 42
        assert ctx.lot_id == "LOT-2024-001"
        assert ctx.serial_number == "SN-00001"
        assert ctx.hardware_config == sample_config["hardware"]
        assert ctx.parameters == sample_config["parameters"]
        assert ctx.sequence_name == "test_sequence"
        assert ctx.sequence_version == "1.0.0"
        assert ctx.station_id == "STATION-001"

    def test_from_config_empty(self):
        """Test creation from empty config."""
        ctx = ExecutionContext.from_config({})

        assert ctx.execution_id is not None
        assert ctx.wip_id is None
        assert ctx.hardware_config == {}
        assert ctx.parameters == {}

    def test_from_config_partial(self):
        """Test creation from partial config."""
        config = {
            "wip_id": "WIP-001",
            "parameters": {"timeout": 60},
        }
        ctx = ExecutionContext.from_config(config)

        assert ctx.wip_id == "WIP-001"
        assert ctx.parameters == {"timeout": 60}
        assert ctx.hardware_config == {}

    def test_to_dict(self, sample_config):
        """Test conversion to dictionary."""
        ctx = ExecutionContext.from_config(sample_config)
        ctx.start()
        ctx.complete()

        result = ctx.to_dict()

        assert result["execution_id"] == "exec-123"
        assert result["wip_id"] == "WIP-001"
        assert result["batch_id"] == "BATCH-001"
        assert result["process_id"] == 1
        assert result["operator_id"] == 42
        assert result["lot_id"] == "LOT-2024-001"
        assert result["serial_number"] == "SN-00001"
        assert result["hardware_config"] == sample_config["hardware"]
        assert result["parameters"] == sample_config["parameters"]
        assert result["started_at"] is not None
        assert result["completed_at"] is not None
        assert result["sequence_name"] == "test_sequence"
        assert result["sequence_version"] == "1.0.0"
        assert result["station_id"] == "STATION-001"

    def test_to_dict_no_timestamps(self):
        """Test conversion to dict without timestamps."""
        ctx = ExecutionContext(execution_id="test")
        result = ctx.to_dict()

        assert result["started_at"] is None
        assert result["completed_at"] is None

    def test_start(self):
        """Test start method sets timestamp."""
        ctx = ExecutionContext()
        assert ctx.started_at is None

        ctx.start()

        assert ctx.started_at is not None
        assert isinstance(ctx.started_at, datetime)

    def test_complete(self):
        """Test complete method sets timestamp."""
        ctx = ExecutionContext()
        assert ctx.completed_at is None

        ctx.complete()

        assert ctx.completed_at is not None
        assert isinstance(ctx.completed_at, datetime)

    def test_duration_seconds_not_started(self):
        """Test duration_seconds when not started."""
        ctx = ExecutionContext()
        assert ctx.duration_seconds is None

    def test_duration_seconds_in_progress(self):
        """Test duration_seconds when in progress."""
        ctx = ExecutionContext()
        ctx.start()

        duration = ctx.duration_seconds

        assert duration is not None
        assert duration >= 0

    def test_duration_seconds_completed(self):
        """Test duration_seconds when completed."""
        ctx = ExecutionContext()
        ctx.start()
        ctx.complete()

        duration = ctx.duration_seconds

        assert duration is not None
        assert duration >= 0


class TestExecutionContextTimestamps:
    """Tests for timestamp handling in ExecutionContext."""

    def test_to_dict_timestamp_format(self):
        """Test timestamp ISO format in to_dict."""
        ctx = ExecutionContext()
        ctx.started_at = datetime(2024, 1, 15, 10, 30, 45)
        ctx.completed_at = datetime(2024, 1, 15, 10, 31, 15)

        result = ctx.to_dict()

        assert result["started_at"] == "2024-01-15T10:30:45"
        assert result["completed_at"] == "2024-01-15T10:31:15"

    def test_duration_calculation(self):
        """Test duration calculation accuracy."""
        ctx = ExecutionContext()
        ctx.started_at = datetime(2024, 1, 15, 10, 30, 0)
        ctx.completed_at = datetime(2024, 1, 15, 10, 30, 30)

        assert ctx.duration_seconds == 30.0

    def test_duration_with_microseconds(self):
        """Test duration with microsecond precision."""
        ctx = ExecutionContext()
        ctx.started_at = datetime(2024, 1, 15, 10, 30, 0, 0)
        ctx.completed_at = datetime(2024, 1, 15, 10, 30, 0, 500000)

        assert ctx.duration_seconds == 0.5
