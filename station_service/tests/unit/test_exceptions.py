"""
Unit tests for the exception hierarchy.

Tests exception creation, error codes, and serialization.
"""

import pytest

from station_service.core.exceptions import (
    StationError,
    BatchError,
    BatchNotFoundError,
    BatchAlreadyRunningError,
    BatchNotRunningError,
    BatchProcessError,
    SequenceError,
    SequenceNotFoundError,
    SequenceValidationError,
    SequenceExecutionError,
    HardwareError,
    HardwareConnectionError,
    HardwareTimeoutError,
    IPCError,
    IPCConnectionError,
    IPCTimeoutError,
    SyncError,
    SyncConnectionError,
    ConfigurationError,
)


class TestStationError:
    """Test suite for base StationError."""

    def test_init_with_message(self):
        """Test creating exception with message."""
        error = StationError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"

    def test_init_with_code(self):
        """Test creating exception with custom code."""
        error = StationError("Error", code="CUSTOM_CODE")

        assert error.code == "CUSTOM_CODE"

    def test_default_code_is_class_name(self):
        """Test that default code is the class name."""
        error = StationError("Error")

        assert error.code == "StationError"

    def test_init_with_details(self):
        """Test creating exception with details."""
        error = StationError("Error", details={"key": "value"})

        assert error.details == {"key": "value"}

    def test_to_dict(self):
        """Test serialization to dictionary."""
        error = StationError(
            "Test error",
            code="TEST_CODE",
            details={"extra": "info"},
        )

        result = error.to_dict()

        assert result["error"] == "TEST_CODE"
        assert result["message"] == "Test error"
        assert result["details"] == {"extra": "info"}


class TestBatchErrors:
    """Test suite for batch-related exceptions."""

    def test_batch_not_found_error(self):
        """Test BatchNotFoundError."""
        error = BatchNotFoundError("batch_001")

        assert error.batch_id == "batch_001"
        assert error.code == "BATCH_NOT_FOUND"
        assert "batch_001" in error.message
        assert error.details["batch_id"] == "batch_001"

    def test_batch_already_running_error(self):
        """Test BatchAlreadyRunningError."""
        error = BatchAlreadyRunningError("batch_001")

        assert error.batch_id == "batch_001"
        assert error.code == "BATCH_ALREADY_RUNNING"
        assert "already running" in error.message.lower()

    def test_batch_not_running_error(self):
        """Test BatchNotRunningError."""
        error = BatchNotRunningError("batch_001")

        assert error.batch_id == "batch_001"
        assert error.code == "BATCH_NOT_RUNNING"
        assert "not running" in error.message.lower()

    def test_batch_process_error(self):
        """Test BatchProcessError."""
        error = BatchProcessError(
            batch_id="batch_001",
            error="Process crashed",
            exit_code=1,
        )

        assert error.batch_id == "batch_001"
        assert error.exit_code == 1
        assert error.code == "BATCH_PROCESS_ERROR"
        assert error.details["exit_code"] == 1


class TestSequenceErrors:
    """Test suite for sequence-related exceptions."""

    def test_sequence_not_found_error(self):
        """Test SequenceNotFoundError."""
        error = SequenceNotFoundError("sequences/my_sequence")

        assert error.package_path == "sequences/my_sequence"
        assert error.code == "SEQUENCE_NOT_FOUND"

    def test_sequence_validation_error(self):
        """Test SequenceValidationError."""
        error = SequenceValidationError(
            message="Invalid manifest format",
            package_path="sequences/bad_sequence",
        )

        assert error.package_path == "sequences/bad_sequence"
        assert error.code == "SEQUENCE_VALIDATION_ERROR"

    def test_sequence_execution_error(self):
        """Test SequenceExecutionError."""
        error = SequenceExecutionError(
            message="Step failed",
            batch_id="batch_001",
            step_name="step_one",
        )

        assert error.batch_id == "batch_001"
        assert error.step_name == "step_one"
        assert error.code == "SEQUENCE_EXECUTION_ERROR"
        assert error.details["step_name"] == "step_one"


