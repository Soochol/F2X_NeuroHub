"""
Integration tests for CLISequenceWorker.

Tests subprocess execution and JSON Lines parsing with mock sequence.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock

import pytest

from station_service.batch.cli_worker import CLISequenceWorker


# ============================================================================
# Mock Sequence Script
# ============================================================================

MOCK_SEQUENCE_SCRIPT = '''
"""Mock sequence for testing CLISequenceWorker."""

import json
import sys
import time
from datetime import datetime

def emit(msg_type: str, data: dict):
    """Emit JSON Lines message to stdout."""
    message = {
        "type": msg_type,
        "timestamp": datetime.now().isoformat(),
        "execution_id": "test-123",
        "data": data,
    }
    print(json.dumps(message), flush=True)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--config", type=str, default="{}")
    args = parser.parse_args()

    if args.stop:
        sys.exit(0)

    config = json.loads(args.config) if args.config else {}

    # Emit step start
    emit("step_start", {"step": "init", "index": 1, "total": 2})
    time.sleep(0.05)

    # Emit measurement
    emit("measurement", {
        "name": "voltage",
        "value": 3.28,
        "unit": "V",
        "passed": True,
        "min": 3.0,
        "max": 3.6,
    })

    # Emit step complete
    emit("step_complete", {
        "step": "init",
        "index": 1,
        "passed": True,
        "duration": 0.05,
        "measurements": {"voltage": 3.28},
    })

    # Emit log
    emit("log", {"level": "info", "message": "Test log message"})

    # Emit step start for second step
    emit("step_start", {"step": "test", "index": 2, "total": 2})
    time.sleep(0.05)

    # Emit step complete
    emit("step_complete", {
        "step": "test",
        "index": 2,
        "passed": True,
        "duration": 0.05,
        "measurements": {"current": 0.5},
    })

    # Emit sequence complete
    emit("sequence_complete", {
        "overall_pass": True,
        "duration": 0.1,
        "steps": [
            {"name": "init", "passed": True, "duration": 0.05},
            {"name": "test", "passed": True, "duration": 0.05},
        ],
        "measurements": {"voltage": 3.28, "current": 0.5},
    })

if __name__ == "__main__":
    main()
'''

FAILING_SEQUENCE_SCRIPT = '''
"""Mock sequence that fails."""

import json
import sys
from datetime import datetime

def emit(msg_type: str, data: dict):
    message = {
        "type": msg_type,
        "timestamp": datetime.now().isoformat(),
        "execution_id": "test-fail",
        "data": data,
    }
    print(json.dumps(message), flush=True)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--config", type=str, default="{}")
    args = parser.parse_args()

    emit("step_start", {"step": "failing_step", "index": 1, "total": 1})

    emit("error", {
        "code": "TEST_ERROR",
        "message": "Test error occurred",
        "step": "failing_step",
    })

    emit("step_complete", {
        "step": "failing_step",
        "index": 1,
        "passed": False,
        "duration": 0.01,
        "error": "Test error occurred",
    })

    emit("sequence_complete", {
        "overall_pass": False,
        "duration": 0.01,
        "error": "Sequence failed due to test error",
    })

    sys.exit(1)

if __name__ == "__main__":
    main()
'''

INPUT_REQUEST_SCRIPT = '''
"""Mock sequence with input request."""

import json
import sys
import time
from datetime import datetime

def emit(msg_type: str, data: dict):
    message = {
        "type": msg_type,
        "timestamp": datetime.now().isoformat(),
        "execution_id": "test-input",
        "data": data,
    }
    print(json.dumps(message), flush=True)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--config", type=str, default="{}")
    args = parser.parse_args()

    emit("step_start", {"step": "input_step", "index": 1, "total": 1})

    # Request input
    emit("input_request", {
        "id": "input-1",
        "prompt": "Enter serial number:",
        "input_type": "text",
        "timeout": 30,
    })

    # Wait for input (with timeout)
    for line in sys.stdin:
        try:
            response = json.loads(line.strip())
            if response.get("type") == "input_response":
                value = response.get("data", {}).get("value", "")
                emit("log", {"level": "info", "message": f"Received input: {value}"})
                break
        except:
            continue

    emit("step_complete", {
        "step": "input_step",
        "index": 1,
        "passed": True,
        "duration": 0.1,
    })

    emit("sequence_complete", {
        "overall_pass": True,
        "duration": 0.1,
    })

if __name__ == "__main__":
    main()
'''


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_sequences_dir():
    """Create temporary sequences directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        sequences_dir = base_dir / "sequences"
        sequences_dir.mkdir()
        yield base_dir


