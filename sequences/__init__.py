"""
Sequences Package

This package contains test sequences for the NeuroHub station service.
Each sequence is a self-contained package with its own manifest, drivers,
and test logic.

Available sequences:
- sensor_inspection: Sensor calibration and inspection sequence
- manual_test: Manual control test sequence
- psa_sensor_test: PSA sensor (VL53L0X, MLX90640) test sequence
"""

__all__ = ["sensor_inspection", "manual_test", "psa_sensor_test"]
