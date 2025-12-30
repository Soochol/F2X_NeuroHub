# 05. Sequence Package - 상세 설계

## 구현 체크리스트

> Phase 2.2 ~ 2.4 - 시퀀스 패키지 핵심 구현

### 2.2 SequenceLoader 구현
- [x] `station_service/sequence/__init__.py` 생성
- [x] `station_service/sequence/loader.py` - SequenceLoader 클래스
  - [x] `discover_packages()` - 패키지 스캔
  - [x] `load_package()` - 단일 패키지 로딩
  - [x] `validate_manifest()` - Manifest 검증
  - [x] `load_sequence_class()` - 시퀀스 클래스 동적 로딩

### 2.3 SequenceExecutor 구현
- [x] `station_service/sequence/executor.py` - SequenceExecutor 클래스
  - [x] `run()` - 시퀀스 실행 메인 루프
  - [x] `_execute_step()` - 단일 스텝 실행
  - [x] `_handle_timeout()` - 타임아웃 처리
  - [x] `_handle_retry()` - 재시도 로직
  - [x] 콜백: `on_step_start`, `on_step_complete`, `on_log`

### 2.4 Driver 인터페이스
- [x] `station_service/sequence/drivers/__init__.py`
- [x] `station_service/sequence/drivers/base.py` - BaseDriver ABC
  - [x] `async connect()`
  - [x] `async disconnect()`
  - [x] `async execute(command, params)`
  - [x] `is_connected` 프로퍼티

### 데코레이터
- [x] `station_service/sequence/decorators.py`
  - [x] `@sequence` - 시퀀스 클래스 데코레이터
  - [x] `@step` - 스텝 메서드 데코레이터
  - [x] `@cleanup` - 클린업 스텝 데코레이터

---

## Document Information
- **Version**: 1.2.0
- **Date**: 2025-12-30
- **Type**: Design Specification
- **Related**: [04-sequence-package-spec.md](./04-sequence-package-spec.md) (요구사항 명세)

---

## 1. 개요

이 문서는 Sequence Package의 상세 구현 설계를 다룹니다. 요구사항, 스키마 정의, 데코레이터 명세는 [03-sequence-package-spec.md](./03-sequence-package-spec.md)를 참조하세요.

### 1.1 Purpose
This document provides comprehensive implementation details for the **Sequence Package** component - including Pydantic models, executor implementation, validation logic, and testing strategies.

### 1.2 Design Principles

| Principle | Description |
|-----------|-------------|
| **Self-contained** | All required code (drivers, utils) bundled together |
| **Portable** | Deploy by folder copy, no external dependencies on Station Service |
| **Versioned** | Semantic versioning with change tracking |
| **Documented** | manifest.yaml provides complete self-documentation |
| **Type-Safe** | Full type hints and Pydantic validation |
| **Async-First** | All I/O operations are async/await |

---

## 2. Architecture Overview

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SEQUENCE PACKAGE                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        manifest.yaml                                 │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │   │
│  │  │   Metadata    │  │   Hardware    │  │     Parameters        │   │   │
│  │  │ name, version │  │   Definitions │  │   UI-editable         │   │   │
│  │  │ author, desc  │  │   + configs   │  │   test settings       │   │   │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐   │
│  │         sequence.py              │  │          drivers/            │   │
│  │                                  │  │                              │   │
│  │  @sequence                       │  │  ┌────────────────────────┐ │   │
│  │  class TestSequence:             │  │  │      base.py           │ │   │
│  │                                  │  │  │  BaseDriver(ABC)       │ │   │
│  │    @parameter                    │  │  └────────────────────────┘ │   │
│  │    def voltage_limit(): ...      │  │                              │   │
│  │                                  │  │  ┌────────────────────────┐ │   │
│  │    @step(order=1)                │  │  │      dmm.py            │ │   │
│  │    async def initialize(): ...   │  │  │  KeysightDMM(Base)     │ │   │
│  │                                  │  │  └────────────────────────┘ │   │
│  │    @step(order=2)                │  │                              │   │
│  │    async def measure(): ...      │  │  ┌────────────────────────┐ │   │
│  │                                  │  │  │   power_supply.py      │ │   │
│  │    @step(cleanup=True)           │  │  │  AgilentPower(Base)    │ │   │
│  │    async def finalize(): ...     │  │  └────────────────────────┘ │   │
│  │                                  │  │                              │   │
│  └──────────────────────────────────┘  └──────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐                                      │
│  │          utils/ (optional)       │                                      │
│  │  calculations.py, helpers.py     │                                      │
│  └──────────────────────────────────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Package Structure

```
sequences/
└── pcb_voltage_test/              # Package folder name = Package ID
    ├── __init__.py                # Package initialization
    ├── manifest.yaml              # Metadata, hardware, parameters
    ├── sequence.py                # Main sequence class with decorators
    │
    ├── drivers/                   # Hardware drivers (bundled)
    │   ├── __init__.py
    │   ├── base.py                # Optional: BaseDriver ABC
    │   ├── dmm.py                 # Digital multimeter driver
    │   └── power_supply.py        # Power supply driver
    │
    └── utils/                     # Optional utilities
        ├── __init__.py
        └── calculations.py        # Helper functions
```

---

## 3. Core Components

### 3.1 Manifest Schema (manifest.yaml)

The manifest provides complete package metadata and serves as the single source of truth.

```yaml
# ============================================
# BASIC INFORMATION
# ============================================
name: pcb_voltage_test              # Package ID (matches folder name)
version: 1.2.0                      # Semantic version
author: "Engineering Team"
description: "PCB Voltage Test Sequence"
created_at: "2025-01-15"
updated_at: "2025-01-20"

# ============================================
# ENTRY POINT
# ============================================
entry_point:
  module: sequence                  # sequence.py
  class: PCBVoltageTest             # Class name in sequence.py

# ============================================
# HARDWARE DEFINITIONS
# ============================================
# Key = Hardware ID used in sequence code
# Driver paths are relative to package root
hardware:
  dmm:
    display_name: "디지털 멀티미터"
    driver: "./drivers/dmm.py"
    class: "KeysightDMM"
    description: "Voltage/current measurement"
    config_schema:                  # Station provides these values
      port:
        type: string
        required: true
        description: "Serial port (e.g., /dev/ttyUSB0)"
      baudrate:
        type: integer
        default: 9600
        options: [9600, 19200, 38400, 115200]
      timeout:
        type: float
        default: 1.0
        min: 0.1
        max: 30.0

  power:
    display_name: "파워 서플라이"
    driver: "./drivers/power_supply.py"
    class: "AgilentPowerSupply"
    description: "Power supply control"
    config_schema:
      ip:
        type: string
        required: true
        description: "Device IP address"
      port:
        type: integer
        default: 5025
      timeout:
        type: float
        default: 5.0

# ============================================
# SEQUENCE PARAMETERS (UI-editable)
# ============================================
parameters:
  voltage_limit:
    display_name: "전압 상한"
    type: float
    default: 5.5
    min: 0.0
    max: 50.0
    unit: "V"
    description: "Fail if exceeded"

  current_limit:
    display_name: "전류 상한"
    type: float
    default: 1.0
    min: 0.0
    max: 10.0
    unit: "A"

  test_points:
    display_name: "테스트 포인트 수"
    type: integer
    default: 10
    min: 1
    max: 100

  dut_type:
    display_name: "DUT 타입"
    type: string
    default: "TypeA"
    options: ["TypeA", "TypeB", "TypeC"]

  enable_aging:
    display_name: "에이징 테스트 활성화"
    type: boolean
    default: false

# ============================================
# DEPENDENCIES (optional)
# ============================================
dependencies:
  python:
    - pyserial>=3.5
    - numpy>=1.20.0
```

### 3.2 Manifest Pydantic Models

```python
# station-service/sequence/models.py

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Any, Optional, Literal
from enum import Enum

class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


class ConfigFieldSchema(BaseModel):
    """Hardware configuration field schema"""
    type: ParameterType
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    options: Optional[List[Any]] = None
    min: Optional[float] = None
    max: Optional[float] = None


class HardwareDefinition(BaseModel):
    """Hardware driver definition in manifest"""
    display_name: str
    driver: str = Field(..., description="Relative path to driver file")
    class_name: str = Field(..., alias="class")
    description: Optional[str] = None
    config_schema: Dict[str, ConfigFieldSchema] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class ParameterDefinition(BaseModel):
    """Sequence parameter definition"""
    display_name: str
    type: ParameterType
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[Any]] = None
    unit: Optional[str] = None
    description: Optional[str] = None

    @field_validator('default', mode='before')
    @classmethod
    def validate_default(cls, v, info):
        """Validate default value matches type"""
        return v


class EntryPoint(BaseModel):
    """Sequence class entry point"""
    module: str = Field(..., description="Python module name (without .py)")
    class_name: str = Field(..., alias="class")

    class Config:
        populate_by_name = True


class DependencySpec(BaseModel):
    """Package dependencies"""
    python: List[str] = Field(default_factory=list)


class SequenceManifest(BaseModel):
    """Complete manifest.yaml schema"""
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$')
    author: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    entry_point: EntryPoint
    hardware: Dict[str, HardwareDefinition] = Field(default_factory=dict)
    parameters: Dict[str, ParameterDefinition] = Field(default_factory=dict)
    dependencies: Optional[DependencySpec] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate package name is valid Python identifier"""
        if not v.isidentifier():
            raise ValueError(f"Package name must be valid identifier: {v}")
        return v
```

---

## 4. Decorator System

### 4.1 Decorator Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DECORATOR HIERARCHY                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  @sequence(name, description, version)                               │   │
│  │                                                                      │   │
│  │  Attaches _sequence_meta to class:                                   │   │
│  │  - name: str                                                         │   │
│  │  - description: str                                                  │   │
│  │  - version: str                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  @parameter(name, display_name, unit, description)                   │   │
│  │                                                                      │   │
│  │  Attaches _param_meta to property:                                   │   │
│  │  - name: str                                                         │   │
│  │  - display_name: str                                                 │   │
│  │  - unit: str                                                         │   │
│  │  - description: str                                                  │   │
│  │  - default_getter: Callable                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  @step(order, timeout, retry, cleanup, condition)                    │   │
│  │                                                                      │   │
│  │  Attaches _step_meta to async method:                                │   │
│  │  - order: int           (execution order, 1-based)                   │   │
│  │  - timeout: float       (seconds, default 60)                        │   │
│  │  - retry: int           (retry count, default 0)                     │   │
│  │  - cleanup: bool        (always execute on error, default False)     │   │
│  │  - condition: str       (parameter name for conditional exec)        │   │
│  │  - name: str            (method name)                                │   │
│  │  - description: str     (from docstring)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Decorator Implementation

