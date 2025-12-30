"""
Process-Specific Simulation Templates for F2X NeuroHub.

This module provides pre-configured simulation templates for each of the
8 manufacturing processes in the production line. Each template includes
realistic measurement ranges and process-specific behaviors.

Manufacturing Processes:
1. Laser Marking (레이저 마킹)
2. LMA Assembly (LMA 조립)
3. Sensor Inspection (센서 검사)
4. Firmware Upload (펌웨어 업로드)
5. Robot Assembly (로봇 조립)
6. Performance Testing (성능검사)
7. Label Printing (라벨 프린팅)
8. Packaging + Visual Inspection (포장 + 외관검사)
"""

from typing import Dict, List, Any
from station_service.drivers.simulation import SimulationConfig, MeasurementRange


# ============================================================================
# Process 1: Laser Marking (레이저 마킹)
# ============================================================================

LASER_MARKING_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.3,
    max_delay=0.8,
    failure_rate=0.01,
    connection_delay=0.5,
    measurement_ranges={
        "marking_depth": MeasurementRange(min=0.05, max=0.15, unit="mm", noise=0.02),
        "power_level": MeasurementRange(min=85, max=100, unit="%", noise=0.01),
        "scan_speed": MeasurementRange(min=800, max=1200, unit="mm/s", noise=0.02),
        "focus_offset": MeasurementRange(min=-0.1, max=0.1, unit="mm", noise=0.03),
        "marking_contrast": MeasurementRange(min=80, max=100, unit="%", noise=0.02),
        "cycle_time": MeasurementRange(min=2.5, max=4.0, unit="s", noise=0.05),
    },
)


# ============================================================================
# Process 2: LMA Assembly (LMA 조립)
# ============================================================================

LMA_ASSEMBLY_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.2,
    max_delay=0.6,
    failure_rate=0.015,
    connection_delay=0.3,
    measurement_ranges={
        "torque": MeasurementRange(min=0.5, max=2.0, unit="Nm", noise=0.03),
        "alignment_offset_x": MeasurementRange(min=-0.05, max=0.05, unit="mm", noise=0.02),
        "alignment_offset_y": MeasurementRange(min=-0.05, max=0.05, unit="mm", noise=0.02),
        "insertion_force": MeasurementRange(min=5, max=15, unit="N", noise=0.05),
        "seating_depth": MeasurementRange(min=2.8, max=3.2, unit="mm", noise=0.02),
        "assembly_time": MeasurementRange(min=3, max=6, unit="s", noise=0.05),
    },
)


# ============================================================================
# Process 3: Sensor Inspection (센서 검사)
# ============================================================================

SENSOR_INSPECTION_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.4,
    max_delay=1.0,
    failure_rate=0.03,  # Higher failure rate - more rigorous inspection
    connection_delay=0.4,
    measurement_ranges={
        "resistance": MeasurementRange(min=95, max=105, unit="Ohm", noise=0.02),
        "voltage_output": MeasurementRange(min=4.8, max=5.2, unit="V", noise=0.01),
        "current_draw": MeasurementRange(min=0.09, max=0.11, unit="A", noise=0.02),
        "calibration_offset": MeasurementRange(min=-0.02, max=0.02, unit="", noise=0.01),
        "signal_noise": MeasurementRange(min=0.001, max=0.01, unit="mV", noise=0.1),
        "response_time": MeasurementRange(min=5, max=15, unit="ms", noise=0.05),
        "temperature": MeasurementRange(min=23, max=27, unit="C", noise=0.02),
        "inspection_duration": MeasurementRange(min=5, max=10, unit="s", noise=0.05),
    },
)


# ============================================================================
# Process 4: Firmware Upload (펌웨어 업로드)
# ============================================================================

FIRMWARE_UPLOAD_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.1,
    max_delay=0.3,
    failure_rate=0.02,
    connection_delay=0.8,  # Longer connection time for bootloader
    measurement_ranges={
        "flash_time": MeasurementRange(min=8, max=15, unit="s", noise=0.1),
        "verify_checksum": MeasurementRange(min=0, max=0, unit="", noise=0),  # Boolean result
        "transfer_speed": MeasurementRange(min=800, max=1200, unit="KB/s", noise=0.05),
        "memory_usage": MeasurementRange(min=60, max=85, unit="%", noise=0.02),
        "boot_time": MeasurementRange(min=1.5, max=3.0, unit="s", noise=0.1),
        "communication_latency": MeasurementRange(min=2, max=10, unit="ms", noise=0.1),
    },
)


