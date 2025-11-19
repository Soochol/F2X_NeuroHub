"""
Production Tracker App - Main Entry Point.

A dedicated work start/completion tracking application for manufacturing floor use.
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox

# Import configuration
from utils.config import AppConfig

# Import services
from services.api_client import APIClient
from services.auth_service import AuthService
from services.work_service import WorkService
from services.barcode_service import BarcodeService
from services.completion_watcher import CompletionWatcher
from services.print_service import PrintService

# Import viewmodels
from viewmodels.main_viewmodel import MainViewModel

# Import views
from views.main_window import MainWindow
from views.login_dialog import LoginDialog

# Import utilities
from utils.logger import setup_logger
from utils.theme_manager import load_theme

# Setup logger
logger = setup_logger()


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("Production Tracker App Starting...")
    logger.info("=" * 60)

    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("F2X Production Tracker")
    app.setOrganizationName("F2X")

    # Note: High DPI scaling is enabled by default in Qt6/PySide6

    # Load theme and apply global styles
    try:
        load_theme(app, "production_tracker")
        logger.info("Theme loaded and applied: production_tracker")
    except Exception as e:
        logger.warning("Failed to load theme: %s", e)

    try:
        # Load configuration
        config = AppConfig()

        # Set API URL to 8001 (backend port)
        config.api_base_url = "http://localhost:8001"

        logger.info(
            f"Configuration loaded: Process {config.process_number} ({config.process_name})"
        )
        logger.info(f"API URL: {config.api_base_url}")
        logger.info(f"Watch Folder: {config.watch_folder}")

        # Initialize API Client
        api_client = APIClient(config.api_base_url)
        logger.info("API Client initialized")

        # Initialize Auth Service
        auth_service = AuthService(api_client)
        logger.info("Auth Service initialized")

        # Authentication flow
        authenticated = False

        # Check for auto-login
        if config.auto_login_enabled and config.saved_token:
            logger.info("Attempting auto-login...")
            api_client.set_token(config.saved_token)

            # Synchronous token validation
            try:
                response = api_client.get("/api/v1/auth/me")
                if response:
                    auth_service.current_user = response
                    logger.info("Auto-login successful")
                    authenticated = True
                else:
                    logger.info("Auto-login failed: Invalid response")
            except Exception as e:
                logger.info(f"Auto-login failed: {e}")

            if not authenticated:
                config.clear_auth()
                api_client.clear_token()

        # Show login dialog if not authenticated
        if not authenticated:
            logger.info("Showing login dialog")
            login_dialog = LoginDialog(auth_service, config)
            if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
                logger.info("Login cancelled by user")
                return 0
            logger.info("Login successful")

        # Initialize Work Service
        work_service = WorkService(api_client, config)
        logger.info("Work Service initialized")

        # Initialize Barcode Service
        barcode_service = BarcodeService()
        logger.info("Barcode Service initialized")

        # Initialize services based on process type
        print_service = None
        completion_watcher = None

        if config.is_label_printing_process:
            # Process 7: Use PrintService instead of CompletionWatcher
            print_service = PrintService(config)
            logger.info("Print Service initialized (Process 7 - Label Printing)")

            # Create dummy completion watcher (not used but required by ViewModel)
            completion_watcher = CompletionWatcher(
                config.watch_folder, config.process_id
            )
            completion_watcher.stop()  # Stop immediately - not needed for Process 7
        else:
            # Other processes: Use CompletionWatcher
            completion_watcher = CompletionWatcher(
                config.watch_folder, config.process_id
            )
            logger.info("Completion Watcher initialized")

        # Create ViewModel
        viewmodel = MainViewModel(
            config=config,
            api_client=api_client,
            auth_service=auth_service,
            work_service=work_service,
            barcode_service=barcode_service,
            completion_watcher=completion_watcher,
            print_service=print_service,
        )
        logger.info("ViewModel created")

        # Create Main Window
        window = MainWindow(viewmodel, config)
        window.show()
        logger.info("Main window shown")

        # Initial stats refresh
        viewmodel.refresh_stats()

        logger.info("Application ready")
        logger.info("=" * 60)

        # Run application
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            "치명적 오류",
            f"애플리케이션 시작 중 오류가 발생했습니다:\n\n{str(e)}\n\n"
            f"자세한 내용은 로그 파일을 확인하세요.",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
