# Utils package
"""
Utilities package for Production Tracker App.

This package contains:
- config: Application configuration management
- exceptions: Typed exception hierarchy
- service_registry: Dependency injection container
- theme_manager: Theme loading and management
- logger: Logging configuration
- exception_handler: Global exception handling
"""

from .exceptions import (
    NeuroHubError,
    ErrorCode,
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    WorkOperationError,
    ValidationError,
    EquipmentError,
    FileOperationError,
    ConfigurationError,
)

from .service_registry import (
    ServiceRegistry,
    ServiceNotFoundError,
    ServiceAlreadyRegisteredError,
    get_registry,
    get_service,
    try_get_service,
    register_service,
)

__all__ = [
    # Exceptions
    "NeuroHubError",
    "ErrorCode",
    "ConnectionError",
    "TimeoutError",
    "AuthenticationError",
    "WorkOperationError",
    "ValidationError",
    "EquipmentError",
    "FileOperationError",
    "ConfigurationError",
    # Service Registry
    "ServiceRegistry",
    "ServiceNotFoundError",
    "ServiceAlreadyRegisteredError",
    "get_registry",
    "get_service",
    "try_get_service",
    "register_service",
]
