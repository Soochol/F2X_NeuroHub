# Services package
"""
Services layer for Production Tracker App.

This package contains:
- interfaces: Abstract base classes for service contracts
- api_client: REST API communication
- auth_service: JWT authentication lifecycle
- work_service: Work start/complete operations
- barcode_service: USB HID barcode scanning
- completion_watcher: JSON file monitoring
- tcp_server: Equipment TCP communication
- history_manager: Event logging
- workers: Background worker threads
"""

from .interfaces import (
    IAPIClient,
    IAuthService,
    IWorkService,
    IBarcodeService,
    ICompletionWatcher,
    ITCPServer,
    IHistoryManager,
)

__all__ = [
    # Interfaces
    "IAPIClient",
    "IAuthService",
    "IWorkService",
    "IBarcodeService",
    "ICompletionWatcher",
    "ITCPServer",
    "IHistoryManager",
]
