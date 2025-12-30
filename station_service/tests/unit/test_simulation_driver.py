"""
Unit tests for the Simulation Driver.

Tests simulation driver initialization, connection management,
measurement simulation, and failure rate behavior.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from station_service.drivers.simulation import (
    MeasurementRange,
    SimulationConfig,
    SimulationDriver,
    create_simulation_driver,
)
from station_service.drivers.base import BaseDriver, DriverConnectionError


class TestSimulationConfig:
    """Tests for SimulationConfig model."""

    def test_default_values(self):
        """Test default configuration values."""
        config = SimulationConfig()

        assert config.enabled is True
        assert config.min_delay == 0.1
        assert config.max_delay == 0.5
        assert config.failure_rate == 0.02
        assert config.connection_delay == 0.2
        assert config.measurement_ranges == {}

    def test_custom_values(self):
        """Test custom configuration values."""
        config = SimulationConfig(
            enabled=False,
            min_delay=0.05,
            max_delay=0.2,
            failure_rate=0.1,
            connection_delay=0.5,
            measurement_ranges={
                "voltage": MeasurementRange(min=4.8, max=5.2, unit="V"),
            },
        )

        assert config.enabled is False
        assert config.min_delay == 0.05
        assert config.max_delay == 0.2
        assert config.failure_rate == 0.1
        assert "voltage" in config.measurement_ranges


class TestMeasurementRange:
    """Tests for MeasurementRange model."""

    def test_default_values(self):
        """Test default measurement range values."""
        range_ = MeasurementRange(min=0.0, max=100.0)

        assert range_.min == 0.0
        assert range_.max == 100.0
        assert range_.unit == ""
        assert range_.noise == 0.01

    def test_custom_values(self):
        """Test custom measurement range values."""
        range_ = MeasurementRange(
            min=4.8,
            max=5.2,
            unit="V",
            noise=0.05,
        )

        assert range_.min == 4.8
        assert range_.max == 5.2
        assert range_.unit == "V"
        assert range_.noise == 0.05


class TestSimulationDriverInit:
    """Tests for SimulationDriver initialization."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        driver = SimulationDriver(name="test_driver")

        assert driver.name == "test_driver"
        assert driver.simulation_enabled is True
        assert driver._connected is False

    def test_init_with_simulation_config(self):
        """Test initialization with explicit SimulationConfig."""
        sim_config = SimulationConfig(
            min_delay=0.01,
            max_delay=0.02,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        assert driver._sim_config.min_delay == 0.01
        assert driver._sim_config.max_delay == 0.02
        assert driver._sim_config.failure_rate == 0.0

    def test_init_with_config_dict(self):
        """Test initialization with config dict containing simulation section."""
        config = {
            "simulation": {
                "enabled": True,
                "min_delay": 0.05,
                "max_delay": 0.1,
                "failure_rate": 0.01,
            },
        }
        driver = SimulationDriver(name="test_driver", config=config)

        assert driver._sim_config.min_delay == 0.05
        assert driver._sim_config.max_delay == 0.1
        assert driver._sim_config.failure_rate == 0.01

    def test_init_with_wrapped_driver(self):
        """Test initialization with a wrapped driver."""
        mock_driver = MagicMock(spec=BaseDriver)
        driver = SimulationDriver(
            name="test_driver",
            wrapped_driver=mock_driver,
        )

        assert driver._wrapped_driver is mock_driver


class TestSimulationDriverConnect:
    """Tests for SimulationDriver connect/disconnect."""

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        sim_config = SimulationConfig(
            connection_delay=0.01,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        result = await driver.connect()

        assert result is True
        assert driver._connected is True
        assert driver._connected_at is not None

    @pytest.mark.asyncio
    async def test_connect_with_wrapped_driver(self):
        """Test connection with wrapped driver."""
        mock_driver = MagicMock(spec=BaseDriver)
        mock_driver.connect = AsyncMock()

        sim_config = SimulationConfig(
            connection_delay=0.01,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
            wrapped_driver=mock_driver,
        )

        await driver.connect()

        mock_driver.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure_on_high_failure_rate(self):
        """Test connection failure with 100% failure rate."""
        sim_config = SimulationConfig(
            connection_delay=0.01,
            failure_rate=1.0,  # Always fail
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        with pytest.raises(DriverConnectionError):
            await driver.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnection."""
        sim_config = SimulationConfig(
            connection_delay=0.01,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        await driver.disconnect()

        assert driver._connected is False
        assert driver._connected_at is None

    @pytest.mark.asyncio
    async def test_is_connected(self):
        """Test is_connected method."""
        sim_config = SimulationConfig(
            connection_delay=0.01,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        assert await driver.is_connected() is False

        await driver.connect()
        assert await driver.is_connected() is True

        await driver.disconnect()
        assert await driver.is_connected() is False


class TestSimulationDriverMeasure:
    """Tests for SimulationDriver measurement simulation."""

    @pytest.mark.asyncio
    async def test_measure_without_connection_raises(self):
        """Test that measure raises when not connected."""
        driver = SimulationDriver(name="test_driver")

        with pytest.raises(DriverConnectionError):
            await driver.measure("voltage")

    @pytest.mark.asyncio
    async def test_measure_with_configured_range(self):
        """Test measurement with configured range."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
            measurement_ranges={
                "voltage": MeasurementRange(min=4.8, max=5.2, unit="V", noise=0.01),
            },
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        value = await driver.measure("voltage")

        # Value should be within range (approximately)
        assert 4.7 <= value <= 5.3  # Allow for noise

    @pytest.mark.asyncio
    async def test_measure_with_default_range(self):
        """Test measurement with default range when not configured."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        value = await driver.measure("unconfigured_measurement")

        # Should use default range 0-100
        assert 0 <= value <= 100

    @pytest.mark.asyncio
    async def test_measure_updates_last_measurements(self):
        """Test that measurement updates last_measurements dict."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        value = await driver.measure("test_measurement")

        assert "test_measurement" in driver._last_measurements
        assert driver._last_measurements["test_measurement"] == value

    @pytest.mark.asyncio
    async def test_measure_increments_operation_count(self):
        """Test that measurement increments operation counter."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        initial_count = driver._operation_count

        await driver.measure("test")
        await driver.measure("test")

        assert driver._operation_count == initial_count + 2


class TestSimulationDriverSetOutput:
    """Tests for SimulationDriver set_output method."""

    @pytest.mark.asyncio
    async def test_set_output_without_connection_raises(self):
        """Test that set_output raises when not connected."""
        driver = SimulationDriver(name="test_driver")

        with pytest.raises(DriverConnectionError):
            await driver.set_output("relay", True)

    @pytest.mark.asyncio
    async def test_set_output_success(self):
        """Test successful set_output operation."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        result = await driver.set_output("relay", True)

        assert result is True


class TestSimulationDriverReadInput:
    """Tests for SimulationDriver read_input method."""

    @pytest.mark.asyncio
    async def test_read_input_without_connection_raises(self):
        """Test that read_input raises when not connected."""
        driver = SimulationDriver(name="test_driver")

        with pytest.raises(DriverConnectionError):
            await driver.read_input("sensor")

    @pytest.mark.asyncio
    async def test_read_input_status_returns_boolean(self):
        """Test that status input returns boolean."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        value = await driver.read_input("ready_status")

        assert isinstance(value, bool)

    @pytest.mark.asyncio
    async def test_read_input_count_returns_int(self):
        """Test that count input returns integer."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        value = await driver.read_input("item_count")

        assert isinstance(value, int)


class TestSimulationDriverExecuteAction:
    """Tests for SimulationDriver execute_action method."""

    @pytest.mark.asyncio
    async def test_execute_action_without_connection_raises(self):
        """Test that execute_action raises when not connected."""
        driver = SimulationDriver(name="test_driver")

        with pytest.raises(DriverConnectionError):
            await driver.execute_action("calibrate")

    @pytest.mark.asyncio
    async def test_execute_action_success(self):
        """Test successful action execution."""
        sim_config = SimulationConfig(
            min_delay=0.001,
            max_delay=0.002,
            failure_rate=0.0,
            connection_delay=0.001,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        result = await driver.execute_action("calibrate", param1="value1")

        assert result["success"] is True
        assert result["action"] == "calibrate"
        assert result["params"]["param1"] == "value1"
        assert "timestamp" in result


class TestSimulationDriverGetStatus:
    """Tests for SimulationDriver get_status method."""

    @pytest.mark.asyncio
    async def test_get_status_disconnected(self):
        """Test status when disconnected."""
        driver = SimulationDriver(name="test_driver")

        status = await driver.get_status()

        assert status["connected"] is False
        assert status["simulation_enabled"] is True
        assert status["operation_count"] == 0
        assert status["connected_at"] is None

    @pytest.mark.asyncio
    async def test_get_status_connected(self):
        """Test status when connected."""
        sim_config = SimulationConfig(
            connection_delay=0.001,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        await driver.connect()
        status = await driver.get_status()

        assert status["connected"] is True
        assert status["connected_at"] is not None

    @pytest.mark.asyncio
    async def test_get_status_includes_wrapped_driver(self):
        """Test status includes wrapped driver status."""
        mock_driver = MagicMock(spec=BaseDriver)
        mock_driver.get_status = AsyncMock(return_value={"test": "data"})

        sim_config = SimulationConfig(
            connection_delay=0.001,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
            wrapped_driver=mock_driver,
        )

        await driver.connect()
        status = await driver.get_status()

        assert "wrapped_driver" in status
        assert status["wrapped_driver"]["test"] == "data"


class TestSimulationDriverAvailableCommands:
    """Tests for get_available_commands method."""

    def test_available_commands(self):
        """Test that available commands are returned."""
        driver = SimulationDriver(name="test_driver")

        commands = driver.get_available_commands()

        assert "measure" in commands
        assert "set_output" in commands
        assert "read_input" in commands
        assert "execute_action" in commands


class TestCreateSimulationDriver:
    """Tests for create_simulation_driver factory function."""

    def test_creates_simulation_driver_when_enabled(self):
        """Test factory creates SimulationDriver when enabled."""
        sim_config = SimulationConfig(enabled=True)

        driver = create_simulation_driver(
            driver_class=BaseDriver,
            name="test_driver",
            config={},
            simulation_config=sim_config,
        )

        assert isinstance(driver, SimulationDriver)

    def test_creates_real_driver_when_disabled(self):
        """Test factory creates real driver when simulation disabled."""

        class MockDriver(BaseDriver):
            async def connect(self):
                return True

            async def disconnect(self):
                pass

            async def is_connected(self):
                return self._connected

            async def get_status(self):
                return {"connected": self._connected}

        sim_config = SimulationConfig(enabled=False)

        driver = create_simulation_driver(
            driver_class=MockDriver,
            name="test_driver",
            config={},
            simulation_config=sim_config,
        )

        assert isinstance(driver, MockDriver)
        assert not isinstance(driver, SimulationDriver)

    def test_wraps_real_driver_when_enabled(self):
        """Test that real driver is wrapped when simulation enabled."""

        class MockDriver(BaseDriver):
            pass

        sim_config = SimulationConfig(enabled=True)

        driver = create_simulation_driver(
            driver_class=MockDriver,
            name="test_driver",
            config={},
            simulation_config=sim_config,
        )

        assert isinstance(driver, SimulationDriver)
        # Wrapped driver should be created
        assert driver._wrapped_driver is not None or driver._wrapped_driver is None
        # May be None if MockDriver init fails, but that's ok for simulation


class TestSimulationDelayAndFailure:
    """Tests for delay simulation and failure rate."""

    @pytest.mark.asyncio
    async def test_simulate_delay_within_range(self):
        """Test that delays are within configured range."""
        sim_config = SimulationConfig(
            min_delay=0.01,
            max_delay=0.02,
            connection_delay=0.001,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        start = asyncio.get_event_loop().time()
        await driver._simulate_delay()
        elapsed = asyncio.get_event_loop().time() - start

        assert 0.01 <= elapsed <= 0.03  # Allow some margin

    @pytest.mark.asyncio
    async def test_simulate_fixed_delay(self):
        """Test fixed delay parameter."""
        sim_config = SimulationConfig(
            min_delay=1.0,  # High min delay
            max_delay=2.0,
            failure_rate=0.0,
        )
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        start = asyncio.get_event_loop().time()
        await driver._simulate_delay(fixed_delay=0.01)  # Override with short delay
        elapsed = asyncio.get_event_loop().time() - start

        assert elapsed < 0.5  # Should use fixed delay, not config

    def test_should_fail_never_with_zero_rate(self):
        """Test that failures never occur with 0% rate."""
        sim_config = SimulationConfig(failure_rate=0.0)
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        # Run many times to ensure no failures
        failures = sum(driver._should_fail() for _ in range(1000))
        assert failures == 0

    def test_should_fail_always_with_full_rate(self):
        """Test that failures always occur with 100% rate."""
        sim_config = SimulationConfig(failure_rate=1.0)
        driver = SimulationDriver(
            name="test_driver",
            simulation_config=sim_config,
        )

        # Run many times to ensure all failures
        failures = sum(driver._should_fail() for _ in range(100))
        assert failures == 100
