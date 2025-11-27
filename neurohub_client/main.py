"""
Production Tracker App - Main Entry Point.

A dedicated work start/completion tracking application for manufacturing floor use.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

# Import configuration
from utils.config import AppConfig

# Import services
from services.api_client import APIClient
from services.auth_service import AuthService
from services.work_service import WorkService
from services.barcode_service import BarcodeService
from services.completion_watcher import CompletionWatcher
from services.tcp_server import TCPServer

# Import viewmodels
from viewmodels.main_viewmodel import MainViewModel

# Import views
from views.main_window import MainWindow
from views.login_dialog import LoginDialog

# Import utilities
from utils.logger import setup_logger
from utils.theme_manager import load_theme
from utils.exception_handler import ExceptionHandler

# Setup logger
logger = setup_logger()

# Install global exception handler
ExceptionHandler.install_global_handler()

# Note: TCP_SERVER_PORT is now configured in AppConfig (tcp_port property)


def main():
    """Main application entry point."""
    logger.info("=" * 60)
    logger.info("Production Tracker App Starting...")
    logger.info("=" * 60)

    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("F2X Production Tracker")
    app.setOrganizationName("F2X")

    # Set application icon
    icon_path = Path(__file__).parent / "resources" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        logger.info(f"Application icon set: {icon_path}")

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

        # Authentication flow - Always require login
        logger.info("Always requiring login - auto-login disabled")

        # Show login dialog
        if True:
            logger.info("Showing login dialog")
            login_dialog = LoginDialog(auth_service, config)
            if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
                logger.info("Login cancelled by user")
                return 0
            logger.info("Login successful")

            # Mark first run as completed after successful login
            if not config.first_run_completed:
                config.first_run_completed = True
                logger.info("First run completed - future auto-login enabled")

        # Load production lines and equipment from API
        logger.info("Loading production lines and equipment from API...")
        production_lines = []
        equipment_list = []

        try:
            production_lines = api_client.get_production_lines()
            logger.info(f"Loaded {len(production_lines)} production lines")
        except Exception as e:
            logger.warning(f"Failed to load production lines: {e}")

        try:
            equipment_list = api_client.get_equipment()
            logger.info(f"Loaded {len(equipment_list)} equipment")
        except Exception as e:
            logger.warning(f"Failed to load equipment: {e}")

        # Validate saved settings
        if config.line_id and production_lines:
            line_exists = any(
                line.get('id') == config.line_id for line in production_lines
            )
            if not line_exists:
                logger.warning(
                    f"Saved line_id {config.line_id} not found in database. "
                    "Please update settings."
                )

        if config.equipment_id and equipment_list:
            equip_exists = any(
                equip.get('id') == config.equipment_id for equip in equipment_list
            )
            if not equip_exists:
                logger.warning(
                    f"Saved equipment_id {config.equipment_id} not found in database. "
                    "Please update settings."
                )

        # Log current settings
        logger.info(
            f"Current settings - Line: {config.line_code or '(미설정)'}, "
            f"Equipment: {config.equipment_code or '(미설정)'}"
        )

        # Initialize Work Service
        work_service = WorkService(api_client, config)
        logger.info("Work Service initialized")

        # Initialize Barcode Service
        barcode_service = BarcodeService()
        logger.info("Barcode Service initialized")

        # Initialize services based on process type
        completion_watcher = CompletionWatcher(
            config.watch_folder, config.process_id
        )
        logger.info("Completion Watcher initialized")

        # Initialize TCP Server for equipment communication
        tcp_port = config.tcp_port
        tcp_server = TCPServer(port=tcp_port)
        # Set services for synchronous API calls (START -> Backend -> ACK)
        tcp_server.set_services(work_service, auth_service)
        logger.info(f"TCP Server initialized (port: {tcp_port})")

        # Create ViewModel
        viewmodel = MainViewModel(
            config=config,
            api_client=api_client,
            auth_service=auth_service,
            work_service=work_service,
            barcode_service=barcode_service,
            completion_watcher=completion_watcher,
            tcp_server=tcp_server,
        )
        logger.info("ViewModel created")

        # Start TCP server
        if tcp_server.start():
            logger.info("TCP Server started successfully")
        else:
            logger.warning("TCP Server failed to start")

        # Create Main Window
        window = MainWindow(viewmodel, config)
        window.show()
        logger.info("Main window shown")

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