```python
# station-service/sequence/decorators.py

from typing import Callable, Optional, Any, TypeVar
from functools import wraps
import asyncio
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class SequenceMeta:
    """Metadata attached to sequence class"""
    name: str
    description: str
    version: str


@dataclass
class StepMeta:
    """Metadata attached to step method"""
    order: int
    timeout: float
    retry: int
    cleanup: bool
    condition: Optional[str]
    name: str
    description: str


@dataclass
class ParameterMeta:
    """Metadata attached to parameter property"""
    name: str
    display_name: str
    unit: str
    description: str
    default_getter: Callable


def sequence(
    name: str,
    description: str = "",
    version: str = "1.0.0"
) -> Callable[[type], type]:
    """
    Sequence class decorator.

    Marks a class as a test sequence and attaches metadata.

    Args:
        name: Sequence display name
        description: Human-readable description
        version: Semantic version string

    Example:
        @sequence(
            name="PCB_Voltage_Test",
            description="PCB voltage measurement sequence"
        )
        class PCBVoltageTest:
            ...
    """
    def decorator(cls: type) -> type:
        cls._sequence_meta = SequenceMeta(
            name=name,
            description=description,
            version=version
        )
        return cls
    return decorator


def step(
    order: int,
    timeout: float = 60.0,
    retry: int = 0,
    cleanup: bool = False,
    condition: Optional[str] = None
) -> Callable:
    """
    Step method decorator.

    Marks an async method as a test step with execution metadata.

    Args:
        order: Execution order (1-based, must be unique)
        timeout: Maximum execution time in seconds
        retry: Number of retry attempts on failure
        cleanup: If True, always executes even on prior errors
        condition: Parameter name; step runs only if parameter is truthy

    Example:
        @step(order=1, timeout=30, retry=3)
        async def initialize(self) -> Dict[str, Any]:
            '''Initialize equipment'''
            await self.power.reset()
            return {"status": "ready"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            return await func(self, *args, **kwargs)

        wrapper._step_meta = StepMeta(
            order=order,
            timeout=timeout,
            retry=retry,
            cleanup=cleanup,
            condition=condition,
            name=func.__name__,
            description=func.__doc__ or ""
        )
        return wrapper
    return decorator


def parameter(
    name: str,
    display_name: str = "",
    unit: str = "",
    description: str = ""
) -> Callable:
    """
    Parameter property decorator.

    Creates a property that can be externally configured by Station Service.
    Default value comes from the decorated method's return value.

    Args:
        name: Parameter identifier (must match manifest.yaml)
        display_name: Human-readable name for UI
        unit: Unit of measurement (e.g., "V", "A", "ms")
        description: Detailed description

    Example:
        @parameter(name="voltage_limit", display_name="Voltage Limit", unit="V")
        def voltage_limit(self) -> float:
            return 5.5  # Default value
    """
    def decorator(func: Callable[..., T]) -> property:
        @property
        @wraps(func)
        def wrapper(self) -> T:
            # Check for externally set value first
            param_attr = f"_param_{name}"
            if hasattr(self, param_attr):
                return getattr(self, param_attr)
            # Fall back to default from decorated method
            return func(self)

        # Store metadata on the getter function
        wrapper.fget._param_meta = ParameterMeta(
            name=name,
            display_name=display_name or name,
            unit=unit,
            description=description,
            default_getter=func
        )
        return wrapper
    return decorator
```

---

## 5. Driver Interface

### 5.1 Base Driver Abstract Class

```python
# Example: sequences/pcb_voltage_test/drivers/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseDriver(ABC):
    """
    Abstract base class for hardware drivers.

    All drivers in a sequence package should inherit from this class
    to ensure consistent interface and behavior.

    Lifecycle:
        1. __init__(config) - Store configuration
        2. connect() - Establish connection
        3. [operations] - Use driver methods
        4. disconnect() - Clean up connection
    """

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to hardware.

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close connection and release resources.

        Should not raise exceptions; log errors instead.
        """
        pass

    @abstractmethod
    async def reset(self) -> None:
        """
        Reset hardware to known state.

        Called during initialization and error recovery.
        """
        pass

    async def identify(self) -> str:
        """
        Query hardware identification.

        Returns:
            ID string (e.g., "*IDN?" response)
        """
        return "Unknown"

    async def is_connected(self) -> bool:
        """
        Check if connection is active.

        Returns:
            True if connected and responsive
        """
        return True

    async def self_test(self) -> Dict[str, Any]:
        """
        Run hardware self-test.

        Returns:
            Test results with pass/fail status
        """
        return {"pass": True, "message": "Self-test not implemented"}
```

### 5.2 Driver State Diagram

```
                    ┌───────────────┐
                    │   CREATED     │
                    │ (constructor) │
                    └───────┬───────┘
                            │
                            │ connect()
                            ▼
              ┌─────────────────────────────┐
              │         CONNECTING          │
              └─────────────┬───────────────┘
                            │
           ┌────────────────┼────────────────┐
           │ success        │                │ failure
           ▼                                 ▼
    ┌──────────────┐                 ┌──────────────┐
    │  CONNECTED   │                 │    ERROR     │
    │              │─────────────────│              │
    │ ready for    │     retry       │ log error    │
    │ operations   │<────────────────│ attempt      │
    └──────┬───────┘                 └──────────────┘
           │
           │ operations (measure, set, etc.)
           │
           │ disconnect() or error
           ▼
    ┌──────────────┐
    │ DISCONNECTED │
    └──────────────┘
```

### 5.3 Example DMM Driver

```python
# sequences/pcb_voltage_test/drivers/dmm.py

import serial
import asyncio
from typing import Optional
from .base import BaseDriver


class KeysightDMM(BaseDriver):
    """
    Keysight 34461A Digital Multimeter Driver

    Supports:
        - DC voltage measurement
        - DC current measurement
        - Resistance measurement
        - Channel selection (with multiplexer)

    Communication:
        - Serial (RS-232/USB-Serial)
        - SCPI command protocol
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0
    ):
        """
        Initialize DMM driver.

        Args:
            port: Serial port (e.g., "/dev/ttyUSB0")
            baudrate: Communication speed
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Establish serial connection"""
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            await self.reset()
            return True
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to DMM: {e}")

    async def disconnect(self) -> None:
        """Close serial connection"""
        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
            except Exception:
                pass
            finally:
                self._serial = None

    async def reset(self) -> None:
        """Reset DMM to default state"""
        await self._write("*RST")
        await self._write("*CLS")
        await asyncio.sleep(0.5)  # Allow reset to complete

    async def identify(self) -> str:
        """Query instrument identification"""
        return await self._query("*IDN?")

    async def is_connected(self) -> bool:
        """Check connection status"""
        if not self._serial or not self._serial.is_open:
            return False
        try:
            await self._query("*IDN?")
            return True
        except Exception:
            return False

    # ==================== Measurement Methods ====================

    async def measure_dc_voltage(
        self,
        range_: str = "AUTO"
    ) -> float:
        """
        Measure DC voltage.

        Args:
            range_: Measurement range ("AUTO", "0.1", "1", "10", "100", "1000")

        Returns:
            Measured voltage in Volts
        """
        if range_ != "AUTO":
            await self._write(f"CONF:VOLT:DC {range_}")
        else:
            await self._write("CONF:VOLT:DC")

        result = await self._query("READ?")
        return float(result)

    async def measure_dc_current(
        self,
        range_: str = "AUTO"
    ) -> float:
        """
        Measure DC current.

        Args:
            range_: Measurement range

        Returns:
            Measured current in Amperes
        """
        if range_ != "AUTO":
            await self._write(f"CONF:CURR:DC {range_}")
        else:
            await self._write("CONF:CURR:DC")

        result = await self._query("READ?")
        return float(result)

    async def measure_resistance(
        self,
        range_: str = "AUTO",
        four_wire: bool = False
    ) -> float:
        """
        Measure resistance.

        Args:
            range_: Measurement range
            four_wire: Use 4-wire measurement for precision

        Returns:
            Measured resistance in Ohms
        """
        mode = "FRES" if four_wire else "RES"
        if range_ != "AUTO":
            await self._write(f"CONF:{mode} {range_}")
        else:
            await self._write(f"CONF:{mode}")

        result = await self._query("READ?")
        return float(result)

    async def select_channel(self, channel: int) -> None:
        """
        Select multiplexer channel.

        Args:
            channel: Channel number (1-20)
        """
        await self._write(f"ROUT:CLOS (@{channel})")
        await asyncio.sleep(0.1)  # Relay settling time

    # ==================== Communication Methods ====================

    async def _write(self, command: str) -> None:
        """Send command to instrument"""
        async with self._lock:
            if not self._serial:
                raise ConnectionError("Not connected")
            self._serial.write(f"{command}\n".encode())

    async def _query(self, command: str) -> str:
        """Send command and read response"""
        async with self._lock:
            if not self._serial:
                raise ConnectionError("Not connected")

            self._serial.write(f"{command}\n".encode())
            response = self._serial.readline().decode().strip()

            if not response:
                raise TimeoutError(f"No response to: {command}")

            return response
```

---

## 6. Sequence Executor

### 6.1 Executor Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENCE EXECUTOR                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Initialization Phase                            │  │
│  │                                                                        │  │
│  │  1. Load manifest.yaml                                                 │  │
│  │  2. Validate manifest schema                                           │  │
│  │  3. Load sequence class (entry_point)                                  │  │
│  │  4. Create driver instances                                            │  │
│  │  5. Connect all drivers                                                │  │
│  │  6. Instantiate sequence (inject drivers)                              │  │
│  │  7. Extract step metadata from decorators                              │  │
│  │  8. Sort steps by order                                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Execution Phase                                 │  │
│  │                                                                        │  │
│  │  for each step in sorted_steps:                                        │  │
│  │      │                                                                 │  │
│  │      ├─► Check condition (skip if condition param is False)           │  │
│  │      │                                                                 │  │
│  │      ├─► Emit STEP_START event                                        │  │
│  │      │                                                                 │  │
│  │      ├─► Execute with timeout and retry logic                         │  │
│  │      │   │                                                             │  │
│  │      │   ├─► Success: Store result, emit STEP_COMPLETE                │  │
│  │      │   │                                                             │  │
│  │      │   └─► Failure: Retry or fail based on config                   │  │
│  │      │       │                                                         │  │
│  │      │       └─► If not cleanup step: break execution                 │  │
│  │      │                                                                 │  │
│  │      └─► If stopped flag: break execution                             │  │
│  │                                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                     │                                        │
│                                     ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Cleanup Phase                                   │  │
│  │                                                                        │  │
│  │  for each cleanup_step:                                                │  │
│  │      Execute (ignore errors)                                           │  │
│  │                                                                        │  │
│  │  Disconnect all drivers                                                │  │
│  │  Emit SEQUENCE_COMPLETE event                                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Executor Implementation

