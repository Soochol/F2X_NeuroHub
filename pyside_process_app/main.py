"""Main entry point for F2X NeuroHub MES Desktop Application"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Import modules
from config import AppConfig
from services.api_client import APIClient
from services.auth_service import AuthService
from services.process_service import ProcessService
from services.file_watcher_service import FileWatcherService
from services.history_service import HistoryService
from viewmodels.app_state import AppState
from viewmodels.main_viewmodel import MainViewModel
from views.main_window import MainWindow
from views.login_dialog import LoginDialog
from utils.logger import setup_logger

# Setup logging
logger = setup_logger('neurohub', 'logs')


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("F2X NeuroHub MES")
    app.setOrganizationName("F2X")

    logger.info("=" * 50)
    logger.info("Application starting...")

    # Load configuration
    config = AppConfig()
    logger.info(f"API URL: {config.api_base_url}")
    logger.info(f"Process: {config.process_number} - {config.process_name}")

    # Initialize services
    api_client = APIClient(config.api_base_url)
    auth_service = AuthService(api_client)
    process_service = ProcessService(api_client)
    history_service = HistoryService(api_client)
    file_watcher_service = FileWatcherService(config.json_watch_path)

    # Initialize app state
    app_state = AppState()

    # Initialize ViewModel
    main_viewmodel = MainViewModel(
        process_service,
        file_watcher_service,
        config,
        app_state
    )

    # Auto-login attempt
    if config.auto_login_enabled and config.saved_token:
        logger.info("Attempting auto-login with saved token...")
        api_client.set_token(config.saved_token)

        # Validate token
        if auth_service.validate_token():
            logger.info("Auto-login successful")
            # User info already set in validate_token via auth_service.current_user
            app_state.current_user = auth_service.current_user
            show_main_window(main_viewmodel, config, app_state, history_service)
        else:
            logger.warning("Auto-login failed: token invalid")
            # Show login dialog
            if not show_login_dialog(auth_service, config, app_state):
                return 0
            show_main_window(main_viewmodel, config, app_state, history_service)
    else:
        logger.info("Auto-login disabled or no saved token")
        # Show login dialog
        if not show_login_dialog(auth_service, config, app_state):
            return 0
        show_main_window(main_viewmodel, config, app_state, history_service)

    logger.info("Application running...")
    exit_code = app.exec()
    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


def show_login_dialog(auth_service: AuthService, config: AppConfig, app_state: AppState) -> bool:
    """Show login dialog and return True if successful"""
    login_dialog = LoginDialog(auth_service, config)

    if login_dialog.exec():
        # Login successful, user info already in auth_service.current_user
        if auth_service.current_user:
            app_state.current_user = auth_service.current_user
            logger.info(f"User logged in: {auth_service.current_user.get('username', 'Unknown')}")

            # Save token if auto-login enabled (already handled in LoginDialog)
            # Token is saved in LoginDialog.on_login()

            return True
        else:
            logger.error("Login succeeded but no user info available")
            return False
    else:
        logger.info("Login cancelled by user")
        return False


def show_main_window(main_viewmodel: MainViewModel, config: AppConfig, app_state: AppState, history_service: HistoryService):
    """Show main window and load initial data"""
    main_window = MainWindow(main_viewmodel, config, app_state, history_service)
    main_window.showMaximized()

    # Load initial data after window is shown
    QTimer.singleShot(500, main_viewmodel.load_daily_stats)

    logger.info("Main window displayed")


if __name__ == "__main__":
    sys.exit(main())
