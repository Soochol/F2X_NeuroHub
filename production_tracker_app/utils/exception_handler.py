"""
Centralized Exception Handling Utilities.

Provides structured, reusable exception handling patterns for the entire application.
Ensures consistent error logging, user feedback, and graceful degradation.
"""

import sys
import logging
import traceback
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtCore import QObject

logger = logging.getLogger(__name__)


class ExceptionHandler:
    """
    Central exception handling utility for PySide6 applications.

    Provides decorators and utility methods for consistent exception handling
    across the entire application.
    """

    @staticmethod
    def install_global_handler():
        """
        Install global exception handler to catch unhandled exceptions.

        Should be called once at application startup in main.py.
        """
        def global_exception_hook(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions globally."""
            if issubclass(exc_type, KeyboardInterrupt):
                # Allow keyboard interrupt to pass through
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Log the exception with full traceback
            logger.critical(
                "Unhandled exception occurred",
                exc_info=(exc_type, exc_value, exc_traceback)
            )

            # Format error message for user
            error_msg = str(exc_value) if str(exc_value) else exc_type.__name__

            # Show error dialog to user
            try:
                QMessageBox.critical(
                    None,
                    "예기치 않은 오류",
                    f"예기치 않은 오류가 발생했습니다:\n\n{error_msg}\n\n"
                    f"자세한 내용은 로그 파일을 확인하세요."
                )
            except Exception:
                # If dialog fails, at least print to console
                print(f"CRITICAL ERROR: {error_msg}", file=sys.stderr)

        sys.excepthook = global_exception_hook
        logger.info("Global exception handler installed")

    @staticmethod
    def safe_call(
        func: Callable,
        *args,
        error_message: str = "작업 중 오류가 발생했습니다",
        default_return: Any = None,
        show_dialog: bool = False,
        parent: Optional[QWidget] = None,
        **kwargs
    ) -> Any:
        """
        Safely execute a function with exception handling.

        Args:
            func: Function to execute
            *args: Arguments to pass to function
            error_message: User-friendly error message prefix
            default_return: Value to return on error
            show_dialog: Whether to show error dialog to user
            parent: Parent widget for dialog
            **kwargs: Keyword arguments to pass to function

        Returns:
            Function result or default_return on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {e}", exc_info=True)

            if show_dialog:
                QMessageBox.warning(
                    parent,
                    "오류",
                    f"{error_message}:\n\n{str(e)}"
                )

            return default_return

    @staticmethod
    def safe_connect(
        signal,
        slot: Callable,
        error_message: str = "시그널 연결 실패"
    ) -> bool:
        """
        Safely connect a Qt signal to a slot.

        Args:
            signal: Qt signal to connect
            slot: Slot function to connect to
            error_message: Error message for logging

        Returns:
            True if connection successful, False otherwise
        """
        try:
            signal.connect(slot)
            return True
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.error(f"{error_message}: {e}")
            return False

    @staticmethod
    def safe_disconnect(
        signal,
        slot: Optional[Callable] = None,
        error_message: str = "시그널 연결 해제 실패"
    ) -> bool:
        """
        Safely disconnect a Qt signal from a slot.

        Args:
            signal: Qt signal to disconnect
            slot: Specific slot to disconnect (None for all)
            error_message: Error message for logging

        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if slot:
                signal.disconnect(slot)
            else:
                signal.disconnect()
            return True
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.warning(f"{error_message}: {e}")
            return False


def safe_slot(
    error_message: str = "슬롯 실행 중 오류",
    show_dialog: bool = False,
    default_return: Any = None
):
    """
    Decorator for Qt slot methods to handle exceptions safely.

    Args:
        error_message: User-friendly error message
        show_dialog: Whether to show error dialog
        default_return: Value to return on error

    Example:
        @safe_slot("데이터 로드 실패", show_dialog=True)
        def on_data_loaded(self, data):
            # Process data - exceptions will be caught
            self.process(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}", exc_info=True)

                if show_dialog:
                    parent = self if isinstance(self, QWidget) else None
                    QMessageBox.warning(
                        parent,
                        "오류",
                        f"{error_message}:\n\n{str(e)}"
                    )

                return default_return
        return wrapper
    return decorator


def safe_init(error_message: str = "초기화 중 오류"):
    """
    Decorator for __init__ methods to handle initialization errors.

    Logs errors but allows object creation to continue with degraded state.

    Args:
        error_message: Error message prefix for logging

    Example:
        @safe_init("SettingsPage 초기화 실패")
        def __init__(self, config, parent=None):
            super().__init__(parent)
            self.setup_ui()  # Exceptions caught
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}", exc_info=True)
                # Don't re-raise - allow degraded object creation
                # Set a flag to indicate initialization failure
                self._init_failed = True
                self._init_error = str(e)
        return wrapper
    return decorator


def safe_cleanup(error_message: str = "정리 중 오류"):
    """
    Decorator for cleanup methods to ensure resources are released.

    Catches exceptions during cleanup to prevent resource leaks.

    Args:
        error_message: Error message prefix for logging

    Example:
        @safe_cleanup("리소스 정리 실패")
        def cleanup(self):
            self.timer.stop()
            self.worker.cancel()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}", exc_info=True)
                # Don't re-raise - cleanup should always complete
        return wrapper
    return decorator