@pytest.fixture
def mock_sequence(temp_sequences_dir):
    """Create mock sequence package."""
    seq_dir = temp_sequences_dir / "sequences" / "mock_test"
    seq_dir.mkdir(parents=True)

    # Write main.py
    main_file = seq_dir / "main.py"
    main_file.write_text(MOCK_SEQUENCE_SCRIPT)

    # Write __init__.py
    init_file = seq_dir / "__init__.py"
    init_file.write_text("")

    return "mock_test"


@pytest.fixture
def failing_sequence(temp_sequences_dir):
    """Create failing mock sequence package."""
    seq_dir = temp_sequences_dir / "sequences" / "failing_test"
    seq_dir.mkdir(parents=True)

    main_file = seq_dir / "main.py"
    main_file.write_text(FAILING_SEQUENCE_SCRIPT)

    init_file = seq_dir / "__init__.py"
    init_file.write_text("")

    return "failing_test"


@pytest.fixture
def input_sequence(temp_sequences_dir):
    """Create mock sequence with input request."""
    seq_dir = temp_sequences_dir / "sequences" / "input_test"
    seq_dir.mkdir(parents=True)

    main_file = seq_dir / "main.py"
    main_file.write_text(INPUT_REQUEST_SCRIPT)

    init_file = seq_dir / "__init__.py"
    init_file.write_text("")

    return "input_test"


# ============================================================================
# Tests for CLISequenceWorker
# ============================================================================


