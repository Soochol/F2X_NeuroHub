"""Demo Mode - Show UI without backend authentication"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
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
from utils.logger import setup_logger
from ui_components import load_and_apply_theme

# Setup logging
logger = setup_logger('neurohub_demo', 'logs')


def main():
    """Demo mode entry point - bypasses authentication"""
    app = QApplication(sys.argv)
    app.setApplicationName("F2X NeuroHub MES (Demo Mode)")
    app.setOrganizationName("F2X")

    logger.info("=" * 50)
    logger.info("DEMO MODE - Application starting...")

    # Load theme - Switch between "neurohub" and "supabase"
    theme_name = "supabase"  # Change to "neurohub" for original theme
    logger.info(f"Loading {theme_name} theme...")
    theme = load_and_apply_theme(app, theme_name)
    logger.info(f"{theme_name.capitalize()} theme loaded successfully")

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

    # Set demo user
    app_state.current_user = {
        "id": 1,
        "username": "demo_user",
        "full_name": "데모 사용자",
        "role": "OPERATOR",
        "email": "demo@f2x.com"
    }
    logger.info("Demo user set: demo_user")

    # Initialize ViewModel
    main_viewmodel = MainViewModel(
        process_service,
        file_watcher_service,
        config,
        app_state
    )

    # Show main window
    main_window = MainWindow(main_viewmodel, config, app_state, history_service)
    main_window.showMaximized()
    logger.info("Main window displayed (Demo Mode)")

    # Show info message
    from PySide6.QtWidgets import QMessageBox
    QTimer.singleShot(500, lambda: QMessageBox.information(
        main_window,
        "데모 모드",
        "🎨 F2X NeuroHub MES UI 데모 모드\n\n"
        "백엔드 서버 없이 UI를 확인할 수 있습니다.\n\n"
        "주요 기능:\n"
        "✅ UI 레이아웃 및 디자인 확인\n"
        "✅ 메뉴 및 다이얼로그 탐색\n"
        "✅ 오프라인 모드 UI 확인\n\n"
        "⚠️ 백엔드 연결이 필요한 기능은 오류가 발생할 수 있습니다."
    ))

    logger.info("Application running in demo mode...")
    exit_code = app.exec()
    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