```python
# station-service/sequence/executor.py

import asyncio
import importlib.util
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from datetime import datetime
import yaml

from .models import SequenceManifest
from .decorators import StepMeta


@dataclass
class StepResult:
    """Result of a single step execution"""
    name: str
    order: int
    passed: bool
    duration: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TestFailure(Exception):
    """Raised when a test step fails"""

    def __init__(self, message: str, **data):
        super().__init__(message)
        self.message = message
        self.data = data


class TestSkipped(Exception):
    """Raised when a test step should be skipped"""
    pass


class SequenceExecutor:
    """
    Executes sequence packages.

    Handles:
        - Package loading and validation
        - Driver lifecycle management
        - Step execution with retry/timeout
        - Result collection and event emission
    """

    def __init__(
        self,
        package_path: str,
        hardware_config: Dict[str, Dict[str, Any]]
    ):
        """
        Initialize executor.

        Args:
            package_path: Path to sequence package folder
            hardware_config: Station-provided hardware configuration
        """
        self.package_path = Path(package_path)
        self.hardware_config = hardware_config

        self.manifest: Optional[SequenceManifest] = None
        self.sequence_class: Optional[type] = None
        self.sequence_instance: Optional[Any] = None
        self.drivers: Dict[str, Any] = {}
        self.parameters: Dict[str, Any] = {}

        self._running = False
        self._stopped = False
        self._current_step: Optional[str] = None

    async def initialize(self) -> None:
        """
        Initialize executor: load package, create drivers, instantiate sequence.
        """
        # Load and validate manifest
        self.manifest = self._load_manifest()

        # Load sequence class
        self.sequence_class = self._load_sequence_class()

        # Create and connect drivers
        for hw_name, hw_spec in self.manifest.hardware.items():
            driver = await self._create_driver(hw_name, hw_spec)
            self.drivers[hw_name] = driver

        # Instantiate sequence with driver injection
        self.sequence_instance = self.sequence_class(**self.drivers)

    def set_parameters(self, params: Dict[str, Any]) -> None:
        """
        Apply runtime parameters to sequence.

        Args:
            params: Parameter name -> value mapping
        """
        self.parameters = params

        for name, value in params.items():
            # Set as private attribute that @parameter decorator reads
            setattr(self.sequence_instance, f"_param_{name}", value)

    async def run(
        self,
        on_step_start: Optional[Callable] = None,
        on_step_complete: Optional[Callable] = None,
        on_log: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute the sequence.

        Args:
            on_step_start: Callback(step_name, step_index)
            on_step_complete: Callback(step_name, result)
            on_log: Callback(level, message)

        Returns:
            Complete execution result
        """
        self._running = True
        self._stopped = False

        results = {
            "sequence": self.manifest.name,
            "version": self.manifest.version,
            "started_at": datetime.utcnow().isoformat(),
            "steps": [],
            "overall_pass": True
        }

        # Get and sort steps
        steps = self._extract_steps()
        cleanup_steps = [s for s in steps if s["cleanup"]]
        normal_steps = [s for s in steps if not s["cleanup"]]

        try:
            # Execute normal steps
            for step_meta in normal_steps:
                if self._stopped:
                    break

                # Check condition
                if not self._check_condition(step_meta):
                    results["steps"].append({
                        "name": step_meta["name"],
                        "order": step_meta["order"],
                        "status": "skipped",
                        "pass": True
                    })
                    continue

                # Execute step
                step_result = await self._execute_step(
                    step_meta,
                    on_step_start,
                    on_step_complete,
                    on_log
                )
                results["steps"].append(step_result)

                if not step_result["pass"]:
                    results["overall_pass"] = False
                    break

        finally:
            # Always execute cleanup steps
            for step_meta in cleanup_steps:
                try:
                    step_result = await self._execute_step(
                        step_meta,
                        on_step_start,
                        on_step_complete,
                        on_log
                    )
                    results["steps"].append(step_result)
                except Exception:
                    pass  # Ignore cleanup errors

        results["completed_at"] = datetime.utcnow().isoformat()
        self._running = False

        return results

    async def stop(self) -> None:
        """Request sequence stop (graceful)"""
        self._stopped = True

    async def cleanup(self) -> None:
        """Disconnect all drivers"""
        for driver in self.drivers.values():
            try:
                await driver.disconnect()
            except Exception:
                pass

    async def get_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return {
            "running": self._running,
            "stopped": self._stopped,
            "current_step": self._current_step,
            "sequence": self.manifest.name if self.manifest else None
        }

    # ==================== Private Methods ====================

    def _load_manifest(self) -> SequenceManifest:
        """Load and validate manifest.yaml"""
        manifest_path = self.package_path / "manifest.yaml"

        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = yaml.safe_load(f)

        return SequenceManifest(**data)

    def _load_sequence_class(self) -> type:
        """Dynamically load sequence class from entry_point"""
        entry = self.manifest.entry_point
        module_path = self.package_path / f"{entry.module}.py"

        if not module_path.exists():
            raise FileNotFoundError(f"Sequence module not found: {module_path}")

        # Dynamic import
        spec = importlib.util.spec_from_file_location(
            entry.module,
            module_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        sequence_class = getattr(module, entry.class_name)

        # Verify it has sequence decorator
        if not hasattr(sequence_class, "_sequence_meta"):
            raise ValueError(
                f"Class {entry.class_name} is not decorated with @sequence"
            )

        return sequence_class

    async def _create_driver(
        self,
        hw_name: str,
        hw_spec: Any
    ) -> Any:
        """Create driver instance and establish connection"""
        driver_path = self.package_path / hw_spec.driver

        if not driver_path.exists():
            raise FileNotFoundError(f"Driver not found: {driver_path}")

        # Dynamic import
        spec = importlib.util.spec_from_file_location(hw_name, driver_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        driver_class = getattr(module, hw_spec.class_name)

        # Get configuration from station config
        config = self.hardware_config.get(hw_name, {})

        # Instantiate and connect
        driver = driver_class(**config)
        await driver.connect()

        return driver

    def _extract_steps(self) -> List[Dict[str, Any]]:
        """Extract step metadata from sequence instance"""
        steps = []

        for name in dir(self.sequence_instance):
            method = getattr(self.sequence_instance, name)
            if hasattr(method, "_step_meta"):
                meta: StepMeta = method._step_meta
                steps.append({
                    "func": method,
                    "name": meta.name,
                    "order": meta.order,
                    "timeout": meta.timeout,
                    "retry": meta.retry,
                    "cleanup": meta.cleanup,
                    "condition": meta.condition,
                    "description": meta.description
                })

        # Sort by order
        steps.sort(key=lambda x: x["order"])
        return steps

    def _check_condition(self, step_meta: Dict[str, Any]) -> bool:
        """Check if step should execute based on condition parameter"""
        condition = step_meta.get("condition")
        if not condition:
            return True

        # Get parameter value
        value = getattr(self.sequence_instance, condition, False)
        return bool(value)

    async def _execute_step(
        self,
        step_meta: Dict[str, Any],
        on_step_start: Optional[Callable],
        on_step_complete: Optional[Callable],
        on_log: Optional[Callable]
    ) -> Dict[str, Any]:
        """Execute a single step with timeout and retry"""
        step_name = step_meta["name"]
        step_func = step_meta["func"]

        self._current_step = step_name

        # Emit start event
        if on_step_start:
            await on_step_start(step_name, step_meta["order"])

        result = {
            "name": step_name,
            "order": step_meta["order"],
            "pass": True,
            "error": None,
            "data": None,
            "duration": 0
        }

        start_time = asyncio.get_event_loop().time()

        # Retry loop
        for attempt in range(step_meta["retry"] + 1):
            try:
                # Execute with timeout
                data = await asyncio.wait_for(
                    step_func(),
                    timeout=step_meta["timeout"]
                )
                result["data"] = data
                result["pass"] = True
                break

            except asyncio.TimeoutError:
                result["pass"] = False
                result["error"] = f"Timeout after {step_meta['timeout']}s"

            except TestFailure as e:
                result["pass"] = False
                result["error"] = str(e)
                result["data"] = e.data

            except Exception as e:
                result["pass"] = False
                result["error"] = str(e)

            # Retry if not last attempt
            if attempt < step_meta["retry"]:
                if on_log:
                    await on_log(
                        "warning",
                        f"Step {step_name} failed, retrying ({attempt + 1}/{step_meta['retry']})"
                    )
                await asyncio.sleep(1)

        result["duration"] = asyncio.get_event_loop().time() - start_time

        # Emit complete event
        if on_step_complete:
            await on_step_complete(step_name, result)

        self._current_step = None
        return result
```

---

## 7. Example Sequence Implementation

### 7.1 Complete Sequence Example

```python
# sequences/pcb_voltage_test/sequence.py

import asyncio
from typing import Dict, Any

from station.sequence import sequence, step, parameter
from station.exceptions import TestFailure, TestSkipped
from .drivers.dmm import KeysightDMM
from .drivers.power_supply import AgilentPowerSupply


@sequence(
    name="PCB_Voltage_Test",
    description="PCB voltage measurement and validation sequence",
    version="1.2.0"
)
class PCBVoltageTest:
    """
    PCB Voltage Test Sequence

    This sequence performs voltage measurements on PCB test points
    and validates against configured limits.

    Steps:
        1. Initialize - Reset equipment
        2. Power On Test - Apply power and check current
        3. Voltage Measurement - Measure all test points
        4. Aging Test - Extended test (optional)
        5. Finalize - Power off and cleanup
    """

    # ==================== Parameters ====================
    # These match manifest.yaml parameter definitions

    @parameter(name="voltage_limit", display_name="Voltage Limit", unit="V")
    def voltage_limit(self) -> float:
        """Maximum allowable voltage"""
        return 5.5

    @parameter(name="current_limit", display_name="Current Limit", unit="A")
    def current_limit(self) -> float:
        """Maximum allowable current"""
        return 1.0

    @parameter(name="test_points", display_name="Test Points")
    def test_points(self) -> int:
        """Number of measurement points"""
        return 10

    @parameter(name="dut_type", display_name="DUT Type")
    def dut_type(self) -> str:
        """Device under test variant"""
        return "TypeA"

    @parameter(name="enable_aging", display_name="Enable Aging")
    def enable_aging(self) -> bool:
        """Whether to run aging test"""
        return False

    # ==================== Constructor ====================

    def __init__(
        self,
        dmm: KeysightDMM,
        power: AgilentPowerSupply
    ):
        """
        Drivers are injected by the executor based on manifest hardware IDs.

        Args:
            dmm: Digital multimeter instance
            power: Power supply instance
        """
        self.dmm = dmm
        self.power = power
        self.results: Dict[str, Any] = {}

    # ==================== Test Steps ====================

    @step(order=1, timeout=30, retry=3)
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize Equipment

        Reset power supply and DMM to known state.
        Perform self-test on DMM.
        """
        # Reset power supply
        await self.power.reset()
        await self.power.set_output(voltage=0, current_limit=self.current_limit)

        # Reset and identify DMM
        await self.dmm.reset()
        idn = await self.dmm.identify()

        return {
            "status": "initialized",
            "dmm_id": idn,
            "power_ready": True
        }

    @step(order=2, timeout=60)
    async def power_on_test(self) -> Dict[str, Any]:
        """
        Power On Test

        Apply power and verify initial current is within limits.
        """
        # Apply power
        await self.power.set_output(
            voltage=5.0,
            current_limit=self.current_limit
        )
        await self.power.enable()

        # Wait for stabilization
        await asyncio.sleep(0.5)

        # Measure current
        current = await self.dmm.measure_dc_current()

        # Validate
        if current > self.current_limit:
            raise TestFailure(
                f"Current exceeded: {current}A > {self.current_limit}A",
                actual=current,
                limit=self.current_limit
            )

        self.results["initial_current"] = current

        return {
            "voltage": 5.0,
            "current": current,
            "pass": True
        }

    @step(order=3, timeout=120)
    async def voltage_measurement(self) -> Dict[str, Any]:
        """
        Voltage Measurement

        Measure voltage at all test points.
        """
        measurements = []
        all_pass = True

        for point in range(self.test_points):
            # Select channel based on DUT type
            channel = self._get_channel_for_point(point)
            await self.dmm.select_channel(channel)

            # Measure
            voltage = await self.dmm.measure_dc_voltage()

            # Validate
            passed = voltage <= self.voltage_limit
            if not passed:
                all_pass = False

            measurements.append({
                "point": point,
                "channel": channel,
                "voltage": round(voltage, 4),
                "limit": self.voltage_limit,
                "pass": passed
            })

        if not all_pass:
            failed_points = [m for m in measurements if not m["pass"]]
            raise TestFailure(
                f"Voltage exceeded at {len(failed_points)} points",
                measurements=measurements,
                failed_count=len(failed_points)
            )

        return {
            "measurements": measurements,
            "all_pass": all_pass,
            "total_points": len(measurements)
        }

    @step(order=4, timeout=300, condition="enable_aging")
    async def aging_test(self) -> Dict[str, Any]:
        """
        Aging Test (Conditional)

        Extended operation test. Only runs if enable_aging is True.
        """
        start_voltage = await self.dmm.measure_dc_voltage()

        # Run for extended period
        await asyncio.sleep(60)

        end_voltage = await self.dmm.measure_dc_voltage()
        drift = abs(end_voltage - start_voltage)

        return {
            "start_voltage": start_voltage,
            "end_voltage": end_voltage,
            "drift": drift,
            "duration_seconds": 60,
            "pass": drift < 0.1
        }

    @step(order=5, cleanup=True)
    async def finalize(self) -> Dict[str, Any]:
        """
        Finalize (Cleanup)

        Turn off power and reset equipment.
        Always runs, even if earlier steps failed.
        """
        try:
            await self.power.disable()
            await self.power.set_output(voltage=0, current_limit=0)
        except Exception:
            pass  # Ignore errors in cleanup

        return {
            "status": "finalized",
            "power_off": True
        }

    # ==================== Helper Methods ====================

    def _get_channel_for_point(self, point: int) -> int:
        """Map test point to DMM channel based on DUT type"""
        channel_maps = {
            "TypeA": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "TypeB": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19],
            "TypeC": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        }
        channels = channel_maps.get(self.dut_type, channel_maps["TypeA"])
        return channels[point % len(channels)]
```