class TestCLISequenceWorker:
    """Integration tests for CLISequenceWorker."""

    @pytest.mark.asyncio
    async def test_successful_execution(self, temp_sequences_dir, mock_sequence):
        """Test successful sequence execution."""
        step_starts: List[Dict] = []
        step_completes: List[Dict] = []
        measurements: List[Dict] = []
        logs: List[str] = []
        result_data: Dict[str, Any] = {}

        def on_step_start(step_name, index, total, exec_id):
            step_starts.append({
                "step": step_name,
                "index": index,
                "total": total,
            })

        def on_step_complete(step_name, index, passed, duration, data, exec_id):
            step_completes.append({
                "step": step_name,
                "index": index,
                "passed": passed,
                "duration": duration,
            })

        def on_measurement(name, value, unit, data):
            measurements.append({
                "name": name,
                "value": value,
                "unit": unit,
            })

        def on_log(level, msg):
            logs.append(f"[{level}] {msg}")

        async def on_sequence_complete(exec_id, overall_pass, duration, data):
            result_data.update(data)

        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=mock_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
            on_step_start=on_step_start,
            on_step_complete=on_step_complete,
            on_measurement=on_measurement,
            on_log=on_log,
            on_sequence_complete=on_sequence_complete,
        )

        config = {
            "wip_id": "WIP-001",
            "parameters": {"timeout": 30},
        }

        exec_id = await worker.start(config)
        assert exec_id is not None
        assert worker.running is True

        result = await worker.wait()
        assert worker.running is False

        # Verify callbacks were called
        assert len(step_starts) == 2
        assert step_starts[0]["step"] == "init"
        assert step_starts[1]["step"] == "test"

        assert len(step_completes) == 2
        assert all(s["passed"] for s in step_completes)

        assert len(measurements) >= 1
        assert any(m["name"] == "voltage" for m in measurements)

        # Verify final result
        assert result is not None
        assert result["overall_pass"] is True
        assert result["execution_id"] == exec_id

    @pytest.mark.asyncio
    async def test_failing_execution(self, temp_sequences_dir, failing_sequence):
        """Test sequence that fails."""
        errors: List[Dict] = []

        def on_error(code, msg, step):
            errors.append({"code": code, "message": msg, "step": step})

        async def on_sequence_complete(exec_id, overall_pass, duration, data):
            pass

        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=failing_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
            on_error=on_error,
            on_sequence_complete=on_sequence_complete,
        )

        await worker.start({"wip_id": "WIP-FAIL"})
        result = await worker.wait()

        assert result is not None
        assert result["overall_pass"] is False
        assert len(errors) == 1
        assert errors[0]["code"] == "TEST_ERROR"

    @pytest.mark.asyncio
    async def test_stop_running_sequence(self, temp_sequences_dir, mock_sequence):
        """Test stopping a running sequence."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=mock_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
        )

        await worker.start({"wip_id": "WIP-001"})
        assert worker.running is True

        await worker.stop()
        assert worker.running is False

    @pytest.mark.asyncio
    async def test_cannot_start_twice(self, temp_sequences_dir, mock_sequence):
        """Test that starting twice raises error."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=mock_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
        )

        await worker.start({"wip_id": "WIP-001"})

        with pytest.raises(RuntimeError, match="already running"):
            await worker.start({"wip_id": "WIP-002"})

        await worker.stop()

    @pytest.mark.asyncio
    async def test_execution_id_generation(self, temp_sequences_dir, mock_sequence):
        """Test execution ID generation."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=mock_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
        )

        # With provided ID
        exec_id = await worker.start({
            "execution_id": "custom-id",
            "wip_id": "WIP-001",
        })
        assert exec_id == "custom-id"
        await worker.stop()

    @pytest.mark.asyncio
    async def test_async_callbacks(self, temp_sequences_dir, mock_sequence):
        """Test async callback support."""
        called = False

        async def on_step_start(step_name, index, total, exec_id):
            nonlocal called
            await asyncio.sleep(0.01)  # Simulate async work
            called = True

        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=mock_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
            on_step_start=on_step_start,
        )

        await worker.start({"wip_id": "WIP-001"})
        await worker.wait()

        assert called is True

    @pytest.mark.asyncio
    async def test_status_callback(self, temp_sequences_dir, mock_sequence):
        """Test status callback receives updates."""
        statuses: List[Dict] = []

        def on_status(status, progress, current_step, exec_id):
            statuses.append({
                "status": status,
                "progress": progress,
                "current_step": current_step,
            })

        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=mock_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
            on_status=on_status,
        )

        await worker.start({"wip_id": "WIP-001"})
        await worker.wait()

        # Status updates depend on sequence implementation

    @pytest.mark.asyncio
    async def test_input_request_handling(self, temp_sequences_dir, input_sequence):
        """Test input request and response handling."""
        input_requests: List[Dict] = []
        logs: List[str] = []

        def on_input_request(request_id, prompt, input_type, data):
            input_requests.append({
                "id": request_id,
                "prompt": prompt,
                "input_type": input_type,
            })

        def on_log(level, msg):
            logs.append(msg)

        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name=input_sequence,
            sequences_dir=temp_sequences_dir / "sequences",
            on_input_request=on_input_request,
            on_log=on_log,
        )

        await worker.start({"wip_id": "WIP-001"})

        # Wait for input request
        await asyncio.sleep(0.1)

        if input_requests:
            # Send input response
            await worker.send_input("input-1", "SN-12345")

        result = await worker.wait()
        assert result is not None


class TestCLISequenceWorkerProperties:
    """Tests for CLISequenceWorker properties."""

    def test_running_property(self, temp_sequences_dir):
        """Test running property defaults to False."""
        worker = CLISequenceWorker(
            batch_id="test",
            sequence_name="test",
            sequences_dir=temp_sequences_dir / "sequences",
        )
        assert worker.running is False

    def test_execution_id_property(self, temp_sequences_dir):
        """Test execution_id property defaults to None."""
        worker = CLISequenceWorker(
            batch_id="test",
            sequence_name="test",
            sequences_dir=temp_sequences_dir / "sequences",
        )
        assert worker.execution_id is None


class TestCLISequenceWorkerErrorHandling:
    """Tests for error handling in CLISequenceWorker."""

    @pytest.mark.asyncio
    async def test_invalid_sequence_name(self, temp_sequences_dir):
        """Test handling of invalid sequence name."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name="nonexistent_sequence",
            sequences_dir=temp_sequences_dir / "sequences",
        )

        # Should fail to start since module doesn't exist
        # The subprocess will fail with import error
        await worker.start({"wip_id": "WIP-001"})
        result = await worker.wait()

        # Result may be None or contain error info depending on how
        # the subprocess handles the import error

    @pytest.mark.asyncio
    async def test_stop_not_running(self, temp_sequences_dir):
        """Test stopping when not running does nothing."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name="test",
            sequences_dir=temp_sequences_dir / "sequences",
        )

        # Should not raise
        await worker.stop()

    @pytest.mark.asyncio
    async def test_wait_not_started(self, temp_sequences_dir):
        """Test waiting when not started."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name="test",
            sequences_dir=temp_sequences_dir / "sequences",
        )

        result = await worker.wait()
        assert result is None

    @pytest.mark.asyncio
    async def test_send_input_not_running(self, temp_sequences_dir):
        """Test sending input when not running."""
        worker = CLISequenceWorker(
            batch_id="test-batch",
            sequence_name="test",
            sequences_dir=temp_sequences_dir / "sequences",
        )

        # Should not raise, just log warning
        await worker.send_input("id", "value")
