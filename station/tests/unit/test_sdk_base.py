"""
Unit tests for SDK SequenceBase class.
"""

import asyncio
import json
from io import StringIO
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from station_service.sdk.base import SequenceBase, StepResult
from station_service.sdk.context import ExecutionContext
from station_service.sdk.exceptions import SetupError, SequenceError, AbortError


# ============================================================================
# Test Fixtures
# ============================================================================


class MockSequence(SequenceBase):
    """Mock sequence for testing."""

    name = "mock_sequence"
    version = "1.0.0"
    description = "Mock test sequence"

    def __init__(self, context, hardware_config=None, parameters=None):
        super().__init__(context, hardware_config, parameters)
        self.setup_called = False
        self.run_called = False
        self.teardown_called = False
        self.should_fail_setup = False
        self.should_fail_run = False
        self.should_abort = False

    async def setup(self) -> None:
        self.setup_called = True
        if self.should_fail_setup:
            raise SetupError("Setup failed: Mock setup failure")

    async def run(self) -> Dict[str, Any]:
        self.run_called = True
        if self.should_abort:
            self.abort("Test abort")
        if self.should_fail_run:
            raise SequenceError("Sequence error: Mock run failure")

        # Emit some test data
        self.emit_step_start("test_step", 1, 2, "Test step")
        self.emit_measurement("voltage", 3.3, "V", passed=True, min_value=3.0, max_value=3.6)
        self.emit_step_complete("test_step", 1, True, 1.5, {"voltage": 3.3})

        return {
            "passed": True,
            "measurements": {"voltage": 3.3},
            "data": {"test": "data"},
        }

    async def teardown(self) -> None:
        self.teardown_called = True


@pytest.fixture
def mock_context():
    """Create a mock execution context."""
    return ExecutionContext(
        execution_id="test-123",
        wip_id="WIP-001",
        sequence_name="mock_sequence",
        sequence_version="1.0.0",
        hardware_config={},
        parameters={"param1": "value1"},
    )


@pytest.fixture
def mock_sequence(mock_context):
    """Create a mock sequence instance."""
    return MockSequence(
        context=mock_context,
        hardware_config={"device": {"port": "/dev/test"}},
        parameters={"param1": "value1", "param2": 42},
    )


# ============================================================================
# Tests for SequenceBase
# ============================================================================


class TestSequenceBase:
    """Tests for SequenceBase class."""

    def test_init(self, mock_sequence, mock_context):
        """Test sequence initialization."""
        assert mock_sequence.context == mock_context
        assert mock_sequence.parameters["param1"] == "value1"
        assert mock_sequence.parameters["param2"] == 42
        assert mock_sequence.hardware_config["device"]["port"] == "/dev/test"

    def test_get_parameter(self, mock_sequence):
        """Test get_parameter method."""
        assert mock_sequence.get_parameter("param1") == "value1"
        assert mock_sequence.get_parameter("param2") == 42
        assert mock_sequence.get_parameter("missing") is None
        assert mock_sequence.get_parameter("missing", "default") == "default"

    def test_get_hardware_config(self, mock_sequence):
        """Test get_hardware_config method."""
        config = mock_sequence.get_hardware_config("device")
        assert config["port"] == "/dev/test"
        assert mock_sequence.get_hardware_config("missing") == {}

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_sequence):
        """Test successful execution."""
        result = await mock_sequence._execute()

        assert mock_sequence.setup_called
        assert mock_sequence.run_called
        assert mock_sequence.teardown_called
        assert result["passed"] is True
        assert "voltage" in result["measurements"]

    @pytest.mark.asyncio
    async def test_execute_setup_failure(self, mock_sequence):
        """Test execution with setup failure."""
        mock_sequence.should_fail_setup = True
        result = await mock_sequence._execute()

        assert mock_sequence.setup_called
        assert not mock_sequence.run_called
        assert mock_sequence.teardown_called  # Teardown should still be called
        assert result["passed"] is False
        assert "Setup failed" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_run_failure(self, mock_sequence):
        """Test execution with run failure."""
        mock_sequence.should_fail_run = True
        result = await mock_sequence._execute()

        assert mock_sequence.setup_called
        assert mock_sequence.run_called
        assert mock_sequence.teardown_called
        assert result["passed"] is False
        assert "Sequence error" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_abort(self, mock_sequence):
        """Test execution with abort."""
        mock_sequence.should_abort = True
        result = await mock_sequence._execute()

        assert mock_sequence.setup_called
        assert mock_sequence.run_called
        assert mock_sequence.teardown_called
        assert result["passed"] is False
        assert "Aborted" in result["error"]