---

## 8. Package Validation

### 8.1 Validation Rules

```python
# station-service/sequence/validator.py

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from .models import SequenceManifest


@dataclass
class ValidationError:
    """Validation error details"""
    code: str
    message: str
    field: Optional[str] = None


class PackageValidator:
    """
    Validates sequence package structure and content.

    Checks:
        - Required files exist
        - Manifest is valid YAML and schema-compliant
        - Entry point module and class exist
        - Driver files exist
        - Parameter types match declarations
        - Step orders are unique
    """

    def __init__(self, package_path: str):
        self.package_path = Path(package_path)
        self.errors: List[ValidationError] = []

    def validate(self) -> bool:
        """
        Run all validations.

        Returns:
            True if all validations pass
        """
        self.errors = []

        self._validate_structure()
        self._validate_manifest()
        self._validate_entry_point()
        self._validate_drivers()
        self._validate_steps()

        return len(self.errors) == 0

    def _validate_structure(self) -> None:
        """Check required files exist"""
        required_files = [
            "__init__.py",
            "manifest.yaml",
        ]

        for filename in required_files:
            if not (self.package_path / filename).exists():
                self.errors.append(ValidationError(
                    code="MISSING_FILE",
                    message=f"Required file not found: {filename}",
                    field=filename
                ))

        # Check drivers directory
        drivers_dir = self.package_path / "drivers"
        if not drivers_dir.exists() or not drivers_dir.is_dir():
            self.errors.append(ValidationError(
                code="MISSING_DIR",
                message="drivers/ directory not found"
            ))

    def _validate_manifest(self) -> None:
        """Validate manifest.yaml"""
        manifest_path = self.package_path / "manifest.yaml"

        if not manifest_path.exists():
            return  # Already reported in structure check

        try:
            import yaml
            with open(manifest_path) as f:
                data = yaml.safe_load(f)

            # Validate schema
            manifest = SequenceManifest(**data)

            # Validate folder name matches package name
            if self.package_path.name != manifest.name:
                self.errors.append(ValidationError(
                    code="NAME_MISMATCH",
                    message=f"Folder name '{self.package_path.name}' "
                            f"doesn't match manifest name '{manifest.name}'",
                    field="name"
                ))

        except yaml.YAMLError as e:
            self.errors.append(ValidationError(
                code="INVALID_YAML",
                message=f"Invalid YAML: {e}"
            ))
        except Exception as e:
            self.errors.append(ValidationError(
                code="INVALID_SCHEMA",
                message=f"Schema validation failed: {e}"
            ))

    def _validate_entry_point(self) -> None:
        """Validate entry point module and class"""
        try:
            import yaml
            manifest_path = self.package_path / "manifest.yaml"
            with open(manifest_path) as f:
                data = yaml.safe_load(f)

            manifest = SequenceManifest(**data)
            module_path = self.package_path / f"{manifest.entry_point.module}.py"

            if not module_path.exists():
                self.errors.append(ValidationError(
                    code="MISSING_MODULE",
                    message=f"Entry point module not found: {module_path}",
                    field="entry_point.module"
                ))
                return

            # Try to load and verify class exists
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                manifest.entry_point.module,
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, manifest.entry_point.class_name):
                self.errors.append(ValidationError(
                    code="MISSING_CLASS",
                    message=f"Class '{manifest.entry_point.class_name}' "
                            f"not found in {module_path}",
                    field="entry_point.class"
                ))

        except Exception as e:
            self.errors.append(ValidationError(
                code="ENTRY_POINT_ERROR",
                message=f"Entry point validation failed: {e}"
            ))

    def _validate_drivers(self) -> None:
        """Validate all declared drivers exist"""
        try:
            import yaml
            manifest_path = self.package_path / "manifest.yaml"
            with open(manifest_path) as f:
                data = yaml.safe_load(f)

            manifest = SequenceManifest(**data)

            for hw_name, hw_spec in manifest.hardware.items():
                driver_path = self.package_path / hw_spec.driver

                if not driver_path.exists():
                    self.errors.append(ValidationError(
                        code="MISSING_DRIVER",
                        message=f"Driver file not found: {hw_spec.driver}",
                        field=f"hardware.{hw_name}.driver"
                    ))

        except Exception:
            pass  # Already reported in manifest validation

    def _validate_steps(self) -> None:
        """Validate step decorators and uniqueness"""
        try:
            import yaml
            manifest_path = self.package_path / "manifest.yaml"
            with open(manifest_path) as f:
                data = yaml.safe_load(f)

            manifest = SequenceManifest(**data)
            module_path = self.package_path / f"{manifest.entry_point.module}.py"

            import importlib.util
            spec = importlib.util.spec_from_file_location(
                manifest.entry_point.module,
                module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            cls = getattr(module, manifest.entry_point.class_name)

            # Check for @sequence decorator
            if not hasattr(cls, "_sequence_meta"):
                self.errors.append(ValidationError(
                    code="MISSING_DECORATOR",
                    message=f"Class missing @sequence decorator"
                ))

            # Collect step orders
            step_orders = []
            for name in dir(cls):
                method = getattr(cls, name)
                if hasattr(method, "_step_meta"):
                    order = method._step_meta.order
                    if order in step_orders:
                        self.errors.append(ValidationError(
                            code="DUPLICATE_ORDER",
                            message=f"Duplicate step order: {order}",
                            field=name
                        ))
                    step_orders.append(order)

            if not step_orders:
                self.errors.append(ValidationError(
                    code="NO_STEPS",
                    message="No @step decorated methods found"
                ))

        except Exception:
            pass  # Already reported elsewhere
```

---

## 9. Integration Points

### 9.1 Station Service Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATION SERVICE INTEGRATION                               │
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │  BatchManager   │                                                        │
│  │                 │                                                        │
│  │  - start_batch()│───────────────┐                                        │
│  │  - stop_batch() │               │                                        │
│  └─────────────────┘               ▼                                        │
│                         ┌──────────────────────┐                            │
│                         │    BatchProcess      │                            │
│                         │    (Child Process)   │                            │
│                         │                      │                            │
│                         │  ┌────────────────┐  │                            │
│                         │  │  BatchWorker   │  │                            │
│                         │  │                │  │                            │
│                         │  │  - Loads pkg   │  │                            │
│                         │  │  - Creates exe │  │                            │
│                         │  │  - Runs seq    │  │                            │
│                         │  └───────┬────────┘  │                            │
│                         │          │           │                            │
│                         │          ▼           │                            │
│                         │  ┌────────────────┐  │                            │
│                         │  │SequenceExecutor│  │                            │
│                         │  │                │  │                            │
│                         │  │  ┌──────────┐  │  │                            │
│                         │  │  │ Sequence │  │  │                            │
│                         │  │  │ Instance │  │  │                            │
│                         │  │  │          │  │  │                            │
│                         │  │  │ Drivers  │  │  │                            │
│                         │  │  └──────────┘  │  │                            │
│                         │  └────────────────┘  │                            │
│                         └──────────────────────┘                            │
│                                    │                                        │
│                                    │ ZeroMQ                                 │
│                                    ▼                                        │
│  ┌─────────────────┐     ┌─────────────────┐                               │
│  │   REST API      │     │   WebSocket     │                               │
│  │                 │     │                 │                               │
│  │  GET /batches   │     │  step_start     │                               │
│  │  POST /sequence │     │  step_complete  │                               │
│  └─────────────────┘     └─────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Backend (NeuroHub) Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NEUROHUB BACKEND INTEGRATION                            │
│                                                                             │
│  Station Service                          NeuroHub Backend                   │
│  ┌─────────────────┐                     ┌─────────────────┐                │
│  │                 │                     │                 │                │
│  │  Sync Engine    │ ───── REST ──────>  │  API Endpoints  │                │
│  │                 │                     │                 │                │
│  │  - Results      │  POST /results      │  - Store result │                │
│  │  - Heartbeat    │  POST /heartbeat    │  - Update status│                │
│  │                 │                     │                 │                │
│  └─────────────────┘                     └────────┬────────┘                │
│                                                   │                          │
│                                                   ▼                          │
│                                          ┌─────────────────┐                │
│                                          │   Database      │                │
│                                          │                 │                │
│                                          │  execution_logs │                │
│                                          │  step_results   │                │
│                                          │  process_data   │                │
│                                          └─────────────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Error Handling

### 10.1 Error Hierarchy

```python
# station-service/sequence/exceptions.py

class SequenceError(Exception):
    """Base exception for sequence operations"""
    pass


class PackageError(SequenceError):
    """Package structure or validation error"""
    pass


class ManifestError(PackageError):
    """Manifest parsing or validation error"""
    pass


class DriverError(SequenceError):
    """Hardware driver error"""
    pass


class ConnectionError(DriverError):
    """Driver connection error"""
    pass


class CommunicationError(DriverError):
    """Driver communication error"""
    pass


class ExecutionError(SequenceError):
    """Sequence execution error"""
    pass


class TestFailure(ExecutionError):
    """Test step failed validation"""

    def __init__(self, message: str, **data):
        super().__init__(message)
        self.message = message
        self.data = data


class TestSkipped(ExecutionError):
    """Test step was skipped"""
    pass


class TimeoutError(ExecutionError):
    """Step execution timeout"""
    pass
```

### 10.2 Error Flow Diagram

