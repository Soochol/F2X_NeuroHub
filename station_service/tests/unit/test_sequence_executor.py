"""
Unit tests for the SequenceExecutor class.

Tests step execution, retry logic, timeouts, and cleanup handling.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from station_service.sequence.decorators import StepMeta, step
from station_service.sequence.executor import ExecutionResult, SequenceExecutor, StepResult
from station_service.sequence.exceptions import TestFailure, TestSkipped


class MockSequence:
    """A mock sequence for testing."""

    name = "mock_sequence"
    version = "1.0.0"

    def __init__(self, step_results: dict = None):
        self._step_results = step_results or {}

    @step(order=1, timeout=5.0)
    async def step_one(self):
        """First step."""
        return self._step_results.get("step_one", {"value": 1})

    @step(order=2, timeout=5.0, retry=2)
    async def step_two(self):
        """Second step with retry."""
        result = self._step_results.get("step_two")
        if isinstance(result, Exception):
            raise result
        return result or {"value": 2}

    @step(order=3, timeout=5.0, condition="run_step_three")
    async def step_three(self):
        """Conditional step."""
        return {"value": 3}

    @step(order=100, cleanup=True, timeout=5.0)
    async def cleanup_step(self):
        """Cleanup step."""
        return {"cleaned": True}


class TestSequenceExecutor:
    """Test suite for SequenceExecutor."""

    @pytest.fixture
    def mock_sequence(self) -> MockSequence:
        """Create a mock sequence instance."""
        return MockSequence()

    @pytest.fixture
    def executor(self, mock_sequence: MockSequence) -> SequenceExecutor:
        """Create an executor with mock sequence."""
        return SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={"run_step_three": True},
        )

    # ============================================================
    # Basic Execution Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_run_executes_all_steps(self, executor: SequenceExecutor):
        """Test that run() executes all regular steps."""
        result = await executor.run()

        assert result.status == "completed"
        assert result.overall_pass is True
        # Should have step_one, step_two, step_three, and cleanup
        assert len(result.steps) == 4

    @pytest.mark.asyncio
    async def test_run_returns_execution_result(self, executor: SequenceExecutor):
        """Test that run() returns proper ExecutionResult."""
        result = await executor.run()

        assert isinstance(result, ExecutionResult)
        assert result.sequence_name == "mock_sequence"
        assert result.sequence_version == "1.0.0"
        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.duration is not None
        assert result.duration > 0

    @pytest.mark.asyncio
    async def test_step_results_contain_details(self, executor: SequenceExecutor):
        """Test that step results contain all required details."""
        result = await executor.run()

        step_one = result.steps[0]
        assert step_one.name == "step_one"
        assert step_one.order == 1
        assert step_one.status == "completed"
        assert step_one.passed is True
        assert step_one.duration is not None
        assert step_one.result == {"value": 1}

    # ============================================================
    # Conditional Step Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_conditional_step_runs_when_true(self, mock_sequence: MockSequence):
        """Test conditional step runs when condition is true."""
        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={"run_step_three": True},
        )

        result = await executor.run()

        step_three = next(s for s in result.steps if s.name == "step_three")
        assert step_three.status == "completed"
        assert step_three.passed is True

    @pytest.mark.asyncio
    async def test_conditional_step_skipped_when_false(self, mock_sequence: MockSequence):
        """Test conditional step is skipped when condition is false."""
        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={"run_step_three": False},
        )

        result = await executor.run()

        step_three = next(s for s in result.steps if s.name == "step_three")
        assert step_three.status == "skipped"
        assert step_three.passed is True  # Skipped is considered pass

    @pytest.mark.asyncio
    async def test_conditional_step_skipped_when_missing(self, mock_sequence: MockSequence):
        """Test conditional step is skipped when parameter missing."""
        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={},  # No run_step_three
        )

        result = await executor.run()

        step_three = next(s for s in result.steps if s.name == "step_three")
        assert step_three.status == "skipped"

    # ============================================================
    # Failure Handling Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_step_failure_stops_execution(self, mock_sequence: MockSequence):
        """Test that step failure stops regular execution."""
        mock_sequence._step_results["step_two"] = TestFailure("Test failed")

        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={"run_step_three": True},
        )

        result = await executor.run()

        assert result.status == "failed"
        assert result.overall_pass is False

        # step_one should pass
        step_one = next(s for s in result.steps if s.name == "step_one")
        assert step_one.passed is True

        # step_two should fail
        step_two = next(s for s in result.steps if s.name == "step_two")
        assert step_two.passed is False
        assert step_two.error is not None

    @pytest.mark.asyncio
    async def test_cleanup_runs_after_failure(self, mock_sequence: MockSequence):
        """Test that cleanup steps run even after failure."""
        mock_sequence._step_results["step_one"] = TestFailure("Failed early")

        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={},
        )

        result = await executor.run()

        # Cleanup should still run
        cleanup = next((s for s in result.steps if s.name == "cleanup_step"), None)
        assert cleanup is not None
        assert cleanup.status == "completed"

    # ============================================================
    # Retry Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_step_retry_on_exception(self):
        """Test that steps retry on exception."""
        call_count = 0

        class RetrySequence:
            name = "retry_sequence"
            version = "1.0.0"

            @step(order=1, timeout=5.0, retry=2)
            async def flaky_step(self):
                nonlocal call_count
                call_count += 1
                if call_count < 3:  # Fail first 2 times
                    raise RuntimeError("Temporary error")
                return {"success": True}

        executor = SequenceExecutor(
            sequence_instance=RetrySequence(),
            parameters={},
        )

        result = await executor.run()

        assert call_count == 3  # Initial + 2 retries
        assert result.overall_pass is True

    @pytest.mark.asyncio
    async def test_step_fails_after_max_retries(self):
        """Test that step fails after exhausting retries."""

        class AlwaysFailSequence:
            name = "fail_sequence"
            version = "1.0.0"

            @step(order=1, timeout=5.0, retry=2)
            async def always_fail(self):
                raise RuntimeError("Always fails")

        executor = SequenceExecutor(
            sequence_instance=AlwaysFailSequence(),
            parameters={},
        )

        result = await executor.run()

        assert result.overall_pass is False
        assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_test_failure_does_not_retry(self):
        """Test that TestFailure does not trigger retry."""
        call_count = 0

        class TestFailureSequence:
            name = "test_failure_sequence"
            version = "1.0.0"

            @step(order=1, timeout=5.0, retry=2)
            async def fail_test(self):
                nonlocal call_count
                call_count += 1
                raise TestFailure("Test assertion failed")

        executor = SequenceExecutor(
            sequence_instance=TestFailureSequence(),
            parameters={},
        )

        result = await executor.run()

        # TestFailure should not trigger retry
        assert call_count == 1
        assert result.overall_pass is False

    # ============================================================
    # Timeout Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_step_timeout(self):
        """Test that step times out correctly."""

        class SlowSequence:
            name = "slow_sequence"
            version = "1.0.0"

            @step(order=1, timeout=0.1)  # 100ms timeout
            async def slow_step(self):
                await asyncio.sleep(1.0)  # Takes 1 second
                return {"done": True}

        executor = SequenceExecutor(
            sequence_instance=SlowSequence(),
            parameters={},
        )

        result = await executor.run()

        assert result.overall_pass is False
        step_result = result.steps[0]
        assert step_result.status == "failed"
        assert "timeout" in step_result.error.lower()

    # ============================================================
    # Stop Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_stop_halts_execution(self):
        """Test that stop() halts execution after current step."""
        step_count = 0

        class StoppableSequence:
            name = "stoppable"
            version = "1.0.0"

            @step(order=1, timeout=5.0)
            async def step_one(self):
                nonlocal step_count
                step_count += 1
                return {}

            @step(order=2, timeout=5.0)
            async def step_two(self):
                nonlocal step_count
                step_count += 1
                return {}

            @step(order=3, timeout=5.0)
            async def step_three(self):
                nonlocal step_count
                step_count += 1
                return {}

        executor = SequenceExecutor(
            sequence_instance=StoppableSequence(),
            parameters={},
        )

        # Stop after first step
        async def stop_after_first():
            await asyncio.sleep(0.05)
            await executor.stop()

        # Run both concurrently
        await asyncio.gather(executor.run(), stop_after_first())

        # Should have stopped after 1 or 2 steps
        assert step_count < 3

    def test_is_stopped_property(self, executor: SequenceExecutor):
        """Test is_stopped property."""
        assert executor.is_stopped is False

    # ============================================================
    # Callback Tests
    # ============================================================

    @pytest.mark.asyncio
    async def test_on_step_start_callback(self, mock_sequence: MockSequence):
        """Test on_step_start callback is called."""
        callback = MagicMock()

        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={"run_step_three": True},
            on_step_start=callback,
        )

        await executor.run()

        # Should be called for each step
        assert callback.call_count >= 3

    @pytest.mark.asyncio
    async def test_on_step_complete_callback(self, mock_sequence: MockSequence):
        """Test on_step_complete callback is called."""
        callback = MagicMock()

        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={"run_step_three": True},
            on_step_complete=callback,
        )

        await executor.run()

        # Should be called for each step
        assert callback.call_count >= 3

    @pytest.mark.asyncio
    async def test_on_log_callback(self, mock_sequence: MockSequence):
        """Test on_log callback is called."""
        callback = MagicMock()

        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={},
            on_log=callback,
        )

        await executor.run()

        # Should have some log messages
        assert callback.call_count > 0

    @pytest.mark.asyncio
    async def test_on_error_callback(self, mock_sequence: MockSequence):
        """Test on_error callback is called on failure."""
        mock_sequence._step_results["step_two"] = RuntimeError("Test error")
        callback = MagicMock()

        executor = SequenceExecutor(
            sequence_instance=mock_sequence,
            parameters={},
            on_error=callback,
        )

        await executor.run()

        # Should have been called for the error
        assert callback.call_count > 0


class TestStepResult:
    """Test suite for StepResult dataclass."""

    def test_to_dict(self):
        """Test StepResult.to_dict() method."""
        result = StepResult(
            name="test_step",
            order=1,
            status="completed",
            passed=True,
            duration=1.5,
            result={"value": 42},
        )

        d = result.to_dict()

        assert d["name"] == "test_step"
        assert d["order"] == 1
        assert d["status"] == "completed"
        assert d["pass"] is True
        assert d["duration"] == 1.5
        assert d["result"] == {"value": 42}


class TestExecutionResult:
    """Test suite for ExecutionResult dataclass."""

    def test_to_dict(self):
        """Test ExecutionResult.to_dict() method."""
        result = ExecutionResult(
            sequence_name="test_sequence",
            sequence_version="1.0.0",
            status="completed",
            overall_pass=True,
            started_at=datetime.now(),
            parameters={"key": "value"},
            steps=[],
        )

        d = result.to_dict()

        assert d["sequence_name"] == "test_sequence"
        assert d["sequence_version"] == "1.0.0"
        assert d["status"] == "completed"
        assert d["overall_pass"] is True
        assert d["parameters"] == {"key": "value"}
        assert d["steps"] == []
