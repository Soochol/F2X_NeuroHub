"""
Settings Dialog with Sidebar Navigation.
"""
import logging
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget
)

from utils.theme_manager import get_theme

logger = logging.getLogger(__name__)
theme = get_theme()

# Try to import PrintService for printer list
try:
    from services.print_service import PrintService
    PRINT_SERVICE_AVAILABLE = True
except ImportError:
    PRINT_SERVICE_AVAILABLE = False


class SettingsDialog(QDialog):
    """Settings dialog with sidebar navigation for configuration."""

    def __init__(
        self,
        config: Any,
        print_service: Optional[Any] = None,
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.print_service = print_service
        self.setWindowTitle("환경설정")
        self.setModal(True)
        self.resize(650, 500)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI components with sidebar navigation."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("settings_sidebar")
        sidebar.setFixedWidth(160)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("settings_nav")
        self.nav_list.setFrameShape(QListWidget.NoFrame)

        # Add navigation items
        nav_items = [
            ("공정 설정", "process"),
            ("파일 감시", "folder"),
            ("설비 설정", "equipment"),
            ("API 설정", "api"),
            ("프린터 설정", "printer"),
        ]

        for label, data in nav_items:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, data)
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)

        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("settings_content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        self.stack.addWidget(self._create_process_page())
        self.stack.addWidget(self._create_folder_page())
        self.stack.addWidget(self._create_equipment_page())
        self.stack.addWidget(self._create_api_page())
        self.stack.addWidget(self._create_printer_page())

        content_layout.addWidget(self.stack)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        save_button = QPushButton("저장")
        save_button.setObjectName("save_button")
        save_button.setProperty("variant", "primary")
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("취소")
        cancel_button.setObjectName("cancel_button")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        content_layout.addLayout(button_layout)

        main_layout.addWidget(content_widget)

        # Select first item
        self.nav_list.setCurrentRow(0)

        # Apply sidebar styles
        self._apply_styles()

    def _apply_styles(self) -> None:
        """Apply styles for sidebar navigation."""
        # Theme colors
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
        bg_hover = theme.get('colors.background.hover')
        border_default = theme.get('colors.border.default')
        border_light = theme.get('colors.border.light')
        text_primary = theme.get('colors.text.primary')
        text_on_brand = theme.get('colors.text.onBrand')
        grey_300 = theme.get('colors.grey.300')
        grey_400 = theme.get('colors.grey.400')
        brand = theme.get('colors.brand.main')
        brand_light = theme.get('colors.brand.light')

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_default};
            }}

            #settings_sidebar {{
                background-color: {border_default};
                border-right: 1px solid {border_light};
            }}

            #settings_nav {{
                background-color: transparent;
                border: none;
                outline: none;
            }}

            #settings_nav::item {{
                padding: 12px 16px;
                border-left: 3px solid transparent;
                color: {grey_300};
                font-size: 13px;
            }}

            #settings_nav::item:selected {{
                background-color: {bg_hover};
                border-left: 3px solid {brand};
                color: {brand};
                font-weight: 600;
            }}

            #settings_nav::item:hover:!selected {{
                background-color: {bg_elevated};
            }}

            #settings_content {{
                background-color: {bg_default};
            }}

            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {text_primary};
                border: 1px solid {border_light};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: {border_default};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }}

            QLabel {{
                color: {grey_300};
                font-size: 13px;
            }}

            QLineEdit, QComboBox {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 8px 12px;
                color: {text_primary};
                font-size: 13px;
                min-height: 20px;
            }}

            QLineEdit:focus, QComboBox:focus {{
                border-color: {brand};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {grey_400};
                margin-right: 8px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                selection-background-color: {brand};
                selection-color: {text_on_brand};
            }}

            QPushButton {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 6px;
                padding: 8px 16px;
                color: {text_primary};
                font-size: 13px;
                font-weight: 500;
                min-width: 80px;
            }}

            QPushButton:hover {{
                background-color: {bg_hover};
            }}

            QPushButton[variant="primary"] {{
                background-color: {brand};
                border: none;
                color: {text_on_brand};
                font-weight: 600;
            }}

            QPushButton[variant="primary"]:hover {{
                background-color: {brand_light};
            }}
        """)

    def _on_nav_changed(self, index: int) -> None:
        """Handle navigation item change."""
        self.stack.setCurrentIndex(index)

    def _create_process_page(self) -> QWidget:
        """Create process settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text_primary = theme.get('colors.text.primary')
        grey_400 = theme.get('colors.grey.400')

        # Header
        header = QLabel("공정 설정")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("현재 작업 공정을 선택합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Process selection
        group = QGroupBox("공정 선택")
        group_layout = QFormLayout(group)
        group_layout.setContentsMargins(16, 20, 16, 16)
        group_layout.setSpacing(12)

        self.process_combo = QComboBox()
        process_names = {
            1: "1. 레이저 마킹", 2: "2. LMA 조립",
            3: "3. 센서 검사", 4: "4. 펌웨어 업로드",
            5: "5. 로봇 조립", 6: "6. 성능검사",
            7: "7. 라벨 프린팅", 8: "8. 포장+외관검사"
        }
        for i in range(1, 9):
            self.process_combo.addItem(process_names[i], i)
        self.process_combo.setCurrentIndex(self.config.process_number - 1)
        group_layout.addRow("공정:", self.process_combo)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def _create_folder_page(self) -> QWidget:
        """Create folder settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text_primary = theme.get('colors.text.primary')
        grey_400 = theme.get('colors.grey.400')

        # Header
        header = QLabel("파일 감시 폴더")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("작업 결과 파일이 생성되는 폴더를 지정합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Folder selection
        group = QGroupBox("감시 폴더")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(16, 20, 16, 16)
        group_layout.setSpacing(12)

        folder_input_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self.config.watch_folder)
        folder_input_layout.addWidget(self.folder_input)

        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.browse_folder)
        folder_input_layout.addWidget(browse_button)

        group_layout.addLayout(folder_input_layout)
        layout.addWidget(group)
        layout.addStretch()
        return page

    def _create_equipment_page(self) -> QWidget:
        """Create equipment settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text_primary = theme.get('colors.text.primary')
        grey_400 = theme.get('colors.grey.400')

        # Header
        header = QLabel("설비 설정")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("설비 및 라인 정보를 설정합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Equipment settings
        group = QGroupBox("설비 정보")
        group_layout = QFormLayout(group)
        group_layout.setContentsMargins(16, 20, 16, 16)
        group_layout.setSpacing(12)

        self.equipment_input = QLineEdit(self.config.equipment_id)
        group_layout.addRow("설비 ID:", self.equipment_input)

        self.line_input = QLineEdit(self.config.line_id)
        group_layout.addRow("라인 ID:", self.line_input)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def _create_api_page(self) -> QWidget:
        """Create API settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text_primary = theme.get('colors.text.primary')
        grey_400 = theme.get('colors.grey.400')

        # Header
        header = QLabel("API 설정")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("백엔드 서버 연결 정보를 설정합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # API settings
        group = QGroupBox("서버 연결")
        group_layout = QFormLayout(group)
        group_layout.setContentsMargins(16, 20, 16, 16)
        group_layout.setSpacing(12)

        self.api_input = QLineEdit(self.config.api_base_url)
        group_layout.addRow("백엔드 URL:", self.api_input)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def _create_printer_page(self) -> QWidget:
        """Create printer settings page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        text_primary = theme.get('colors.text.primary')
        grey_400 = theme.get('colors.grey.400')

        # Header
        header = QLabel("프린터 설정")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {text_primary}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("라벨 프린터 및 템플릿을 설정합니다.")
        desc.setStyleSheet(f"color: {grey_400}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Printer settings
        group = QGroupBox("프린터 설정 (라벨 프린팅)")
        group_layout = QFormLayout(group)
        group_layout.setContentsMargins(16, 20, 16, 16)
        group_layout.setSpacing(12)

        # Printer selection
        self.printer_combo = QComboBox()
        self.printer_combo.addItem("(프린터 선택)", "")
        self._populate_printers()
        group_layout.addRow("프린터:", self.printer_combo)

        # ZPL template path
        zpl_layout = QHBoxLayout()
        self.zpl_input = QLineEdit(self.config.zpl_template_path)
        self.zpl_input.setPlaceholderText("ZPL 템플릿 파일 경로 (선택)")
        zpl_layout.addWidget(self.zpl_input)

        zpl_browse_button = QPushButton("찾아보기")
        zpl_browse_button.clicked.connect(self.browse_zpl_template)
        zpl_layout.addWidget(zpl_browse_button)
        group_layout.addRow("ZPL 템플릿:", zpl_layout)

        # Test print button
        test_print_layout = QHBoxLayout()
        test_print_button = QPushButton("테스트 출력")
        test_print_button.clicked.connect(self.test_print)
        test_print_layout.addStretch()
        test_print_layout.addWidget(test_print_button)
        group_layout.addRow("", test_print_layout)

        layout.addWidget(group)
        layout.addStretch()
        return page

    def browse_folder(self) -> None:
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def _populate_printers(self) -> None:
        """Populate printer combo box with available printers."""
        printers = []

        # Get printers from PrintService if available
        if self.print_service:
            printers = self.print_service.get_available_printers()
        elif PRINT_SERVICE_AVAILABLE:
            # Create temporary PrintService to get printer list
            try:
                temp_service = PrintService(self.config)
                printers = temp_service.get_available_printers()
            except Exception as e:
                logger.warning(f"Failed to get printer list: {e}")

        # Add printers to combo
        for printer in printers:
            self.printer_combo.addItem(printer, printer)

        # Select current printer
        current_printer = self.config.printer_queue
        if current_printer:
            index = self.printer_combo.findData(current_printer)
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)

    def browse_zpl_template(self) -> None:
        """Open file browser for ZPL template."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ZPL 템플릿 선택",
            self.zpl_input.text(),
            "ZPL Files (*.zpl *.prn *.txt);;All Files (*)"
        )
        if file_path:
            self.zpl_input.setText(file_path)

    def test_print(self) -> None:
        """Test print with selected printer."""
        selected_printer = self.printer_combo.currentData()

        if not selected_printer:
            QMessageBox.warning(self, "경고", "프린터를 선택해주세요.")
            return

        # Save printer setting temporarily
        self.config.printer_queue = selected_printer
        self.config.zpl_template_path = self.zpl_input.text()

        if self.print_service:
            # Use existing print service
            self.print_service.set_printer(selected_printer)
            success = self.print_service.test_print()
        elif PRINT_SERVICE_AVAILABLE:
            # Create temporary print service
            try:
                temp_service = PrintService(self.config)
                temp_service.set_printer(selected_printer)
                success = temp_service.test_print()
            except Exception as e:
                QMessageBox.critical(self, "오류", f"테스트 출력 실패: {str(e)}")
                return
        else:
            QMessageBox.warning(self, "경고", "Zebra 라이브러리가 설치되지 않았습니다.\npip install zebra")
            return

        if success:
            QMessageBox.information(self, "성공", "테스트 라벨이 출력되었습니다.")
        else:
            QMessageBox.warning(self, "실패", "테스트 출력에 실패했습니다.")

    def save_settings(self) -> None:
        """Save settings to config."""
        try:
            self.config.process_number = self.process_combo.currentData()
            self.config.watch_folder = self.folder_input.text()
            self.config.equipment_id = self.equipment_input.text()
            self.config.line_id = self.line_input.text()
            self.config.api_base_url = self.api_input.text()

            # Save printer settings
            self.config.printer_queue = self.printer_combo.currentData() or ""
            self.config.zpl_template_path = self.zpl_input.text()

            logger.info("Settings saved successfully")
            self.accept()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 실패: {str(e)}")