```
Step Execution
      │
      ▼
  ┌───────────────────┐
  │  Execute Step     │
  └─────────┬─────────┘
            │
      ┌─────┴─────┐
      │           │
   Success     Exception
      │           │
      ▼           ▼
  ┌─────────┐ ┌─────────────────────────────────┐
  │ Continue│ │  Exception Type?                 │
  │ to next │ │                                  │
  │ step    │ │  ┌───────────┬──────────┬──────┐│
  └─────────┘ │  │TestFailure│ Timeout  │Other ││
              │  └─────┬─────┴────┬─────┴───┬──┘│
              │        │          │         │   │
              │        ▼          ▼         ▼   │
              │  ┌──────────────────────────────┐│
              │  │ retry < max_retry?           ││
              │  │                              ││
              │  │   Yes → Wait → Retry         ││
              │  │   No  → Record failure       ││
              │  └──────────────────────────────┘│
              └────────────────┬─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ cleanup step?   │
                        │                 │
                        │  No  → Stop     │
                        │  Yes → Continue │
                        └─────────────────┘
```

---

## 11. Testing Strategy

### 11.1 Test Categories

| Category | Focus | Tools |
|----------|-------|-------|
| **Unit Tests** | Decorators, models, validators | pytest, unittest.mock |
| **Integration Tests** | Executor + mock drivers | pytest-asyncio |
| **Package Tests** | Example packages | pytest, fixtures |
| **E2E Tests** | Full station workflow | pytest, docker |

### 11.2 Mock Driver Example

```python
# tests/fixtures/mock_drivers.py

from typing import Any, Dict


class MockDMM:
    """Mock DMM for testing"""

    def __init__(self, **config):
        self.config = config
        self.connected = False
        self._voltage = 4.98
        self._current = 0.5

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def disconnect(self) -> None:
        self.connected = False

    async def reset(self) -> None:
        pass

    async def identify(self) -> str:
        return "Mock DMM v1.0"

    async def measure_dc_voltage(self, range_: str = "AUTO") -> float:
        return self._voltage

    async def measure_dc_current(self, range_: str = "AUTO") -> float:
        return self._current

    async def select_channel(self, channel: int) -> None:
        pass

    def set_voltage(self, voltage: float) -> None:
        """Test helper to set next voltage reading"""
        self._voltage = voltage


class MockPowerSupply:
    """Mock Power Supply for testing"""

    def __init__(self, **config):
        self.config = config
        self.connected = False
        self.enabled = False
        self.voltage = 0
        self.current_limit = 0

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def disconnect(self) -> None:
        self.connected = False

    async def reset(self) -> None:
        self.voltage = 0
        self.current_limit = 0
        self.enabled = False

    async def set_output(self, voltage: float, current_limit: float) -> None:
        self.voltage = voltage
        self.current_limit = current_limit

    async def enable(self) -> None:
        self.enabled = True

    async def disable(self) -> None:
        self.enabled = False
```

### 11.3 Test Example

```python
# tests/test_executor.py

import pytest
from pathlib import Path

from sequence.executor import SequenceExecutor
from tests.fixtures.mock_drivers import MockDMM, MockPowerSupply


@pytest.fixture
def test_package_path(tmp_path):
    """Create minimal test package"""
    pkg = tmp_path / "test_sequence"
    pkg.mkdir()

    # Create manifest
    manifest = pkg / "manifest.yaml"
    manifest.write_text("""
name: test_sequence
version: 1.0.0
entry_point:
  module: sequence
  class: TestSequence
hardware:
  dmm:
    display_name: DMM
    driver: ./drivers/dmm.py
    class: MockDMM
parameters:
  limit:
    type: float
    default: 5.0
""")

    # Create sequence
    sequence = pkg / "sequence.py"
    sequence.write_text("""
from station.sequence import sequence, step, parameter

@sequence(name="Test", description="Test sequence")
class TestSequence:
    @parameter(name="limit")
    def limit(self) -> float:
        return 5.0

    def __init__(self, dmm):
        self.dmm = dmm

    @step(order=1)
    async def test_step(self):
        voltage = await self.dmm.measure_dc_voltage()
        return {"voltage": voltage}
""")

    return pkg


@pytest.mark.asyncio
async def test_executor_runs_sequence(test_package_path):
    """Test executor runs sequence successfully"""
    executor = SequenceExecutor(
        str(test_package_path),
        hardware_config={"dmm": {"port": "COM1"}}
    )

    # Replace driver creation with mock
    executor.drivers = {"dmm": MockDMM()}

    await executor.initialize()
    result = await executor.run()

    assert result["overall_pass"] is True
    assert len(result["steps"]) == 1
    assert result["steps"][0]["data"]["voltage"] == 4.98
```

---

## 12. Future Enhancements (Recommended)

본 섹션은 현재 설계에서 식별된 개선 권고사항을 정리합니다.

### 12.1 우선순위 요약

| 우선순위 | 항목 | 이유 |
|---------|------|------|
| **High** | Mock/Simulation 모드 | 개발 생산성 향상, 실제 장비 없이 테스트 가능 |
| **High** | Checkpoint/Resume | 장시간 테스트 안정성, 중단 복구 |
| **High** | Equipment Abstraction Layer | 장비 교체 용이, 벤더 독립성 확보 |
| **Medium** | Step Context | Step 간 데이터 공유 표준화, 코드 품질 |
| **Medium** | Health Check | 장비 연결 상태 모니터링, 운영 안정성 |
| **Medium** | Logging 표준화 | 디버깅/분석 용이, 메트릭 수집 |
| **Medium** | Step Pre/Post Hooks | 공통 로직 재사용, AOP 패턴 지원 |
| **Medium** | Dynamic Parameter Dependencies | UI 사용성 향상, 조건부 파라미터 |
| **Medium** | Result Export Formats | 데이터 호환성, 분석 도구 연동 |
| **Low** | 병렬 Step 실행 | 특수 케이스에만 필요 |
| **Low** | Hot Reload | 개발 편의성 |
| **Low** | Sequence Templates | 코드 재사용, 대규모 프로젝트에 유용 |

---

### 12.2 Mock/Simulation 모드 지원

실제 장비 없이 개발 및 테스트할 수 있는 시뮬레이션 모드입니다.

#### manifest.yaml 확장

```yaml
hardware:
  dmm:
    display_name: "디지털 멀티미터"
    driver: "./drivers/dmm.py"
    class: "KeysightDMM"

    # [NEW] Mock 드라이버 설정
    mock:
      driver: "./drivers/dmm_mock.py"
      class: "MockDMM"
      description: "Simulation driver for testing"
```

#### station.yaml 설정

```yaml
batches:
  - id: batch_1
    name: "Batch 1"
    sequence_package: "sequences/pcb_test_v1"
    simulation_mode: true  # [NEW] Mock 드라이버 사용
    hardware:
      dmm:
        port: "/dev/ttyUSB0"  # 시뮬레이션 모드에서는 무시됨
```

#### Mock 드라이버 구현 예시

```python
# drivers/dmm_mock.py

import random
from typing import Optional


class MockDMM:
    """Simulation DMM for development and testing"""

    def __init__(self, **config):
        self.config = config
        self._voltage_base = 5.0
        self._noise = 0.05

    async def connect(self) -> bool:
        return True  # 항상 성공

    async def disconnect(self) -> None:
        pass

    async def reset(self) -> None:
        pass

    async def identify(self) -> str:
        return "Mock DMM v1.0 (Simulation)"

    async def measure_dc_voltage(self, range_: str = "AUTO") -> float:
        # 현실적인 노이즈 시뮬레이션
        noise = random.uniform(-self._noise, self._noise)
        return self._voltage_base + noise

    async def measure_dc_current(self, range_: str = "AUTO") -> float:
        return 0.5 + random.uniform(-0.01, 0.01)

    async def select_channel(self, channel: int) -> None:
        pass

    # 테스트 헬퍼 메서드
    def set_voltage(self, voltage: float) -> None:
        """Set base voltage for simulation"""
        self._voltage_base = voltage

    def set_failure_mode(self, fail: bool) -> None:
        """Simulate hardware failure"""
        self._fail = fail
```

---

### 12.3 Step Context (Step 간 데이터 공유)

Step 간 데이터 공유를 위한 표준화된 Context 객체입니다.

#### StepContext 클래스

```python
# station-service/sequence/context.py

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StepContext:
    """
    Step 실행 컨텍스트.

    Step 간 데이터 공유, 이전 Step 결과 접근,
    메트릭 수집을 위한 표준 인터페이스 제공.
    """

    sequence_name: str
    execution_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)

    # Step 결과 저장소
    _step_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 공유 데이터
    _shared_data: Dict[str, Any] = field(default_factory=dict)

    # 메트릭 수집
    _metrics: list = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        """공유 데이터 저장"""
        self._shared_data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """공유 데이터 조회"""
        return self._shared_data.get(key, default)

    def get_step_result(self, step_name: str) -> Optional[Dict[str, Any]]:
        """이전 Step 결과 조회"""
        return self._step_results.get(step_name)

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Dict[str, str] = None
    ) -> None:
        """메트릭 기록 (자동 수집)"""
        self._metrics.append({
            "name": name,
            "value": value,
            "unit": unit,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat()
        })

    def _record_step_result(self, step_name: str, result: Dict[str, Any]) -> None:
        """Executor가 호출 - Step 결과 저장"""
        self._step_results[step_name] = result
```

#### 시퀀스에서 사용

```python
@step(order=2)
async def power_on_test(self, ctx: StepContext) -> Dict[str, Any]:
    """
    Context 객체가 자동으로 주입됩니다.
    """
    # 이전 Step 결과 접근
    init_result = ctx.get_step_result("initialize")
    if init_result and init_result.get("dmm_id"):
        print(f"DMM: {init_result['dmm_id']}")

    # 측정 및 메트릭 기록
    current = await self.dmm.measure_dc_current()
    ctx.record_metric("initial_current", current, unit="A")

    # 다음 Step에서 사용할 데이터 저장
    ctx.set("initial_current", current)

    return {"voltage": 5.0, "current": current}
```

---

### 12.4 Hardware Health Check

장비 연결 상태를 주기적으로 확인하는 기능입니다.

#### manifest.yaml 확장

```yaml
hardware:
  dmm:
    display_name: "디지털 멀티미터"
    driver: "./drivers/dmm.py"
    class: "KeysightDMM"

    # [NEW] Health Check 설정
    health_check:
      enabled: true
      interval: 30          # 30초마다 체크
      timeout: 5            # 체크 타임아웃
      command: "*IDN?"      # 헬스체크 명령 (기본: identify())
      on_failure: "pause"   # pause | retry | abort | ignore
      retry_count: 3        # 실패 시 재시도 횟수
      retry_delay: 2        # 재시도 간격 (초)
```

#### Health Check Manager

