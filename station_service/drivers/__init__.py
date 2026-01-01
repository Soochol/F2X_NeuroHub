"""
Station Service Drivers Package.

This package provides hardware driver abstractions and simulation capabilities
for the Station Service.

Modules:
    base: Abstract base class for all hardware drivers
    simulation: Simulation wrapper for testing without real hardware
    process_templates: Process-specific simulation configurations
    barcode_scanner: Serial barcode scanner drivers for WIP ID scanning
"""

from station_service.drivers.base import BaseDriver, DriverConnectionError, DriverError
from station_service.drivers.simulation import SimulationDriver, SimulationConfig
from station_service.drivers.barcode_scanner import (
    SerialBarcodeScannerDriver,
    MockBarcodeScannerDriver,
    BarcodeScannerError,
)

__all__ = [
    "BaseDriver",
    "DriverError",
    "DriverConnectionError",
    "SimulationDriver",
    "SimulationConfig",
    "SerialBarcodeScannerDriver",
    "MockBarcodeScannerDriver",
    "BarcodeScannerError",
]
