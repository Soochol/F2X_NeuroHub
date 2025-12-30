"""
Service Registry for Production Tracker App.

Provides a simple dependency injection container for:
- Service registration and retrieval
- Interface-based dependency resolution
- Singleton and factory patterns
- Type-safe service access

Usage:
    # Registration (in main.py)
    from utils.service_registry import ServiceRegistry
    from services.interfaces import IAPIClient, IAuthService

    registry = ServiceRegistry()
    registry.register(IAPIClient, api_client)
    registry.register(IAuthService, auth_service)

    # Retrieval (anywhere in app)
    api_client = ServiceRegistry.get(IAPIClient)

    # Or use the global instance
    from utils.service_registry import get_service
    api_client = get_service(IAPIClient)
"""
import logging
from threading import Lock
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceNotFoundError(Exception):
    """Raised when a requested service is not registered."""

    def __init__(self, service_type: Type):
        self.service_type = service_type
        super().__init__(
            f"Service not found: {service_type.__name__}. "
            f"Did you forget to register it?"
        )


class ServiceAlreadyRegisteredError(Exception):
    """Raised when trying to register a service that already exists."""

    def __init__(self, service_type: Type):
        self.service_type = service_type
        super().__init__(
            f"Service already registered: {service_type.__name__}. "
            f"Use replace=True to override."
        )


class ServiceRegistry:
    """
    Thread-safe service registry for dependency injection.

    Supports:
    - Singleton instances
    - Factory functions for lazy initialization
    - Interface-based registration
    - Scoped services (future extension)
    """

    # Singleton instance for global access
    _instance: Optional['ServiceRegistry'] = None
    _lock: Lock = Lock()

    def __new__(cls) -> 'ServiceRegistry':
        """Ensure singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry."""
        if getattr(self, '_initialized', False):
            return

        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._service_lock = Lock()
        self._initialized = True
        logger.debug("ServiceRegistry initialized")

    def register(
        self,
        interface: Type[T],
        implementation: Union[T, Callable[[], T]],
        replace: bool = False
    ) -> 'ServiceRegistry':
        """
        Register a service implementation.

        Args:
            interface: The interface type (abstract class)
            implementation: Instance or factory function
            replace: If True, replaces existing registration

        Returns:
            Self for method chaining

        Raises:
            ServiceAlreadyRegisteredError: If service exists and replace=False

        Example:
            registry.register(IAPIClient, api_client)
            registry.register(IAuthService, lambda: AuthService(api_client))
        """
        with self._service_lock:
            if interface in self._services and not replace:
                raise ServiceAlreadyRegisteredError(interface)

            if callable(implementation) and not isinstance(implementation, type):
                # It's a factory function
                self._factories[interface] = implementation
                logger.debug(f"Registered factory: {interface.__name__}")
            else:
                # It's an instance
                self._services[interface] = implementation
                logger.debug(f"Registered service: {interface.__name__}")

        return self

    def register_instance(
        self,
        interface: Type[T],
        instance: T,
        replace: bool = False
    ) -> 'ServiceRegistry':
        """
        Register a service instance (explicit method).

        Args:
            interface: The interface type
            instance: The service instance
            replace: If True, replaces existing registration

        Returns:
            Self for method chaining
        """
        with self._service_lock:
            if interface in self._services and not replace:
                raise ServiceAlreadyRegisteredError(interface)

            self._services[interface] = instance
            logger.debug(f"Registered instance: {interface.__name__}")

        return self

    def register_factory(
        self,
        interface: Type[T],
        factory: Callable[[], T],
        replace: bool = False
    ) -> 'ServiceRegistry':
        """
        Register a factory function for lazy initialization.

        Args:
            interface: The interface type
            factory: Function that creates the service
            replace: If True, replaces existing registration

        Returns:
            Self for method chaining
        """
        with self._service_lock:
            if interface in self._factories and not replace:
                raise ServiceAlreadyRegisteredError(interface)

            self._factories[interface] = factory
            logger.debug(f"Registered factory: {interface.__name__}")

        return self

    def get(self, interface: Type[T]) -> T:
        """
        Get a registered service.

        Args:
            interface: The interface type to retrieve

        Returns:
            The registered service instance

        Raises:
            ServiceNotFoundError: If service is not registered
        """
        with self._service_lock:
            # Check instances first
            if interface in self._services:
                return self._services[interface]

            # Check factories
            if interface in self._factories:
                # Create instance from factory and cache it
                instance = self._factories[interface]()
                self._services[interface] = instance
                logger.debug(f"Created instance from factory: {interface.__name__}")
                return instance

        raise ServiceNotFoundError(interface)

    def try_get(self, interface: Type[T]) -> Optional[T]:
        """
        Try to get a service, returning None if not found.

        Args:
            interface: The interface type to retrieve

        Returns:
            The service instance or None
        """
        try:
            return self.get(interface)
        except ServiceNotFoundError:
            return None

    def has(self, interface: Type) -> bool:
        """
        Check if a service is registered.

        Args:
            interface: The interface type to check

        Returns:
            True if registered
        """
        with self._service_lock:
            return interface in self._services or interface in self._factories

    def unregister(self, interface: Type) -> bool:
        """
        Unregister a service.

        Args:
            interface: The interface type to unregister

        Returns:
            True if service was found and removed
        """
        with self._service_lock:
            removed = False
            if interface in self._services:
                del self._services[interface]
                removed = True
            if interface in self._factories:
                del self._factories[interface]
                removed = True

            if removed:
                logger.debug(f"Unregistered: {interface.__name__}")
            return removed

    def clear(self) -> None:
        """Clear all registered services."""
        with self._service_lock:
            self._services.clear()
            self._factories.clear()
            logger.debug("ServiceRegistry cleared")

    def get_all_registered(self) -> Dict[str, bool]:
        """
        Get all registered service types.

        Returns:
            Dict mapping interface names to whether they're instantiated
        """
        with self._service_lock:
            result = {}
            for interface in self._services:
                result[interface.__name__] = True
            for interface in self._factories:
                if interface not in self._services:
                    result[interface.__name__] = False
            return result

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing).

        Warning: This should only be used in tests!
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.clear()
                cls._instance = None
        logger.debug("ServiceRegistry instance reset")


# Global convenience functions
def get_registry() -> ServiceRegistry:
    """Get the global ServiceRegistry instance."""
    return ServiceRegistry()


def get_service(interface: Type[T]) -> T:
    """
    Get a service from the global registry.

    Args:
        interface: The interface type to retrieve

    Returns:
        The registered service instance

    Raises:
        ServiceNotFoundError: If service is not registered
    """
    return ServiceRegistry().get(interface)


def try_get_service(interface: Type[T]) -> Optional[T]:
    """
    Try to get a service, returning None if not found.

    Args:
        interface: The interface type to retrieve

    Returns:
        The service instance or None
    """
    return ServiceRegistry().try_get(interface)


def register_service(
    interface: Type[T],
    implementation: Union[T, Callable[[], T]],
    replace: bool = False
) -> None:
    """
    Register a service in the global registry.

    Args:
        interface: The interface type
        implementation: Instance or factory function
        replace: If True, replaces existing registration
    """
    ServiceRegistry().register(interface, implementation, replace)