```python
# station-service/sequence/health.py

import asyncio
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class HealthAction(str, Enum):
    PAUSE = "pause"       # 시퀀스 일시 중지
    RETRY = "retry"       # 재연결 시도
    ABORT = "abort"       # 시퀀스 중단
    IGNORE = "ignore"     # 무시하고 계속


@dataclass
class HealthCheckResult:
    hardware_id: str
    healthy: bool
    response_time: float
    error: Optional[str] = None


class HealthCheckManager:
    """
    드라이버 Health Check 관리자.

    주기적으로 드라이버 상태를 확인하고,
    실패 시 설정된 액션을 실행합니다.
    """

    def __init__(
        self,
        drivers: Dict[str, Any],
        health_configs: Dict[str, dict],
        on_failure: Callable[[str, HealthAction], None] = None
    ):
        self.drivers = drivers
        self.health_configs = health_configs
        self.on_failure = on_failure
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False

    async def start(self) -> None:
        """Health Check 시작"""
        self._running = True

        for hw_id, config in self.health_configs.items():
            if config.get("enabled", False):
                task = asyncio.create_task(
                    self._check_loop(hw_id, config)
                )
                self._tasks[hw_id] = task

    async def stop(self) -> None:
        """Health Check 중지"""
        self._running = False

        for task in self._tasks.values():
            task.cancel()

        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()

    async def _check_loop(self, hw_id: str, config: dict) -> None:
        """개별 드라이버 Health Check 루프"""
        interval = config.get("interval", 30)
        timeout = config.get("timeout", 5)
        action = HealthAction(config.get("on_failure", "pause"))

        while self._running:
            await asyncio.sleep(interval)

            result = await self._check_driver(hw_id, timeout)

            if not result.healthy:
                # 재시도
                for i in range(config.get("retry_count", 3)):
                    await asyncio.sleep(config.get("retry_delay", 2))
                    result = await self._check_driver(hw_id, timeout)
                    if result.healthy:
                        break

                # 여전히 실패하면 액션 실행
                if not result.healthy and self.on_failure:
                    await self.on_failure(hw_id, action)

    async def _check_driver(
        self,
        hw_id: str,
        timeout: float
    ) -> HealthCheckResult:
        """단일 드라이버 Health Check"""
        driver = self.drivers.get(hw_id)
        if not driver:
            return HealthCheckResult(
                hardware_id=hw_id,
                healthy=False,
                response_time=0,
                error="Driver not found"
            )

        start = asyncio.get_event_loop().time()

        try:
            await asyncio.wait_for(
                driver.is_connected(),
                timeout=timeout
            )

            response_time = asyncio.get_event_loop().time() - start

            return HealthCheckResult(
                hardware_id=hw_id,
                healthy=True,
                response_time=response_time
            )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                hardware_id=hw_id,
                healthy=False,
                response_time=timeout,
                error="Health check timeout"
            )
        except Exception as e:
            return HealthCheckResult(
                hardware_id=hw_id,
                healthy=False,
                response_time=asyncio.get_event_loop().time() - start,
                error=str(e)
            )
```

---

### 12.5 Checkpoint/Resume (체크포인트 기반 복구)

시퀀스 중단 시 상태를 저장하고, 재시작 시 이어서 실행합니다.

#### @step 데코레이터 확장

```python
@step(order=3, checkpoint=True)  # [NEW] 이 Step 완료 후 체크포인트 저장
async def voltage_measurement(self) -> Dict[str, Any]:
    """이 Step 완료 시 상태가 자동 저장됩니다."""
    ...
```

#### Checkpoint Manager

```python
# station-service/sequence/checkpoint.py

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Checkpoint:
    """체크포인트 데이터"""
    execution_id: str
    sequence_name: str
    sequence_version: str
    last_completed_step: str
    step_order: int
    parameters: Dict[str, Any]
    step_results: Dict[str, Dict[str, Any]]
    shared_data: Dict[str, Any]
    created_at: str


class CheckpointManager:
    """
    체크포인트 관리자.

    Step 완료 시 상태를 저장하고,
    재시작 시 마지막 체크포인트부터 재개할 수 있습니다.
    """

    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        execution_id: str,
        sequence_name: str,
        sequence_version: str,
        step_name: str,
        step_order: int,
        parameters: Dict[str, Any],
        step_results: Dict[str, Dict[str, Any]],
        shared_data: Dict[str, Any]
    ) -> None:
        """체크포인트 저장"""
        checkpoint = Checkpoint(
            execution_id=execution_id,
            sequence_name=sequence_name,
            sequence_version=sequence_version,
            last_completed_step=step_name,
            step_order=step_order,
            parameters=parameters,
            step_results=step_results,
            shared_data=shared_data,
            created_at=datetime.utcnow().isoformat()
        )

        filepath = self.checkpoint_dir / f"{execution_id}.json"
        with open(filepath, "w") as f:
            json.dump(asdict(checkpoint), f, indent=2)

    def load(self, execution_id: str) -> Optional[Checkpoint]:
        """체크포인트 로드"""
        filepath = self.checkpoint_dir / f"{execution_id}.json"

        if not filepath.exists():
            return None

        with open(filepath) as f:
            data = json.load(f)

        return Checkpoint(**data)

    def delete(self, execution_id: str) -> None:
        """체크포인트 삭제 (정상 완료 시)"""
        filepath = self.checkpoint_dir / f"{execution_id}.json"
        if filepath.exists():
            filepath.unlink()

    def get_latest(self, sequence_name: str) -> Optional[Checkpoint]:
        """특정 시퀀스의 최신 체크포인트 조회"""
        checkpoints = []

        for filepath in self.checkpoint_dir.glob("*.json"):
            with open(filepath) as f:
                data = json.load(f)

            if data.get("sequence_name") == sequence_name:
                checkpoints.append(Checkpoint(**data))

        if not checkpoints:
            return None

        return max(checkpoints, key=lambda c: c.created_at)
```

#### Executor에서 사용

```python
async def run(
    self,
    resume_from_checkpoint: bool = False,  # [NEW]
    execution_id: str = None,              # [NEW] 재개할 execution_id
    ...
) -> Dict[str, Any]:
    """
    시퀀스 실행.

    Args:
        resume_from_checkpoint: True면 체크포인트에서 재개
        execution_id: 재개할 실행 ID (없으면 최신 사용)
    """
    if resume_from_checkpoint:
        checkpoint = self._load_checkpoint(execution_id)
        if checkpoint:
            # 체크포인트 상태 복원
            self._restore_from_checkpoint(checkpoint)
            # 마지막 완료된 Step 다음부터 실행
            start_order = checkpoint.step_order + 1
```

---

### 12.6 Parameter Validation Hook

파라미터 값에 대한 커스텀 검증 로직을 추가합니다.

#### @validate 데코레이터

```python
# station-service/sequence/decorators.py

def validate(
    validator: Callable[[Any], bool],
    message: str = "Validation failed"
) -> Callable:
    """
    파라미터 검증 데코레이터.

    Args:
        validator: 검증 함수 (값을 받아 bool 반환)
        message: 검증 실패 시 에러 메시지

    Example:
        @parameter(name="voltage_limit")
        @validate(lambda v: 0 < v < 50, "Voltage must be 0-50V")
        def voltage_limit(self) -> float:
            return 5.5
    """
    def decorator(func):
        if hasattr(func, '_validators'):
            func._validators.append((validator, message))
        else:
            func._validators = [(validator, message)]
        return func
    return decorator


def validate_parameters(func: Callable) -> Callable:
    """
    Cross-parameter 검증 메서드 데코레이터.

    Example:
        @validate_parameters
        def validate(self, params: Dict[str, Any]) -> List[str]:
            errors = []
            if params["current_limit"] > params["voltage_limit"] / 5:
                errors.append("Current limit too high")
            return errors
    """
    func._is_param_validator = True
    return func
```

#### 사용 예시

```python
@sequence(name="PCB_Test")
class PCBTest:

    @parameter(name="voltage_limit", unit="V")
    @validate(lambda v: 0 < v < 50, "Voltage must be between 0 and 50V")
    @validate(lambda v: v % 0.5 == 0, "Voltage must be multiple of 0.5V")
    def voltage_limit(self) -> float:
        return 5.5

    @parameter(name="current_limit", unit="A")
    @validate(lambda v: v > 0, "Current must be positive")
    def current_limit(self) -> float:
        return 1.0

    @validate_parameters
    def validate(self, params: Dict[str, Any]) -> List[str]:
        """Cross-parameter validation"""
        errors = []

        # 전류 제한이 전압 대비 너무 높으면 경고
        if params["current_limit"] > params["voltage_limit"] / 5:
            errors.append(
                f"Current limit ({params['current_limit']}A) is too high "
                f"for voltage ({params['voltage_limit']}V)"
            )

        return errors
```

---

### 12.7 병렬 Step 실행

동일한 order를 가진 Step들을 병렬로 실행합니다.

#### @step 데코레이터 확장

```python
@step(order=2, group="parallel_measurements")
async def measure_voltage(self) -> Dict[str, Any]:
    """전압 측정"""
    voltage = await self.dmm.measure_dc_voltage()
    return {"voltage": voltage}

@step(order=2, group="parallel_measurements")  # 같은 order + group
async def measure_current(self) -> Dict[str, Any]:
    """전류 측정 - voltage와 동시 실행"""
    current = await self.dmm.measure_dc_current()
    return {"current": current}

@step(order=3)  # order 2의 모든 Step이 완료된 후 실행
async def analyze_results(self) -> Dict[str, Any]:
    """결과 분석"""
    ...
```

#### Executor 병렬 실행 로직

```python
async def _execute_parallel_steps(
    self,
    steps: List[Dict[str, Any]],
    on_step_start: Optional[Callable],
    on_step_complete: Optional[Callable],
    on_log: Optional[Callable]
) -> List[Dict[str, Any]]:
    """
    동일 order의 Step들을 병렬 실행.

    모든 Step이 완료될 때까지 대기하고,
    하나라도 실패하면 전체 실패로 처리합니다.
    """
    tasks = []

    for step_meta in steps:
        task = asyncio.create_task(
            self._execute_step(
                step_meta,
                on_step_start,
                on_step_complete,
                on_log
            )
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 예외를 결과로 변환
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append({
                "name": steps[i]["name"],
                "order": steps[i]["order"],
                "pass": False,
                "error": str(result)
            })
        else:
            final_results.append(result)

    return final_results
```

---

### 12.8 표준화된 Logging/Metrics

시퀀스에서 사용할 표준 Logger를 주입합니다.

#### SequenceLogger

```python
# station-service/sequence/logger.py

from typing import Any, Dict, Optional
from datetime import datetime
import structlog


class SequenceLogger:
    """
    시퀀스 전용 Logger.

    구조화된 로깅과 메트릭 수집을 제공합니다.
    """

    def __init__(
        self,
        batch_id: str,
        sequence_name: str,
        execution_id: str,
        on_log: callable = None,
        on_metric: callable = None
    ):
        self.batch_id = batch_id
        self.sequence_name = sequence_name
        self.execution_id = execution_id
        self._on_log = on_log
        self._on_metric = on_metric

        self._logger = structlog.get_logger().bind(
            batch_id=batch_id,
            sequence=sequence_name,
            execution_id=execution_id
        )

    def debug(self, message: str, **kwargs) -> None:
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._log("error", message, **kwargs)

    def metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Dict[str, str] = None
    ) -> None:
        """
        메트릭 기록.

        자동으로 Backend로 전송되어 분석에 사용됩니다.

        Args:
            name: 메트릭 이름 (e.g., "voltage", "current")
            value: 측정값
            unit: 단위 (e.g., "V", "A", "ms")
            tags: 추가 태그
        """
        metric_data = {
            "name": name,
            "value": value,
            "unit": unit,
            "tags": tags or {},
            "batch_id": self.batch_id,
            "sequence": self.sequence_name,
            "execution_id": self.execution_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        self._logger.info("metric", **metric_data)

        if self._on_metric:
            self._on_metric(metric_data)

    def _log(self, level: str, message: str, **kwargs) -> None:
        log_func = getattr(self._logger, level)
        log_func(message, **kwargs)

        if self._on_log:
            self._on_log(level, message, kwargs)
```

