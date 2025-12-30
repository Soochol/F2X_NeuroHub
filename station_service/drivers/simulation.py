"""
Simulation Driver for Station Service.

This module provides a simulation driver that wraps real drivers or operates
independently to simulate hardware behavior. Useful for testing and development
without actual hardware.
"""

import asyncio
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field

from station_service.drivers.base import BaseDriver, DriverConnectionError

import logging

logger = logging.getLogger(__name__)


class MeasurementRange(BaseModel):
    """Range specification for simulated measurements."""

    min: float = Field(..., description="Minimum value")
    max: float = Field(..., description="Maximum value")
    unit: str = Field("", description="Unit of measurement")
    noise: float = Field(0.01, description="Random noise factor (0-1)")


class SimulationConfig(BaseModel):
    """Configuration for simulation behavior."""

    enabled: bool = Field(True, description="Whether simulation mode is enabled")
    min_delay: float = Field(0.1, description="Minimum delay in seconds")
    max_delay: float = Field(0.5, description="Maximum delay in seconds")
    failure_rate: float = Field(0.02, description="Probability of random failure (0-1)")
    connection_delay: float = Field(0.2, description="Delay for connect/disconnect")
    measurement_ranges: Dict[str, MeasurementRange] = Field(
        default_factory=dict,
        description="Measurement ranges by name",
    )


