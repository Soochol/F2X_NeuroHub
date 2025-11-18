"""
Offline Mode Integration Example

This example shows how to integrate offline mode support into your PySide6 application.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import APIClient, OfflineManager, RetryManager, ProcessService, FileWatcherService
from viewmodels.main_viewmodel import MainViewModel
from views.main_window import MainWindow
from config import AppConfig
from models.app_state import AppState


def create_app():
    """Create and configure application with offline mode support"""

    # 1. Create Qt Application
    app = QApplication(sys.argv)

    # 2. Load configuration
    config = AppConfig()

    # 3. Create application state
    app_state = AppState()

    # 4. Create Offline Manager (CRITICAL for offline support)
    offline_manager = OfflineManager(queue_path="offline_queue")

    # 5. Create API Client with offline support
    api_client = APIClient(
        base_url=config.backend_url,  # "http://localhost:8000"
        offline_manager=offline_manager
    )

    # 6. Create Retry Manager (handles auto-retry)
    retry_manager = RetryManager(offline_manager, api_client)

    # 7. Create services
    process_service = ProcessService(api_client)
    file_watcher_service = FileWatcherService(config.json_watch_path)

    # 8. Create ViewModel with offline support
    viewmodel = MainViewModel(
        process_service=process_service,
        file_watcher_service=file_watcher_service,
        config=config,
        app_state=app_state,
        offline_manager=offline_manager,  # IMPORTANT
        retry_manager=retry_manager       # IMPORTANT
    )

    # 9. Create Main Window
    main_window = MainWindow(
        viewmodel=viewmodel,
        config=config,
        app_state=app_state,
        history_service=None  # Add if needed
    )

    # 10. Show window
    main_window.show()

    return app, main_window


def test_offline_mode():
    """Test offline mode functionality"""

    print("\n" + "="*60)
    print("OFFLINE MODE TEST")
    print("="*60)

    # Create components
    offline_manager = OfflineManager(queue_path="test_offline_queue")
    api_client = APIClient(
        base_url="http://localhost:9999",  # Invalid port for testing
        offline_manager=offline_manager
    )
    retry_manager = RetryManager(offline_manager, api_client)

    print("\n1. Testing offline request queuing...")

    # Try to make a request (will fail and queue)
    try:
        api_client.post("/api/v1/test", {"data": "test"})
    except Exception as e:
        print(f"   Expected error: {e}")

    # Check queue
    queue_size = offline_manager.get_queue_size()
    print(f"   Queue size: {queue_size}")

    if queue_size > 0:
        print("   ✓ Request successfully queued!")
    else:
        print("   ✗ Queue is empty - something went wrong")

    print("\n2. Testing queue retrieval...")
    queued_requests = offline_manager.get_queued_requests()
    for i, req in enumerate(queued_requests, 1):
        print(f"   Request {i}:")
        print(f"     - Type: {req['type']}")
        print(f"     - Endpoint: {req['endpoint']}")
        print(f"     - Timestamp: {req['timestamp']}")
        print(f"     - Retry count: {req['retry_count']}")

    print("\n3. Testing manual cleanup...")
    for req in queued_requests:
        offline_manager.remove_from_queue(req['_filename'])

    queue_size = offline_manager.get_queue_size()
    print(f"   Queue size after cleanup: {queue_size}")

    if queue_size == 0:
        print("   ✓ Cleanup successful!")
    else:
        print("   ✗ Cleanup failed")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")


def main():
    """Main entry point"""

    # Option 1: Run full application
    app, main_window = create_app()

    print("\n" + "="*60)
    print("APPLICATION STARTED WITH OFFLINE MODE")
    print("="*60)
    print("\nFeatures enabled:")
    print("  ✓ Connection status indicator (🟢/🔴)")
    print("  ✓ Offline request queuing")
    print("  ✓ Automatic retry on reconnection")
    print("  ✓ Manual retry button")
    print("  ✓ Queue size display")
    print("\nTo test offline mode:")
    print("  1. Stop your backend server")
    print("  2. Try to perform an action (착공/완공)")
    print("  3. Observe offline indicator and queue count")
    print("  4. Restart backend server")
    print("  5. Watch automatic retry or click '재시도'")
    print("\nOffline queue location: offline_queue/")
    print("="*60 + "\n")

    sys.exit(app.exec())

    # Option 2: Run tests only
    # test_offline_mode()


if __name__ == "__main__":
    # Uncomment to run tests instead of full app
    # test_offline_mode()

    main()
