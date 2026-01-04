"""
Unit tests for SDK runner utilities.
"""

import asyncio
import time

import pytest

from station_service.sdk.exceptions import TimeoutError as SDKTimeoutError
from station_service.sdk.runner import (
    AsyncStepTimer,
    StepTimer,
    format_duration,
    run_with_retry,
    run_with_timeout,
    validate_measurement,
)


# ============================================================================
# Tests for run_with_timeout
# ============================================================================


class TestRunWithTimeout:
    """Tests for run_with_timeout function."""

    @pytest.mark.asyncio
    async def test_success_within_timeout(self):
        """Test successful completion within timeout."""

        async def fast_operation():
            await asyncio.sleep(0.01)
            return "success"

        result = await run_with_timeout(fast_operation, timeout=1.0)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Test timeout exception when exceeded."""

        async def slow_operation():
            await asyncio.sleep(10.0)
            return "never"

        with pytest.raises(SDKTimeoutError) as exc_info:
            await run_with_timeout(slow_operation, timeout=0.1)

        assert "timed out" in str(exc_info.value)
        assert exc_info.value.timeout_seconds == 0.1

    @pytest.mark.asyncio
    async def test_with_arguments(self):
        """Test passing arguments to coroutine."""

        async def add_numbers(a, b, c=0):
            return a + b + c

        result = await run_with_timeout(add_numbers, 1.0, 1, 2, c=3)
        assert result == 6

    @pytest.mark.asyncio
    async def test_exception_propagation(self):
        """Test that exceptions from coroutine are propagated."""

        async def failing_operation():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await run_with_timeout(failing_operation, timeout=1.0)


# ============================================================================
# Tests for run_with_retry
# ============================================================================


class TestRunWithRetry:
    """Tests for run_with_retry function."""

    @pytest.mark.asyncio
    async def test_success_first_attempt(self):
        """Test successful completion on first attempt."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await run_with_retry(operation, max_retries=3)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        """Test success after failed attempts."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await run_with_retry(
            operation, max_retries=3, retry_delay=0.01
        )

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_all_retries_failed(self):
        """Test exception when all retries fail."""

        async def failing_operation():
            raise ValueError("Persistent failure")

        with pytest.raises(ValueError, match="Persistent failure"):
            await run_with_retry(
                failing_operation, max_retries=2, retry_delay=0.01
            )

    @pytest.mark.asyncio
    async def test_specific_exception_types(self):
        """Test retry only on specific exception types."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Should retry")
            return "success"

        result = await run_with_retry(
            operation,
            max_retries=3,
            retry_delay=0.01,
            exceptions=(RuntimeError,),
        )

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_non_matching_exception_not_retried(self):
        """Test non-matching exceptions are not retried."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            raise TypeError("Should not retry")

        with pytest.raises(TypeError):
            await run_with_retry(
                operation,
                max_retries=3,
                retry_delay=0.01,
                exceptions=(ValueError,),
            )

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_with_arguments(self):
        """Test passing arguments through retry."""

        async def multiply(a, b):
            return a * b

        result = await run_with_retry(multiply, max_retries=1, a=3, b=4)
        assert result == 12


# ============================================================================
# Tests for StepTimer
# ============================================================================


class TestStepTimer:
    """Tests for StepTimer class."""

    def test_basic_timing(self):
        """Test basic timing functionality."""
        with StepTimer() as timer:
            time.sleep(0.1)

        assert timer.duration >= 0.1
        assert timer.duration < 0.2

    def test_duration_before_entry(self):
        """Test duration returns 0 before context entry."""
        timer = StepTimer()
        assert timer.duration == 0.0

    def test_duration_during_execution(self):
        """Test duration during execution."""
        with StepTimer() as timer:
            time.sleep(0.05)
            mid_duration = timer.duration
            time.sleep(0.05)

        assert mid_duration >= 0.05
        assert timer.duration >= 0.1

    def test_start_and_end_times(self):
        """Test start and end time recording."""
        timer = StepTimer()
        assert timer.start_time is None
        assert timer.end_time is None

        with timer:
            assert timer.start_time is not None
            assert timer.end_time is None

        assert timer.end_time is not None


# ============================================================================
# Tests for AsyncStepTimer
# ============================================================================


class TestAsyncStepTimer:
    """Tests for AsyncStepTimer class."""

    @pytest.mark.asyncio
    async def test_basic_timing(self):
        """Test basic async timing functionality."""
        async with AsyncStepTimer() as timer:
            await asyncio.sleep(0.1)

        assert timer.duration >= 0.1
        assert timer.duration < 0.2

    @pytest.mark.asyncio
    async def test_duration_before_entry(self):
        """Test duration returns 0 before context entry."""
        timer = AsyncStepTimer()
        assert timer.duration == 0.0

    @pytest.mark.asyncio
    async def test_duration_during_execution(self):
        """Test duration during async execution."""
        async with AsyncStepTimer() as timer:
            await asyncio.sleep(0.05)
            mid_duration = timer.duration
            await asyncio.sleep(0.05)

        assert mid_duration >= 0.05
        assert timer.duration >= 0.1


# ============================================================================
# Tests for validate_measurement
# ============================================================================


class TestValidateMeasurement:
    """Tests for validate_measurement function."""

    def test_within_range(self):
        """Test value within range."""
        assert validate_measurement(5.0, min_value=0.0, max_value=10.0) is True

    def test_below_minimum(self):
        """Test value below minimum."""
        assert validate_measurement(-1.0, min_value=0.0, max_value=10.0) is False

    def test_above_maximum(self):
        """Test value above maximum."""
        assert validate_measurement(11.0, min_value=0.0, max_value=10.0) is False

    def test_at_minimum(self):
        """Test value at minimum boundary."""
        assert validate_measurement(0.0, min_value=0.0, max_value=10.0) is True

    def test_at_maximum(self):
        """Test value at maximum boundary."""
        assert validate_measurement(10.0, min_value=0.0, max_value=10.0) is True

    def test_no_limits(self):
        """Test with no limits specified."""
        assert validate_measurement(float("inf")) is True
        assert validate_measurement(float("-inf")) is True

    def test_only_minimum(self):
        """Test with only minimum limit."""
        assert validate_measurement(5.0, min_value=0.0) is True
        assert validate_measurement(-1.0, min_value=0.0) is False

    def test_only_maximum(self):
        """Test with only maximum limit."""
        assert validate_measurement(5.0, max_value=10.0) is True
        assert validate_measurement(11.0, max_value=10.0) is False


# ============================================================================
# Tests for format_duration
# ============================================================================


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_seconds(self):
        """Test formatting seconds."""
        assert format_duration(45.2) == "45.2s"
        assert format_duration(0.5) == "0.5s"
        assert format_duration(59.9) == "59.9s"

    def test_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        assert format_duration(60) == "1m 0s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(125) == "2m 5s"
        assert format_duration(3599) == "59m 59s"

    def test_hours_and_minutes(self):
        """Test formatting hours and minutes."""
        assert format_duration(3600) == "1h 0m"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(7200) == "2h 0m"
        assert format_duration(5400) == "1h 30m"

    def test_zero_duration(self):
        """Test zero duration."""
        assert format_duration(0) == "0.0s"

    def test_fractional_seconds(self):
        """Test fractional second precision."""
        assert format_duration(1.234) == "1.2s"
        assert format_duration(0.01) == "0.0s"