#### 시퀀스에서 사용

```python
def __init__(
    self,
    dmm: KeysightDMM,
    power: AgilentPowerSupply,
    logger: SequenceLogger  # [NEW] 자동 주입
):
    self.dmm = dmm
    self.power = power
    self.logger = logger

@step(order=2)
async def power_on_test(self) -> Dict[str, Any]:
    self.logger.info("Applying power", voltage=5.0)

    await self.power.set_output(voltage=5.0, current_limit=1.0)
    await self.power.enable()

    current = await self.dmm.measure_dc_current()

    # 메트릭 자동 수집
    self.logger.metric("initial_current", current, unit="A")
    self.logger.metric("power_on_time", 0.5, unit="s")

    if current > self.current_limit:
        self.logger.error(
            "Current exceeded",
            actual=current,
            limit=self.current_limit
        )
        raise TestFailure(f"Current {current}A exceeds limit")

    return {"voltage": 5.0, "current": current}
```

---

### 12.9 버전 호환성 검사

Station Service와 Sequence Package 간 버전 호환성을 체크합니다.

#### manifest.yaml 확장

```yaml
name: pcb_voltage_test
version: 1.2.0

# [NEW] 호환성 요구사항
compatibility:
  station_service: ">=1.0.0,<2.0.0"  # Station Service 버전
  python: ">=3.11"                    # Python 버전
  api_version: "1"                    # API 버전
```

#### 호환성 검사기

```python
# station-service/sequence/compatibility.py

from packaging import version
from typing import Optional, List
from dataclasses import dataclass
import sys


@dataclass
class CompatibilityResult:
    compatible: bool
    errors: List[str]
    warnings: List[str]


class CompatibilityChecker:
    """버전 호환성 검사기"""

    def __init__(self, station_version: str, api_version: str = "1"):
        self.station_version = station_version
        self.api_version = api_version
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    def check(self, compatibility_spec: dict) -> CompatibilityResult:
        """호환성 검사 실행"""
        errors = []
        warnings = []

        # Station Service 버전 체크
        station_req = compatibility_spec.get("station_service")
        if station_req:
            if not self._check_version(self.station_version, station_req):
                errors.append(
                    f"Station Service {self.station_version} does not satisfy "
                    f"requirement {station_req}"
                )

        # Python 버전 체크
        python_req = compatibility_spec.get("python")
        if python_req:
            if not self._check_version(self.python_version, python_req):
                errors.append(
                    f"Python {self.python_version} does not satisfy "
                    f"requirement {python_req}"
                )

        # API 버전 체크
        api_req = compatibility_spec.get("api_version")
        if api_req and str(api_req) != self.api_version:
            warnings.append(
                f"API version mismatch: package requires {api_req}, "
                f"service provides {self.api_version}"
            )

        return CompatibilityResult(
            compatible=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _check_version(self, current: str, requirement: str) -> bool:
        """버전 요구사항 검사"""
        from packaging.specifiers import SpecifierSet

        try:
            spec = SpecifierSet(requirement)
            return version.parse(current) in spec
        except Exception:
            return False
```

---

### 12.10 Hot Reload (개발 모드)

개발 중 시퀀스 코드 변경 시 자동 리로드합니다.

#### station.yaml 설정

```yaml
server:
  host: "0.0.0.0"
  port: 8080

# [NEW] 개발 모드 설정
development:
  enabled: true
  hot_reload: true           # 코드 변경 감지 및 리로드
  watch_patterns:            # 감시할 파일 패턴
    - "*.py"
    - "manifest.yaml"
  reload_delay: 1.0          # 변경 후 리로드까지 대기 (초)
```

#### Hot Reload Manager

```python
# station-service/sequence/hot_reload.py

import asyncio
from pathlib import Path
from typing import Callable, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class SequenceReloadHandler(FileSystemEventHandler):
    """파일 변경 감지 핸들러"""

    def __init__(
        self,
        patterns: Set[str],
        on_change: Callable[[str], None],
        delay: float = 1.0
    ):
        self.patterns = patterns
        self.on_change = on_change
        self.delay = delay
        self._pending_reload = False
        self._timer = None

    def on_modified(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        # 패턴 매칭
        if not any(path.match(p) for p in self.patterns):
            return

        # Debounce - 여러 변경을 하나로 묶음
        if self._timer:
            self._timer.cancel()

        self._timer = asyncio.get_event_loop().call_later(
            self.delay,
            lambda: asyncio.create_task(self._trigger_reload(str(path)))
        )

    async def _trigger_reload(self, path: str):
        if self.on_change:
            await self.on_change(path)


class HotReloadManager:
    """Hot Reload 관리자"""

    def __init__(
        self,
        sequence_dirs: list,
        patterns: Set[str],
        on_reload: Callable[[str], None],
        enabled: bool = False
    ):
        self.sequence_dirs = sequence_dirs
        self.patterns = patterns
        self.on_reload = on_reload
        self.enabled = enabled
        self._observer = None

    def start(self) -> None:
        if not self.enabled:
            return

        handler = SequenceReloadHandler(
            patterns=self.patterns,
            on_change=self.on_reload
        )

        self._observer = Observer()

        for seq_dir in self.sequence_dirs:
            self._observer.schedule(
                handler,
                str(seq_dir),
                recursive=True
            )

        self._observer.start()

    def stop(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join()
```

---

### 12.11 Step Pre/Post Hooks

Step 실행 전후에 공통 로직을 실행하는 Hook 시스템입니다.

#### Hook 데코레이터

```python
# station-service/sequence/decorators.py

def before_step(func: Callable) -> Callable:
    """
    모든 Step 실행 전에 호출되는 Hook.

    Example:
        @before_step
        async def setup(self, step_name: str, ctx: StepContext) -> None:
            self.logger.info(f"Starting step: {step_name}")
            await self.dmm.select_channel(1)  # 기본 채널 선택
    """
    func._hook_type = "before_step"
    return func


def after_step(func: Callable) -> Callable:
    """
    모든 Step 실행 후에 호출되는 Hook.

    Example:
        @after_step
        async def teardown(
            self,
            step_name: str,
            result: Dict[str, Any],
            ctx: StepContext
        ) -> None:
            self.logger.info(f"Completed step: {step_name}")
            # 메트릭 자동 수집
            if "voltage" in result.get("data", {}):
                ctx.record_metric("step_voltage", result["data"]["voltage"], "V")
    """
    func._hook_type = "after_step"
    return func


def on_error(func: Callable) -> Callable:
    """
    Step 에러 발생 시 호출되는 Hook.

    Example:
        @on_error
        async def handle_error(
            self,
            step_name: str,
            error: Exception,
            ctx: StepContext
        ) -> Optional[Dict[str, Any]]:
            self.logger.error(f"Error in {step_name}: {error}")
            # 복구 로직 (선택적)
            if isinstance(error, ConnectionError):
                await self.dmm.reconnect()
                return {"retry": True}  # 재시도 요청
            return None
    """
    func._hook_type = "on_error"
    return func
```

#### 사용 예시

```python
@sequence(name="PCB_Test")
class PCBTest:
    def __init__(self, dmm, power, logger):
        self.dmm = dmm
        self.power = power
        self.logger = logger
        self._measurement_count = 0

    @before_step
    async def pre_step(self, step_name: str, ctx: StepContext) -> None:
        """모든 Step 전에 실행"""
        self.logger.debug(f"[PRE] {step_name}")
        # 장비 연결 상태 확인
        if not await self.dmm.is_connected():
            raise ConnectionError("DMM disconnected before step")

    @after_step
    async def post_step(
        self,
        step_name: str,
        result: Dict[str, Any],
        ctx: StepContext
    ) -> None:
        """모든 Step 후에 실행"""
        self._measurement_count += 1
        self.logger.debug(f"[POST] {step_name}: {result['pass']}")

    @on_error
    async def error_handler(
        self,
        step_name: str,
        error: Exception,
        ctx: StepContext
    ) -> Optional[Dict[str, Any]]:
        """에러 처리"""
        # 스크린샷 저장, 상태 덤프 등
        self.logger.error(f"Error in {step_name}", exc_info=error)

        # 특정 에러는 복구 시도
        if "timeout" in str(error).lower():
            await self.dmm.reset()
            return {"retry": True}

        return None
```

---

### 12.12 Dynamic Parameter Dependencies

파라미터 간 동적 의존성을 정의하여 UI에서 조건부 표시/숨김을 지원합니다.

#### manifest.yaml 확장

```yaml
parameters:
  test_mode:
    display_name: "테스트 모드"
    type: string
    default: "basic"
    options: ["basic", "advanced", "aging"]

  # [NEW] 조건부 파라미터
  aging_duration:
    display_name: "에이징 시간"
    type: integer
    default: 60
    min: 10
    max: 3600
    unit: "s"
    depends_on:                          # [NEW]
      parameter: "test_mode"
      condition: "equals"
      value: "aging"

  advanced_options:
    display_name: "고급 옵션"
    type: boolean
    default: false
    depends_on:
      parameter: "test_mode"
      condition: "in"
      value: ["advanced", "aging"]

  # 여러 조건 조합
  voltage_step:
    display_name: "전압 스텝"
    type: float
    default: 0.1
    depends_on:
      all:                               # AND 조건
        - parameter: "advanced_options"
          condition: "equals"
          value: true
        - parameter: "test_mode"
          condition: "not_equals"
          value: "basic"
```

#### UI 렌더링 로직

```typescript
// Station UI에서 파라미터 렌더링
interface ParameterDependency {
  parameter: string;
  condition: 'equals' | 'not_equals' | 'in' | 'greater_than' | 'less_than';
  value: any;
}

function shouldShowParameter(
  param: ParameterSchema,
  currentValues: Record<string, any>
): boolean {
  if (!param.dependsOn) return true;

  const { parameter, condition, value } = param.dependsOn;
  const currentValue = currentValues[parameter];

  switch (condition) {
    case 'equals':
      return currentValue === value;
    case 'not_equals':
      return currentValue !== value;
    case 'in':
      return Array.isArray(value) && value.includes(currentValue);
    case 'greater_than':
      return currentValue > value;
    case 'less_than':
      return currentValue < value;
    default:
      return true;
  }
}
```

---

### 12.13 Equipment Abstraction Layer

장비 드라이버 교체를 용이하게 하는 추상화 레이어입니다.

#### 추상 장비 인터페이스