class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_step_result_creation(self):
        """Test StepResult creation."""
        result = StepResult(
            name="test_step",
            index=1,
            passed=True,
            duration=1.5,
            measurements={"voltage": 3.3},
            data={"extra": "data"},
        )

        assert result.name == "test_step"
        assert result.index == 1
        assert result.passed is True
        assert result.duration == 1.5
        assert result.measurements["voltage"] == 3.3
        assert result.data["extra"] == "data"
        assert result.error is None

    def test_step_result_to_dict(self):
        """Test StepResult.to_dict method."""
        result = StepResult(
            name="test_step",
            index=1,
            passed=False,
            duration=2.0,
            error="Test error",
        )

        data = result.to_dict()
        assert data["name"] == "test_step"
        assert data["index"] == 1
        assert data["passed"] is False
        assert data["duration"] == 2.0
        assert data["error"] == "Test error"


class TestSequenceEmitMethods:
    """Tests for sequence emit methods."""

    @pytest.mark.asyncio
    async def test_emit_measurement(self, mock_sequence):
        """Test emit_measurement method."""
        mock_sequence.emit_measurement(
            "temperature",
            25.5,
            "°C",
            passed=True,
            min_value=20.0,
            max_value=30.0,
        )
        # Allow async tasks to complete
        await asyncio.sleep(0)

        assert "temperature" in mock_sequence._measurements
        measurement = mock_sequence._measurements["temperature"]
        # Measurement is a dataclass, access via attributes
        assert measurement.value == 25.5
        assert measurement.unit == "°C"
        assert measurement.passed is True
        assert measurement.min_value == 20.0
        assert measurement.max_value == 30.0

    @pytest.mark.asyncio
    async def test_emit_step_start(self, mock_sequence):
        """Test emit_step_start method."""
        mock_sequence.emit_step_start("test_step", 1, 3, "Test description")
        # Allow async tasks to complete
        await asyncio.sleep(0)

        assert mock_sequence._current_step == "test_step"
        assert mock_sequence._current_step_index == 1
        assert mock_sequence._total_steps == 3

    @pytest.mark.asyncio
    async def test_emit_step_complete(self, mock_sequence):
        """Test emit_step_complete method."""
        mock_sequence.emit_step_start("test_step", 1, 2)
        await asyncio.sleep(0)
        mock_sequence.emit_step_complete(
            "test_step",
            1,
            True,
            1.5,
            measurements={"voltage": 3.3},
        )
        # Allow async tasks to complete
        await asyncio.sleep(0)

        assert len(mock_sequence._step_results) == 1
        result = mock_sequence._step_results[0]
        assert result.name == "test_step"
        assert result.passed is True
        assert result.duration == 1.5
        assert "voltage" in mock_sequence._measurements

    def test_abort(self, mock_sequence):
        """Test abort method."""
        with pytest.raises(AbortError):
            mock_sequence.abort("Test abort reason")

        assert mock_sequence._aborted is True

    def test_check_abort(self, mock_sequence):
        """Test check_abort method."""
        # Should not raise when not aborted
        mock_sequence.check_abort()

        # Should raise when aborted
        mock_sequence._aborted = True
        with pytest.raises(AbortError):
            mock_sequence.check_abort()