class SimulationDriver(BaseDriver):
    """
    Simulation driver that mimics hardware behavior.

    This driver can either wrap a real driver (for partial simulation)
    or operate independently to fully simulate hardware behavior.

    Features:
    - Configurable delays to simulate real hardware timing
    - Random failures at configurable rate
    - Realistic measurement generation with noise
    - Connection state tracking

    Usage:
        config = SimulationConfig(
            min_delay=0.1,
            max_delay=0.5,
            failure_rate=0.02,
            measurement_ranges={
                "voltage": MeasurementRange(min=4.8, max=5.2, unit="V"),
                "current": MeasurementRange(min=0.9, max=1.1, unit="A"),
            }
        )
        driver = SimulationDriver("dmm", config=config)
        await driver.connect()
        voltage = await driver.measure("voltage")
    """

    def __init__(
        self,
        name: str = "",
        config: Optional[Dict[str, Any]] = None,
        simulation_config: Optional[SimulationConfig] = None,
        wrapped_driver: Optional[BaseDriver] = None,
    ):
        """
        Initialize the simulation driver.

        Args:
            name: Driver instance name
            config: Standard driver configuration
            simulation_config: Simulation-specific configuration
            wrapped_driver: Optional real driver to wrap
        """
        super().__init__(name, config)

        # Parse simulation config
        if simulation_config is not None:
            self._sim_config = simulation_config
        elif config and "simulation" in config:
            self._sim_config = SimulationConfig.model_validate(config["simulation"])
        else:
            self._sim_config = SimulationConfig()

        self._wrapped_driver = wrapped_driver
        self._last_measurements: Dict[str, float] = {}
        self._operation_count = 0
        self._connected_at: Optional[datetime] = None

    @property
    def simulation_enabled(self) -> bool:
        """Check if simulation mode is enabled."""
        return self._sim_config.enabled

    async def connect(self) -> bool:
        """
        Simulate connection to hardware.

        Returns:
            True if connection successful
        """
        await self._simulate_delay(self._sim_config.connection_delay)

        if self._should_fail():
            raise DriverConnectionError(
                "Simulated connection failure",
                driver_name=self.name,
            )

        if self._wrapped_driver:
            # Connect real driver too
            try:
                await self._wrapped_driver.connect()
            except Exception as e:
                logger.warning(f"Wrapped driver connection failed: {e}")
                # Continue with simulation

        self._connected = True
        self._connected_at = datetime.now()
        logger.info(f"Simulation driver connected: {self.name}")
        return True

    async def disconnect(self) -> None:
        """Simulate disconnection from hardware."""
        await self._simulate_delay(self._sim_config.connection_delay * 0.5)

        if self._wrapped_driver and self._wrapped_driver.connected:
            try:
                await self._wrapped_driver.disconnect()
            except Exception as e:
                logger.warning(f"Wrapped driver disconnect failed: {e}")

        self._connected = False
        self._connected_at = None
        logger.info(f"Simulation driver disconnected: {self.name}")

    async def is_connected(self) -> bool:
        """Check if simulation driver is connected."""
        return self._connected

    async def get_status(self) -> Dict[str, Any]:
        """
        Get simulation driver status.

        Returns:
            Dictionary with status information
        """
        status = {
            "connected": self._connected,
            "simulation_enabled": self.simulation_enabled,
            "operation_count": self._operation_count,
            "failure_rate": self._sim_config.failure_rate,
            "connected_at": self._connected_at.isoformat() if self._connected_at else None,
            "last_measurements": self._last_measurements.copy(),
        }

        if self._wrapped_driver:
            try:
                wrapped_status = await self._wrapped_driver.get_status()
                status["wrapped_driver"] = wrapped_status
            except Exception as e:
                status["wrapped_driver_error"] = str(e)

        return status

    async def measure(self, measurement_name: str, **kwargs: Any) -> float:
        """
        Simulate a measurement.

        Args:
            measurement_name: Name of the measurement to simulate
            **kwargs: Additional parameters (ignored in simulation)

        Returns:
            Simulated measurement value

        Raises:
            DriverConnectionError: If not connected
            ValueError: If measurement range not configured
        """
        if not self._connected:
            raise DriverConnectionError(
                "Driver not connected",
                driver_name=self.name,
            )

        await self._simulate_delay()
        self._operation_count += 1

        if self._should_fail():
            raise Exception(f"Simulated measurement failure for {measurement_name}")

        # Get measurement range
        if measurement_name in self._sim_config.measurement_ranges:
            range_config = self._sim_config.measurement_ranges[measurement_name]
        else:
            # Default range if not configured
            range_config = MeasurementRange(min=0.0, max=100.0, unit="")

        # Generate value with noise
        base_value = random.uniform(range_config.min, range_config.max)
        noise = random.uniform(-range_config.noise, range_config.noise) * base_value
        value = round(base_value + noise, 4)

        self._last_measurements[measurement_name] = value
        logger.debug(f"Simulated {measurement_name}: {value} {range_config.unit}")

        return value

    async def set_output(self, output_name: str, value: Any, **kwargs: Any) -> bool:
        """
        Simulate setting an output.

        Args:
            output_name: Name of the output
            value: Value to set
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        if not self._connected:
            raise DriverConnectionError(
                "Driver not connected",
                driver_name=self.name,
            )

        await self._simulate_delay()
        self._operation_count += 1

        if self._should_fail():
            return False

        logger.debug(f"Simulated set {output_name} = {value}")
        return True

    async def read_input(self, input_name: str, **kwargs: Any) -> Any:
        """
        Simulate reading an input.

        Args:
            input_name: Name of the input
            **kwargs: Additional parameters

        Returns:
            Simulated input value
        """
        if not self._connected:
            raise DriverConnectionError(
                "Driver not connected",
                driver_name=self.name,
            )

        await self._simulate_delay()
        self._operation_count += 1

        if self._should_fail():
            raise Exception(f"Simulated read failure for {input_name}")

        # Generate random boolean or numeric value based on name hints
        if "status" in input_name.lower() or "flag" in input_name.lower():
            return random.choice([True, False])
        elif "count" in input_name.lower():
            return random.randint(0, 100)
        else:
            return random.uniform(0, 100)

    async def execute_action(self, action_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Simulate executing an action.

        Args:
            action_name: Name of the action
            **kwargs: Action parameters

        Returns:
            Action result dictionary
        """
        if not self._connected:
            raise DriverConnectionError(
                "Driver not connected",
                driver_name=self.name,
            )

        await self._simulate_delay()
        self._operation_count += 1

        if self._should_fail():
            return {"success": False, "error": "Simulated action failure"}

        logger.debug(f"Simulated action: {action_name} with {kwargs}")

        return {
            "success": True,
            "action": action_name,
            "params": kwargs,
            "timestamp": datetime.now().isoformat(),
        }

    async def _simulate_delay(self, fixed_delay: Optional[float] = None) -> None:
        """
        Simulate operation delay.

        Args:
            fixed_delay: Optional fixed delay, otherwise random within config range
        """
        if fixed_delay is not None:
            delay = fixed_delay
        else:
            delay = random.uniform(
                self._sim_config.min_delay,
                self._sim_config.max_delay,
            )

        await asyncio.sleep(delay)

    def _should_fail(self) -> bool:
        """
        Determine if operation should fail based on failure rate.

        Returns:
            True if operation should fail
        """
        return random.random() < self._sim_config.failure_rate

    def get_available_commands(self) -> List[str]:
        """Get list of available simulation commands."""
        return ["measure", "set_output", "read_input", "execute_action"]


def create_simulation_driver(
    driver_class: Type[BaseDriver],
    name: str,
    config: Dict[str, Any],
    simulation_config: Optional[SimulationConfig] = None,
) -> SimulationDriver:
    """
    Factory function to create a simulation driver.

    If simulation is enabled, returns a SimulationDriver. Otherwise,
    creates and returns the real driver.

    Args:
        driver_class: The real driver class
        name: Driver instance name
        config: Driver configuration
        simulation_config: Simulation configuration

    Returns:
        SimulationDriver or real driver instance
    """
    sim_config = simulation_config or SimulationConfig()

    if sim_config.enabled:
        # Create simulation driver, optionally wrapping the real driver
        try:
            real_driver = driver_class(name=name, config=config)
        except Exception as e:
            logger.warning(f"Failed to create real driver for wrapping: {e}")
            real_driver = None

        return SimulationDriver(
            name=name,
            config=config,
            simulation_config=sim_config,
            wrapped_driver=real_driver,
        )
    else:
        # Return real driver
        return driver_class(name=name, config=config)