```python
# station-service/sequence/equipment/interfaces.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IDMMeter(ABC):
    """디지털 멀티미터 표준 인터페이스"""

    @abstractmethod
    async def measure_voltage(
        self,
        mode: str = "DC",
        range: str = "AUTO"
    ) -> float:
        """전압 측정"""
        pass

    @abstractmethod
    async def measure_current(
        self,
        mode: str = "DC",
        range: str = "AUTO"
    ) -> float:
        """전류 측정"""
        pass

    @abstractmethod
    async def measure_resistance(
        self,
        four_wire: bool = False
    ) -> float:
        """저항 측정"""
        pass


class IPowerSupply(ABC):
    """파워 서플라이 표준 인터페이스"""

    @abstractmethod
    async def set_voltage(self, voltage: float) -> None:
        pass

    @abstractmethod
    async def set_current_limit(self, current: float) -> None:
        pass

    @abstractmethod
    async def enable_output(self) -> None:
        pass

    @abstractmethod
    async def disable_output(self) -> None:
        pass

    @abstractmethod
    async def get_actual_voltage(self) -> float:
        pass

    @abstractmethod
    async def get_actual_current(self) -> float:
        pass


class IOscilloscope(ABC):
    """오실로스코프 표준 인터페이스"""

    @abstractmethod
    async def set_timebase(self, scale: float) -> None:
        pass

    @abstractmethod
    async def set_channel_scale(
        self,
        channel: int,
        scale: float
    ) -> None:
        pass

    @abstractmethod
    async def acquire_waveform(
        self,
        channel: int
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def measure_frequency(self, channel: int) -> float:
        pass

    @abstractmethod
    async def measure_peak_to_peak(self, channel: int) -> float:
        pass
```

#### 드라이버 구현 예시

```python
# sequences/pcb_test/drivers/keysight_dmm.py

from station.equipment.interfaces import IDMMeter

class KeysightDMM(BaseDriver, IDMMeter):
    """Keysight 34461A - IDMMeter 구현"""

    async def measure_voltage(
        self,
        mode: str = "DC",
        range: str = "AUTO"
    ) -> float:
        cmd = f"CONF:VOLT:{mode}"
        if range != "AUTO":
            cmd += f" {range}"
        await self._write(cmd)
        return float(await self._query("READ?"))

    async def measure_current(
        self,
        mode: str = "DC",
        range: str = "AUTO"
    ) -> float:
        cmd = f"CONF:CURR:{mode}"
        if range != "AUTO":
            cmd += f" {range}"
        await self._write(cmd)
        return float(await self._query("READ?"))

    async def measure_resistance(
        self,
        four_wire: bool = False
    ) -> float:
        mode = "FRES" if four_wire else "RES"
        await self._write(f"CONF:{mode}")
        return float(await self._query("READ?"))


# sequences/pcb_test/drivers/fluke_dmm.py

class FlukeDMM(BaseDriver, IDMMeter):
    """Fluke 8845A - IDMMeter 구현 (다른 SCPI 명령 사용)"""

    async def measure_voltage(
        self,
        mode: str = "DC",
        range: str = "AUTO"
    ) -> float:
        # Fluke는 다른 명령 체계 사용
        await self._write(f"FUNC VOLT:{mode}")
        if range != "AUTO":
            await self._write(f"RANGE {range}")
        return float(await self._query("FETCH?"))
```

#### manifest.yaml에서 인터페이스 지정

```yaml
hardware:
  dmm:
    display_name: "디지털 멀티미터"
    interface: "IDMMeter"              # [NEW] 인터페이스 타입
    driver: "./drivers/keysight_dmm.py"
    class: "KeysightDMM"

    # 대체 드라이버 목록
    alternatives:                       # [NEW]
      - driver: "./drivers/fluke_dmm.py"
        class: "FlukeDMM"
        description: "Fluke 8845A"
      - driver: "./drivers/agilent_dmm.py"
        class: "AgilentDMM"
        description: "Agilent 34401A"
```

---

### 12.14 Result Data Export Formats

테스트 결과를 다양한 형식으로 내보내는 기능입니다.

#### 결과 내보내기 설정

```yaml
# station.yaml

export:
  enabled: true
  formats:
    - csv
    - json
    - xml

  # CSV 설정
  csv:
    delimiter: ","
    include_headers: true
    datetime_format: "%Y-%m-%d %H:%M:%S"

  # JSON 설정
  json:
    indent: 2
    include_raw_data: false

  # 자동 내보내기
  auto_export:
    enabled: true
    trigger: "sequence_complete"
    output_dir: "data/exports/{date}/{batch_id}"
    filename_pattern: "{sequence_name}_{execution_id}.{format}"
```

#### Export Manager

```python
# station-service/sequence/export.py

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import csv
import json
import xml.etree.ElementTree as ET
from dataclasses import asdict


class ResultExporter:
    """테스트 결과 내보내기 관리자"""

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "data/exports"))

    def export(
        self,
        result: Dict[str, Any],
        format: str = "json"
    ) -> Path:
        """결과를 지정된 형식으로 내보내기"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        filename = self._generate_filename(result, format)
        filepath = self.output_dir / filename

        if format == "json":
            self._export_json(result, filepath)
        elif format == "csv":
            self._export_csv(result, filepath)
        elif format == "xml":
            self._export_xml(result, filepath)

        return filepath

    def _export_json(self, result: Dict[str, Any], filepath: Path) -> None:
        config = self.config.get("json", {})
        with open(filepath, "w") as f:
            json.dump(
                result,
                f,
                indent=config.get("indent", 2),
                default=str
            )

    def _export_csv(self, result: Dict[str, Any], filepath: Path) -> None:
        config = self.config.get("csv", {})
        delimiter = config.get("delimiter", ",")

        # Step 결과를 플랫하게 변환
        rows = []
        for step in result.get("steps", []):
            row = {
                "execution_id": result["execution_id"],
                "sequence_name": result["sequence_name"],
                "step_name": step["name"],
                "step_order": step["order"],
                "status": step["status"],
                "pass": step["pass"],
                "duration": step.get("duration", 0),
                "error": step.get("error", ""),
            }
            # 결과 데이터 플랫화
            if step.get("data"):
                for key, value in step["data"].items():
                    row[f"data_{key}"] = value
            rows.append(row)

        if rows:
            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=rows[0].keys(),
                    delimiter=delimiter
                )
                if config.get("include_headers", True):
                    writer.writeheader()
                writer.writerows(rows)

    def _export_xml(self, result: Dict[str, Any], filepath: Path) -> None:
        root = ET.Element("TestResult")

        # 메타데이터
        meta = ET.SubElement(root, "Metadata")
        ET.SubElement(meta, "ExecutionId").text = result["execution_id"]
        ET.SubElement(meta, "SequenceName").text = result["sequence_name"]
        ET.SubElement(meta, "OverallPass").text = str(result["overall_pass"])

        # Steps
        steps_elem = ET.SubElement(root, "Steps")
        for step in result.get("steps", []):
            step_elem = ET.SubElement(steps_elem, "Step")
            ET.SubElement(step_elem, "Name").text = step["name"]
            ET.SubElement(step_elem, "Order").text = str(step["order"])
            ET.SubElement(step_elem, "Pass").text = str(step["pass"])

        tree = ET.ElementTree(root)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    def _generate_filename(self, result: Dict[str, Any], format: str) -> str:
        pattern = self.config.get(
            "filename_pattern",
            "{sequence_name}_{execution_id}.{format}"
        )
        return pattern.format(
            sequence_name=result["sequence_name"],
            execution_id=result["execution_id"],
            format=format,
            date=datetime.now().strftime("%Y%m%d")
        )
```

---

### 12.15 Sequence Templates & Inheritance

공통 로직을 재사용하기 위한 시퀀스 템플릿 시스템입니다.

#### 베이스 시퀀스 템플릿

```python
# station-service/sequence/templates/voltage_test_base.py

from abc import abstractmethod
from typing import Dict, Any
from station.sequence import sequence, step, parameter


class VoltageTestTemplate:
    """
    전압 테스트 공통 템플릿.

    모든 전압 테스트 시퀀스의 베이스 클래스.
    공통 Step과 파라미터를 정의합니다.
    """

    # 공통 파라미터
    @parameter(name="voltage_limit", unit="V")
    def voltage_limit(self) -> float:
        return 5.5

    @parameter(name="current_limit", unit="A")
    def current_limit(self) -> float:
        return 1.0

    # 공통 초기화 Step
    @step(order=1, timeout=30, retry=3)
    async def initialize(self) -> Dict[str, Any]:
        """장비 초기화 (공통)"""
        await self.power.reset()
        await self.dmm.reset()
        return {"status": "initialized"}

    # 추상 Step - 서브클래스에서 구현 필수
    @abstractmethod
    @step(order=2, timeout=120)
    async def main_test(self) -> Dict[str, Any]:
        """메인 테스트 로직 (서브클래스에서 구현)"""
        pass

    # 공통 정리 Step
    @step(order=99, cleanup=True)
    async def finalize(self) -> Dict[str, Any]:
        """정리 (공통)"""
        await self.power.disable()
        return {"status": "finalized"}
```

#### 템플릿 상속 사용

```python
# sequences/pcb_voltage_test/sequence.py

from station.templates import VoltageTestTemplate
from station.sequence import sequence, step


@sequence(name="PCB_Voltage_Test", version="1.2.0")
class PCBVoltageTest(VoltageTestTemplate):
    """
    PCB 전압 테스트.

    VoltageTestTemplate을 상속하여 공통 로직 재사용.
    """

    def __init__(self, dmm, power):
        self.dmm = dmm
        self.power = power

    # 추상 메서드 구현
    @step(order=2, timeout=120)
    async def main_test(self) -> Dict[str, Any]:
        """PCB 특화 전압 테스트"""
        await self.power.set_output(5.0, self.current_limit)
        await self.power.enable()

        voltage = await self.dmm.measure_dc_voltage()

        if voltage > self.voltage_limit:
            raise TestFailure(f"Voltage {voltage}V exceeds limit")

        return {"voltage": voltage, "pass": True}

    # 추가 Step (order 3에 삽입)
    @step(order=3, timeout=60)
    async def ripple_test(self) -> Dict[str, Any]:
        """리플 테스트 (PCB 전용)"""
        measurements = []
        for _ in range(10):
            v = await self.dmm.measure_dc_voltage()
            measurements.append(v)

        ripple = max(measurements) - min(measurements)
        return {"ripple": ripple, "pass": ripple < 0.1}
```

---

## 13. Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-30 | Initial design specification |
| 1.1.0 | 2025-12-30 | Added Future Enhancements section with 10 recommendations |
| 1.2.0 | 2025-12-30 | Added 5 additional enhancements: Step Hooks, Dynamic Parameter Dependencies, Equipment Abstraction Layer, Result Export Formats, Sequence Templates |
| 1.3.0 | 2025-12-30 | Document split: Separated requirements spec (spec.md) from design specification (design.md) |

---

## Appendix A: Quick Reference

### A.1 Decorator Summary

| Decorator | Target | Purpose |
|-----------|--------|---------|
| `@sequence(name, description, version)` | Class | Mark as sequence |
| `@step(order, timeout, retry, cleanup, condition)` | Async method | Mark as test step |
| `@parameter(name, display_name, unit, description)` | Method → Property | Define parameter |

### A.2 Manifest Required Fields

```yaml
# Required
name: string           # Package identifier
version: string        # Semantic version (X.Y.Z)
entry_point:
  module: string       # Python module name
  class: string        # Class name

# Optional
author: string
description: string
hardware: {}           # Hardware definitions
parameters: {}         # UI-editable parameters
dependencies: {}       # Python packages
```

### A.3 Driver Interface

```python
class Driver:
    async def connect(self) -> bool: ...
    async def disconnect(self) -> None: ...
    async def reset(self) -> None: ...
    async def identify(self) -> str: ...  # Optional
```