class TestHardwareErrors:
    """Test suite for hardware-related exceptions."""

    def test_hardware_connection_error(self):
        """Test HardwareConnectionError."""
        error = HardwareConnectionError(
            hardware_id="power_supply",
            reason="Port not found",
        )

        assert error.hardware_id == "power_supply"
        assert error.code == "HARDWARE_CONNECTION_ERROR"
        assert "power_supply" in error.message

    def test_hardware_timeout_error(self):
        """Test HardwareTimeoutError."""
        error = HardwareTimeoutError(
            hardware_id="power_supply",
            operation="set_voltage",
            timeout=5.0,
        )

        assert error.hardware_id == "power_supply"
        assert error.operation == "set_voltage"
        assert error.timeout == 5.0
        assert error.code == "HARDWARE_TIMEOUT"


class TestIPCErrors:
    """Test suite for IPC-related exceptions."""

    def test_ipc_connection_error(self):
        """Test IPCConnectionError."""
        error = IPCConnectionError(
            address="tcp://localhost:5555",
            reason="Connection refused",
        )

        assert error.address == "tcp://localhost:5555"
        assert error.code == "IPC_CONNECTION_ERROR"

    def test_ipc_timeout_error(self):
        """Test IPCTimeoutError."""
        error = IPCTimeoutError(
            operation="send_command",
            timeout=5000,
        )

        assert error.operation == "send_command"
        assert error.timeout == 5000
        assert error.code == "IPC_TIMEOUT"


class TestSyncErrors:
    """Test suite for sync-related exceptions."""

    def test_sync_connection_error(self):
        """Test SyncConnectionError."""
        error = SyncConnectionError(
            url="http://backend:8000",
            reason="Network unreachable",
        )

        assert error.url == "http://backend:8000"
        assert error.code == "SYNC_CONNECTION_ERROR"


class TestConfigurationError:
    """Test suite for configuration exceptions."""

    def test_configuration_error_with_file(self):
        """Test ConfigurationError with config file."""
        error = ConfigurationError(
            message="Invalid YAML syntax",
            config_file="/path/to/config.yaml",
        )

        assert error.config_file == "/path/to/config.yaml"
        assert error.code == "CONFIGURATION_ERROR"
        assert error.details["config_file"] == "/path/to/config.yaml"

    def test_configuration_error_without_file(self):
        """Test ConfigurationError without config file."""
        error = ConfigurationError("Missing required field")

        assert error.config_file is None
        assert error.details == {}


class TestExceptionHierarchy:
    """Test inheritance hierarchy."""

    def test_batch_error_is_station_error(self):
        """Test BatchError inherits from StationError."""
        assert issubclass(BatchError, StationError)

    def test_sequence_error_is_station_error(self):
        """Test SequenceError inherits from StationError."""
        assert issubclass(SequenceError, StationError)

    def test_hardware_error_is_station_error(self):
        """Test HardwareError inherits from StationError."""
        assert issubclass(HardwareError, StationError)

    def test_ipc_error_is_station_error(self):
        """Test IPCError inherits from StationError."""
        assert issubclass(IPCError, StationError)

    def test_sync_error_is_station_error(self):
        """Test SyncError inherits from StationError."""
        assert issubclass(SyncError, StationError)

    def test_batch_not_found_is_batch_error(self):
        """Test BatchNotFoundError inherits from BatchError."""
        assert issubclass(BatchNotFoundError, BatchError)

    def test_all_exceptions_are_catchable_as_station_error(self):
        """Test all exceptions can be caught as StationError."""
        exceptions = [
            BatchNotFoundError("test"),
            SequenceValidationError("error", "path"),
            HardwareConnectionError("hw", "reason"),
            IPCTimeoutError("op", 5000),
            SyncConnectionError("url", "reason"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except StationError as e:
                assert e is exc