def safe_api_call(
    error_message: str = "API 호출 실패",
    show_dialog: bool = True,
    emit_signal: Optional[str] = None
):
    """
    Decorator for methods that make API calls.

    Provides consistent error handling for network operations.

    Args:
        error_message: User-friendly error message
        show_dialog: Whether to show error dialog
        emit_signal: Name of error signal to emit (e.g., 'error_occurred')

    Example:
        @safe_api_call("생산라인 로드 실패", emit_signal='error_occurred')
        def load_production_lines(self):
            return self.api_client.get_production_lines()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                full_message = f"{error_message}: {str(e)}"
                logger.error(full_message, exc_info=True)

                # Emit error signal if specified
                if emit_signal and hasattr(self, emit_signal):
                    signal = getattr(self, emit_signal)
                    try:
                        signal.emit(full_message)
                    except Exception as sig_error:
                        logger.error(f"시그널 발신 실패: {sig_error}")

                # Show dialog if specified
                if show_dialog:
                    parent = self if isinstance(self, QWidget) else None
                    QMessageBox.warning(
                        parent,
                        "오류",
                        full_message
                    )

                return None
        return wrapper
    return decorator


class SignalConnector:
    """
    Helper class for safely connecting multiple signals at once.

    Provides batch connection with error tracking.

    Example:
        connector = SignalConnector()
        connector.connect(self.viewmodel.lot_updated, self._on_lot_updated)
        connector.connect(self.viewmodel.work_started, self._on_work_started)

        if not connector.all_connected():
            logger.warning(f"Failed connections: {connector.failed_connections}")
    """

    def __init__(self):
        self._connections = []
        self._failed = []

    def connect(
        self,
        signal,
        slot: Callable,
        description: str = ""
    ) -> 'SignalConnector':
        """
        Add a signal-slot connection.

        Args:
            signal: Qt signal
            slot: Slot function
            description: Description for error messages

        Returns:
            Self for chaining
        """
        try:
            signal.connect(slot)
            self._connections.append((signal, slot, description))
        except Exception as e:
            desc = description or f"{signal} -> {slot.__name__}"
            logger.error(f"시그널 연결 실패 [{desc}]: {e}")
            self._failed.append((desc, str(e)))

        return self

    def all_connected(self) -> bool:
        """Check if all connections succeeded."""
        return len(self._failed) == 0

    @property
    def failed_connections(self) -> list:
        """Get list of failed connections."""
        return self._failed

    @property
    def connection_count(self) -> int:
        """Get number of successful connections."""
        return len(self._connections)

    def disconnect_all(self) -> int:
        """
        Disconnect all managed connections.

        Returns:
            Number of successfully disconnected signals
        """
        disconnected = 0
        for signal, slot, desc in self._connections:
            try:
                signal.disconnect(slot)
                disconnected += 1
            except Exception as e:
                logger.warning(f"시그널 연결 해제 실패 [{desc}]: {e}")

        self._connections.clear()
        return disconnected


class CleanupManager:
    """
    Manager for safe cleanup of multiple resources.

    Ensures all cleanup operations are attempted even if some fail.

    Example:
        cleanup = CleanupManager()
        cleanup.add(self.timer.stop, "타이머 정지")
        cleanup.add(self.worker.cancel, "워커 취소")
        cleanup.add(self.file.close, "파일 닫기")

        failed = cleanup.execute()
        if failed:
            logger.warning(f"Cleanup failures: {failed}")
    """

    def __init__(self):
        self._tasks = []

    def add(
        self,
        func: Callable,
        description: str = "",
        *args,
        **kwargs
    ) -> 'CleanupManager':
        """
        Add a cleanup task.

        Args:
            func: Cleanup function to call
            description: Description for error messages
            *args, **kwargs: Arguments for the function

        Returns:
            Self for chaining
        """
        self._tasks.append((func, description, args, kwargs))
        return self

    def execute(self) -> list:
        """
        Execute all cleanup tasks.

        Returns:
            List of failed task descriptions with errors
        """
        failed = []

        for func, desc, args, kwargs in self._tasks:
            try:
                func(*args, **kwargs)
            except Exception as e:
                error_desc = desc or func.__name__
                logger.error(f"정리 작업 실패 [{error_desc}]: {e}")
                failed.append((error_desc, str(e)))

        self._tasks.clear()
        return failed


# Convenience function for one-off safe operations
def try_or_log(
    func: Callable,
    *args,
    error_message: str = "작업 실패",
    default: Any = None,
    **kwargs
) -> Any:
    """
    Execute function with logging on error.

    Simple wrapper for one-off safe operations.

    Args:
        func: Function to execute
        *args: Function arguments
        error_message: Error message for logging
        default: Default return value on error
        **kwargs: Function keyword arguments

    Returns:
        Function result or default on error

    Example:
        result = try_or_log(
            self.api.get_data,
            endpoint,
            error_message="데이터 조회 실패",
            default=[]
        )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_message}: {e}")
        return default
