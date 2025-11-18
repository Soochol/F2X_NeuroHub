"""
Demo Mode - Launch app with Visual Debugger.

This script launches the Production Tracker app with the Visual Debugger enabled
for analyzing the GUI layout, widget properties, and detecting issues.

Usage:
    python demo_mode.py
"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

# Import configuration
from config import AppConfig

# Import services
from services.api_client import APIClient
from services.auth_service import AuthService
from services.work_service import WorkService
from services.barcode_service import BarcodeService
from services.completion_watcher import CompletionWatcher

# Import viewmodels
from viewmodels.main_viewmodel import MainViewModel

# Import views
from views.main_window import MainWindow

# Import utilities
from utils.logger import setup_logger

# Import Visual Debugger
from visual_debugger import launch_with_debugger

# Setup logger
logger = setup_logger()


def main():
    """Demo mode entry point with visual debugger."""
    logger.info("=" * 60)
    logger.info("Production Tracker App - DEMO MODE WITH VISUAL DEBUGGER")
    logger.info("=" * 60)

    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("F2X Production Tracker - Demo")
    app.setOrganizationName("F2X")

    # High DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)

    try:
        # Load configuration
        config = AppConfig()
        logger.info(f"Configuration loaded: Process {config.process_number} ({config.process_name})")

        # Initialize API Client
        api_client = APIClient(config.api_base_url)

        # Initialize Auth Service
        auth_service = AuthService(api_client)

        # Mock authentication for demo
        logger.info("Mock authentication for demo mode")
        api_client.set_token("mock-token-for-demo")
        auth_service.current_user = {
            "username": "demo",
            "id": 999,
            "full_name": "Demo User"
        }

        # Initialize Services
        work_service = WorkService(api_client, config)
        barcode_service = BarcodeService()
        completion_watcher = CompletionWatcher(config.watch_folder, config.process_id)

        # Create ViewModel
        viewmodel = MainViewModel(
            config=config,
            api_client=api_client,
            auth_service=auth_service,
            work_service=work_service,
            barcode_service=barcode_service,
            completion_watcher=completion_watcher
        )
        logger.info("ViewModel created")

        # Create Main Window
        window = MainWindow(viewmodel, config)
        window.show()
        logger.info("Main window shown")

        # Launch Visual Debugger
        logger.info("🔍 Launching Visual Debugger...")
        debugger = launch_with_debugger(window)
        logger.info("✅ Visual Debugger launched successfully")

        logger.info("=" * 60)
        logger.info("DEMO MODE INSTRUCTIONS:")
        logger.info("1. Main app window is running at 800x700px")
        logger.info("2. Visual Debugger window shows widget tree")
        logger.info("3. Click any widget in tree to inspect properties")
        logger.info("4. Check 'Show All Borders' to visualize layouts")
        logger.info("5. View Issues tab for automatic problem detection")
        logger.info("=" * 60)

        # Run application
        exit_code = app.exec()
        logger.info(f"Demo mode exited with code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.critical(f"Fatal error in demo mode: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            "Demo Mode Error",
            f"Error launching demo mode:\n\n{str(e)}\n\n"
            f"Check log file for details."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