# ============================================================================
# Process 5: Robot Assembly (로봇 조립)
# ============================================================================

ROBOT_ASSEMBLY_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.3,
    max_delay=0.7,
    failure_rate=0.02,
    connection_delay=0.5,
    measurement_ranges={
        "cycle_time": MeasurementRange(min=12, max=18, unit="s", noise=0.05),
        "position_accuracy_x": MeasurementRange(min=-0.02, max=0.02, unit="mm", noise=0.01),
        "position_accuracy_y": MeasurementRange(min=-0.02, max=0.02, unit="mm", noise=0.01),
        "position_accuracy_z": MeasurementRange(min=-0.02, max=0.02, unit="mm", noise=0.01),
        "grip_force": MeasurementRange(min=8, max=12, unit="N", noise=0.03),
        "placement_pressure": MeasurementRange(min=3, max=7, unit="N", noise=0.05),
        "rotation_angle": MeasurementRange(min=-0.5, max=0.5, unit="deg", noise=0.02),
        "repeatability": MeasurementRange(min=0.001, max=0.01, unit="mm", noise=0.05),
    },
)


# ============================================================================
# Process 6: Performance Testing (성능검사)
# ============================================================================

PERFORMANCE_TESTING_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.5,
    max_delay=1.5,
    failure_rate=0.04,  # Higher failure rate - final performance check
    connection_delay=0.6,
    measurement_ranges={
        "response_time": MeasurementRange(min=8, max=15, unit="ms", noise=0.05),
        "accuracy": MeasurementRange(min=98, max=100, unit="%", noise=0.01),
        "noise_level": MeasurementRange(min=-80, max=-60, unit="dB", noise=0.03),
        "power_consumption": MeasurementRange(min=0.4, max=0.6, unit="W", noise=0.02),
        "operating_voltage": MeasurementRange(min=4.9, max=5.1, unit="V", noise=0.01),
        "temperature_rise": MeasurementRange(min=3, max=8, unit="C", noise=0.05),
        "throughput": MeasurementRange(min=90, max=100, unit="%", noise=0.02),
        "stability_index": MeasurementRange(min=95, max=100, unit="%", noise=0.01),
        "test_duration": MeasurementRange(min=15, max=25, unit="s", noise=0.05),
    },
)


# ============================================================================
# Process 7: Label Printing (라벨 프린팅)
# ============================================================================

LABEL_PRINTING_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.2,
    max_delay=0.5,
    failure_rate=0.01,
    connection_delay=0.3,
    measurement_ranges={
        "print_quality": MeasurementRange(min=85, max=100, unit="%", noise=0.02),
        "alignment_offset_x": MeasurementRange(min=-0.3, max=0.3, unit="mm", noise=0.02),
        "alignment_offset_y": MeasurementRange(min=-0.3, max=0.3, unit="mm", noise=0.02),
        "barcode_grade": MeasurementRange(min=3.5, max=4.0, unit="", noise=0.02),  # A=4, B=3, etc.
        "contrast_ratio": MeasurementRange(min=80, max=100, unit="%", noise=0.02),
        "adhesion_strength": MeasurementRange(min=8, max=12, unit="N", noise=0.05),
        "print_time": MeasurementRange(min=1.5, max=3.0, unit="s", noise=0.05),
    },
)


# ============================================================================
# Process 8: Packaging + Visual Inspection (포장 + 외관검사)
# ============================================================================

PACKAGING_INSPECTION_TEMPLATE = SimulationConfig(
    enabled=True,
    min_delay=0.3,
    max_delay=0.8,
    failure_rate=0.02,
    connection_delay=0.4,
    measurement_ranges={
        "seal_integrity": MeasurementRange(min=95, max=100, unit="%", noise=0.01),
        "visual_defect_count": MeasurementRange(min=0, max=0, unit="", noise=0),  # Should be 0
        "package_weight": MeasurementRange(min=95, max=105, unit="g", noise=0.02),
        "dimension_length": MeasurementRange(min=99, max=101, unit="mm", noise=0.01),
        "dimension_width": MeasurementRange(min=49, max=51, unit="mm", noise=0.01),
        "dimension_height": MeasurementRange(min=19, max=21, unit="mm", noise=0.01),
        "label_presence": MeasurementRange(min=1, max=1, unit="", noise=0),  # Boolean
        "barcode_readable": MeasurementRange(min=1, max=1, unit="", noise=0),  # Boolean
        "inspection_time": MeasurementRange(min=3, max=6, unit="s", noise=0.05),
    },
)


