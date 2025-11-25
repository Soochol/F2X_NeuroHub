"""
Pydantic schemas for measurement data in process completion.

Defines the structure for measurement data sent from inspection/assembly equipment
via PySide app to the backend API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MeasurementSpec(BaseModel):
    """Specification (min/max/target) for a measurement."""
    min: Optional[float] = Field(None, description="Minimum acceptable value")
    max: Optional[float] = Field(None, description="Maximum acceptable value")
    target: Optional[float] = Field(None, description="Target/nominal value")


class MeasurementItem(BaseModel):
    """Single measurement item from equipment."""
    code: str = Field(..., description="Measurement code (e.g., VOLTAGE, TORQUE_01)")
    name: str = Field(..., description="Measurement name in Korean")
    value: float = Field(..., description="Measured value")
    unit: Optional[str] = Field(None, description="Unit (V, A, Nm, N, mm, etc.)")
    spec: Optional[MeasurementSpec] = Field(None, description="Specification")
    result: str = Field(..., description="Result: PASS or FAIL")


class DefectItem(BaseModel):
    """Defect information when measurement fails."""
    code: str = Field(..., description="Measurement code that failed")
    reason: str = Field(..., description="Failure reason")


class EquipmentMeasurementData(BaseModel):
    """
    Data format sent from equipment SW to PySide app via TCP.

    This is the JSON structure that inspection/assembly equipment sends.
    """
    result: str = Field(..., description="Overall result: PASS or FAIL")
    measurements: List[MeasurementItem] = Field(
        default_factory=list,
        description="List of measurement items"
    )
    defects: List[DefectItem] = Field(
        default_factory=list,
        description="List of defects (when result=FAIL)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "result": "PASS",
                "measurements": [
                    {
                        "code": "VOLTAGE",
                        "name": "전압",
                        "value": 12.05,
                        "unit": "V",
                        "spec": {"min": 11.8, "max": 12.4, "target": 12.0},
                        "result": "PASS"
                    },
                    {
                        "code": "CURRENT",
                        "name": "전류",
                        "value": 2.35,
                        "unit": "A",
                        "spec": {"min": 2.0, "max": 3.0, "target": 2.5},
                        "result": "PASS"
                    }
                ],
                "defects": []
            }
        }


class ProcessMeasurementData(BaseModel):
    """
    Measurement data structure stored in process_data.measurements (JSONB).

    This wraps the measurement items for API transmission and DB storage.
    """
    items: List[MeasurementItem] = Field(
        default_factory=list,
        description="List of measurement items"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "code": "VOLTAGE",
                        "name": "전압",
                        "value": 12.05,
                        "unit": "V",
                        "spec": {"min": 11.8, "max": 12.4, "target": 12.0},
                        "result": "PASS"
                    }
                ]
            }
        }
