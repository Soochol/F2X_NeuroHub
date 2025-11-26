"""
Process Data Generator - Auto-generate process_data for each process.
"""
from datetime import datetime
from typing import Any, Dict


class ProcessDataGenerator:
    """Generate process_data for completion based on process type."""

    @staticmethod
    def generate_pass_data(process_number: int, lot_number: str,
                           start_time: datetime, complete_time: datetime,
                           **kwargs: Any) -> Dict[str, Any]:
        """
        Generate process_data for PASS completion.

        Args:
            process_number: Process number (1-8)
            lot_number: LOT number
            start_time: Work start time
            complete_time: Work complete time
            **kwargs: Additional process-specific data

        Returns:
            dict: process_data for the completion API
        """
        # Calculate assembly time in minutes
        assembly_time = (complete_time - start_time).total_seconds() / 60

        generators = {
            1: ProcessDataGenerator._generate_laser_marking_pass,
            2: ProcessDataGenerator._generate_lma_assembly_pass,
            3: ProcessDataGenerator._generate_sensor_inspection_pass,
            4: ProcessDataGenerator._generate_firmware_upload_pass,
            5: ProcessDataGenerator._generate_robot_assembly_pass,
            6: ProcessDataGenerator._generate_performance_test_pass,
            7: ProcessDataGenerator._generate_label_printing_pass,
            8: ProcessDataGenerator._generate_packaging_pass,
        }

        generator = generators.get(process_number)
        if generator:
            return generator(lot_number, assembly_time, **kwargs)

        return {}

    @staticmethod
    def generate_fail_data(process_number: int, lot_number: str,
                           start_time: datetime, complete_time: datetime,
                           defect_type: str, defect_description: str = "",
                           **kwargs: Any) -> Dict[str, Any]:
        """
        Generate process_data for FAIL completion.

        Args:
            process_number: Process number (1-8)
            lot_number: LOT number
            start_time: Work start time
            complete_time: Work complete time
            defect_type: Defect type code
            defect_description: Optional defect description
            **kwargs: Additional process-specific data

        Returns:
            dict: process_data for the completion API
        """
        # Get base PASS data and add defect info
        base_data = ProcessDataGenerator.generate_pass_data(
            process_number, lot_number, start_time, complete_time, **kwargs
        )

        # Update result fields for FAIL
        base_data["defect_type"] = defect_type
        if defect_description:
            base_data["defect_description"] = defect_description

        # Update specific result fields based on process
        if process_number == 1:
            base_data["marking_result"] = "FAIL"
        elif process_number == 2:
            base_data["visual_inspection"] = "FAIL"
        elif process_number == 3:
            # Determine which sensor failed based on defect_type
            if defect_type == "SENSOR_TEMP_FAIL":
                base_data["temp_sensor"]["result"] = "FAIL"
            elif defect_type == "SENSOR_TOF_FAIL":
                base_data["tof_sensor"]["result"] = "FAIL"
        elif process_number == 4:
            base_data["upload_result"] = "FAIL"
        elif process_number == 5:
            if defect_type == "ASSEMBLY_ERROR":
                base_data["cable_connection"] = "FAIL"
            base_data["final_visual_check"] = "FAIL"
        elif process_number == 6:
            base_data["overall_result"] = "FAIL"
        elif process_number == 7:
            base_data["label_printed"] = False
        elif process_number == 8:
            base_data["final_result"] = "FAIL"
            base_data["packaging_complete"] = False

        return base_data

    @staticmethod
    def _generate_laser_marking_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 1: Laser Marking PASS data."""
        return {
            "lot_number_engraved": lot_number,
            "marking_result": "SUCCESS"
        }

    @staticmethod
    def _generate_lma_assembly_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 2: LMA Assembly PASS data."""
        return {
            "assembly_time": round(assembly_time, 2),
            "visual_inspection": "PASS"
        }

    @staticmethod
    def _generate_sensor_inspection_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 3: Sensor Inspection PASS data."""
        return {
            "temp_sensor": {
                "measured_temp": 60.0,
                "target_temp": 60.0,
                "tolerance": 1.0,
                "result": "PASS"
            },
            "tof_sensor": {
                "i2c_communication": True,
                "result": "PASS"
            }
        }

    @staticmethod
    def _generate_firmware_upload_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 4: Firmware Upload PASS data."""
        return {
            "firmware_version": kwargs.get("firmware_version", "v1.0.0"),
            "upload_result": "SUCCESS"
        }

    @staticmethod
    def _generate_robot_assembly_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 5: Robot Assembly PASS data."""
        return {
            "assembly_time": round(assembly_time, 2),
            "cable_connection": "OK",
            "final_visual_check": "PASS"
        }

    @staticmethod
    def _generate_performance_test_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 6: Performance Test PASS data."""
        return {
            "test_results": kwargs.get("test_results", []),
            "overall_result": "PASS",
            "test_duration_seconds": round(assembly_time * 60, 0),
            "tested_at": datetime.now().isoformat()
        }

    @staticmethod
    def _generate_label_printing_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 7: Label Printing PASS data."""
        return {
            "serial_number": kwargs.get("serial_number", ""),
            "label_printed": True,
            "print_time": datetime.now().isoformat()
        }

    @staticmethod
    def _generate_packaging_pass(lot_number: str, assembly_time: float, **kwargs: Any) -> Dict[str, Any]:
        """Process 8: Packaging + Visual Inspection PASS data."""
        return {
            "visual_defects": [],
            "packaging_complete": True,
            "final_result": "PASS"
        }
