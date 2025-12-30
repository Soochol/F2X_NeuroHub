"""Unit tests for ExampleTestSequence."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sequences.example_test.sequence import ExampleTestSequence
from sequences.example_test.drivers.mock_dmm import MockDMM


class TestExampleTestSequenceInit:
    """Tests for ExampleTestSequence initialization."""

    def test_init_with_defaults(self) -> None:
        """Test initialization with default values."""
        seq = ExampleTestSequence()

        assert seq.voltage_limit == 5.0
        assert seq.test_count == 3
        assert seq.dmm is not None
        assert isinstance(seq.dmm, MockDMM)
        assert seq.results == []

    def test_init_with_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        params = {"voltage_limit": 10.0, "test_count": 5}
        seq = ExampleTestSequence(parameters=params)

        assert seq.voltage_limit == 10.0
        assert seq.test_count == 5

    def test_init_with_hardware(self) -> None:
        """Test initialization with provided hardware."""
        mock_dmm = MockDMM(config={"port": "/dev/custom"})
        hardware = {"dmm": mock_dmm}
        seq = ExampleTestSequence(hardware=hardware)

        assert seq.dmm is mock_dmm


class TestExampleTestSequenceSteps:
    """Tests for ExampleTestSequence step methods."""

    @pytest.fixture
    def sequence(self) -> ExampleTestSequence:
        """Create a test sequence instance."""
        return ExampleTestSequence(
            parameters={"voltage_limit": 5.0, "test_count": 3}
        )

    @pytest.mark.asyncio
    async def test_initialize_success(self, sequence: ExampleTestSequence) -> None:
        """Test successful initialization step."""
        result = await sequence.initialize()

        assert result["step"] == "initialize"
        assert result["status"] == "passed"
        assert "dmm_idn" in result["data"]
        assert result["data"]["dmm_reset"] is True
        assert result["data"]["voltage_limit"] == 5.0
        assert result["data"]["test_count"] == 3

    @pytest.mark.asyncio
    async def test_initialize_dmm_connection_failure(
        self, sequence: ExampleTestSequence
    ) -> None:
        """Test initialization when DMM connection fails."""
        sequence.dmm = AsyncMock()
        sequence.dmm.connect = AsyncMock(return_value=False)

        result = await sequence.initialize()

        assert result["status"] == "failed"
        assert "error" in result
        assert "connect" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_measure_voltage_success(
        self, sequence: ExampleTestSequence
    ) -> None:
        """Test successful voltage measurement step."""
        # Initialize first
        await sequence.initialize()

        result = await sequence.measure_voltage()

        assert result["step"] == "measure_voltage"
        assert result["status"] == "passed"
        assert len(result["data"]["measurements"]) == 3
        assert "average" in result["data"]
        assert "min" in result["data"]
        assert "max" in result["data"]

    @pytest.mark.asyncio
    async def test_measure_voltage_exceeds_limit(
        self, sequence: ExampleTestSequence
    ) -> None:
        """Test voltage measurement that exceeds limit."""
        # Set a low limit
        sequence.voltage_limit = 0.1
        await sequence.initialize()

        result = await sequence.measure_voltage()

        assert result["status"] == "failed"
        assert "exceeds limit" in result["error"]

    @pytest.mark.asyncio
    async def test_measure_voltage_no_dmm(
        self, sequence: ExampleTestSequence
    ) -> None:
        """Test voltage measurement when DMM is not available."""
        sequence.dmm = None

        result = await sequence.measure_voltage()

        assert result["status"] == "failed"
        assert "DMM not available" in result["error"]

    @pytest.mark.asyncio
    async def test_finalize_success(self, sequence: ExampleTestSequence) -> None:
        """Test successful finalization step."""
        await sequence.initialize()

        result = await sequence.finalize()

        assert result["step"] == "finalize"
        assert result["status"] == "passed"
        assert result["data"]["cleanup_completed"] is True

    @pytest.mark.asyncio
    async def test_finalize_without_connection(
        self, sequence: ExampleTestSequence
    ) -> None:
        """Test finalization when not connected."""
        result = await sequence.finalize()

        assert result["status"] == "passed"
        assert result["data"]["cleanup_completed"] is True


class TestExampleTestSequenceIntegration:
    """Integration tests for ExampleTestSequence."""

    @pytest.mark.asyncio
    async def test_full_sequence_execution(self) -> None:
        """Test full sequence execution from init to finalize."""
        seq = ExampleTestSequence(
            parameters={"voltage_limit": 10.0, "test_count": 2}
        )

        # Execute all steps in order
        init_result = await seq.initialize()
        assert init_result["status"] == "passed"

        measure_result = await seq.measure_voltage()
        assert measure_result["status"] == "passed"

        finalize_result = await seq.finalize()
        assert finalize_result["status"] == "passed"

        # Verify results were collected
        assert len(seq.results) == 1

    @pytest.mark.asyncio
    async def test_sequence_with_failure_still_finalizes(self) -> None:
        """Test that finalization runs even after step failure."""
        seq = ExampleTestSequence(
            parameters={"voltage_limit": 0.01, "test_count": 1}
        )

        await seq.initialize()

        # This should fail due to low voltage limit
        measure_result = await seq.measure_voltage()
        assert measure_result["status"] == "failed"

        # Finalization should still work
        finalize_result = await seq.finalize()
        assert finalize_result["status"] == "passed"


class TestSequenceDecorators:
    """Tests for sequence decorator metadata."""

    def test_sequence_has_metadata(self) -> None:
        """Test that sequence class has proper metadata."""
        meta = getattr(ExampleTestSequence, "_sequence_meta", None)
        assert meta is not None
        assert meta.name == "example_test"
        assert meta.version == "1.0.0"

    def test_step_methods_have_metadata(self) -> None:
        """Test that step methods have proper metadata."""
        seq = ExampleTestSequence()

        # Check initialize step
        init_meta = getattr(seq.initialize, "_step_meta", None)
        assert init_meta is not None
        assert init_meta.order == 1
        assert init_meta.timeout == 30.0

        # Check measure_voltage step
        measure_meta = getattr(seq.measure_voltage, "_step_meta", None)
        assert measure_meta is not None
        assert measure_meta.order == 2
        assert measure_meta.retry == 1

        # Check finalize step
        finalize_meta = getattr(seq.finalize, "_step_meta", None)
        assert finalize_meta is not None
        assert finalize_meta.order == 99
        assert finalize_meta.cleanup is True