# ============================================================================
# Process Template Registry
# ============================================================================

PROCESS_TEMPLATES: Dict[int, SimulationConfig] = {
    1: LASER_MARKING_TEMPLATE,
    2: LMA_ASSEMBLY_TEMPLATE,
    3: SENSOR_INSPECTION_TEMPLATE,
    4: FIRMWARE_UPLOAD_TEMPLATE,
    5: ROBOT_ASSEMBLY_TEMPLATE,
    6: PERFORMANCE_TESTING_TEMPLATE,
    7: LABEL_PRINTING_TEMPLATE,
    8: PACKAGING_INSPECTION_TEMPLATE,
}

PROCESS_NAMES: Dict[int, str] = {
    1: "Laser Marking",
    2: "LMA Assembly",
    3: "Sensor Inspection",
    4: "Firmware Upload",
    5: "Robot Assembly",
    6: "Performance Testing",
    7: "Label Printing",
    8: "Packaging + Visual Inspection",
}

PROCESS_NAMES_KR: Dict[int, str] = {
    1: "레이저 마킹",
    2: "LMA 조립",
    3: "센서 검사",
    4: "펌웨어 업로드",
    5: "로봇 조립",
    6: "성능검사",
    7: "라벨 프린팅",
    8: "포장 + 외관검사",
}


def get_process_template(process_id: int) -> SimulationConfig:
    """
    Get the simulation template for a specific process.

    Args:
        process_id: Process ID (1-8)

    Returns:
        SimulationConfig for the process

    Raises:
        ValueError: If process_id is not 1-8
    """
    if process_id not in PROCESS_TEMPLATES:
        raise ValueError(f"Invalid process_id: {process_id}. Must be 1-8.")
    return PROCESS_TEMPLATES[process_id]


def get_process_name(process_id: int, korean: bool = False) -> str:
    """
    Get the name of a process.

    Args:
        process_id: Process ID (1-8)
        korean: If True, return Korean name

    Returns:
        Process name

    Raises:
        ValueError: If process_id is not 1-8
    """
    names = PROCESS_NAMES_KR if korean else PROCESS_NAMES
    if process_id not in names:
        raise ValueError(f"Invalid process_id: {process_id}. Must be 1-8.")
    return names[process_id]


def get_all_templates() -> Dict[int, Dict[str, Any]]:
    """
    Get all process templates with metadata.

    Returns:
        Dictionary mapping process_id to template info
    """
    result = {}
    for process_id in range(1, 9):
        template = PROCESS_TEMPLATES[process_id]
        result[process_id] = {
            "name": PROCESS_NAMES[process_id],
            "name_kr": PROCESS_NAMES_KR[process_id],
            "config": template.model_dump(),
            "measurements": list(template.measurement_ranges.keys()),
        }
    return result


def create_custom_template(
    base_process_id: int,
    failure_rate: float | None = None,
    min_delay: float | None = None,
    max_delay: float | None = None,
    additional_measurements: Dict[str, MeasurementRange] | None = None,
) -> SimulationConfig:
    """
    Create a custom template based on an existing process template.

    Args:
        base_process_id: Base process ID (1-8)
        failure_rate: Override failure rate
        min_delay: Override minimum delay
        max_delay: Override maximum delay
        additional_measurements: Additional measurement ranges to add

    Returns:
        Customized SimulationConfig
    """
    base = get_process_template(base_process_id)

    # Create copy of measurement ranges
    measurement_ranges = base.measurement_ranges.copy()
    if additional_measurements:
        measurement_ranges.update(additional_measurements)

    return SimulationConfig(
        enabled=base.enabled,
        min_delay=min_delay if min_delay is not None else base.min_delay,
        max_delay=max_delay if max_delay is not None else base.max_delay,
        failure_rate=failure_rate if failure_rate is not None else base.failure_rate,
        connection_delay=base.connection_delay,
        measurement_ranges=measurement_ranges,
    )
