"""
Settings Page - Inline settings configuration.
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                                QComboBox, QLineEdit, QPushButton, QLabel,
                                QFileDialog, QMessageBox, QFrame)
from PySide6.QtCore import Signal

from utils.theme_manager import get_theme
from services.api_client import APIClient
from views.dialogs.printer_config_dialog import PrinterConfigDialog

logger = logging.getLogger(__name__)
theme = get_theme()

# Try to import PrintService for printer list
try:
    from services.print_service import PrintService
    PRINT_SERVICE_AVAILABLE = True
except ImportError:
    PRINT_SERVICE_AVAILABLE = False


class SettingsPage(QWidget):
    """Settings page for inline configuration."""

    # Signal emitted when settings are saved
    settings_saved = Signal()

    def __init__(self, config, print_service: Optional['PrintService'] = None, api_client: Optional[APIClient] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.print_service = print_service
        self.api_client = api_client

        # Cache for API data
        self._production_lines = []
        self._equipment_list = []
        self._processes = []

        self.setup_ui()
        self._apply_styles()

        # Load data from API after UI setup
        self._load_api_data()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header = QLabel("설정")
        header.setStyleSheet(
            f"font-size: 16px; font-weight: 600; color: {theme.get('colors.text.primary')}; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        desc = QLabel("앱 환경을 설정합니다.")
        desc.setStyleSheet(f"color: {theme.get('colors.grey.400')}; font-size: 12px; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Process settings
        layout.addWidget(self._create_process_section())

        # Folder settings
        layout.addWidget(self._create_folder_section())

        # Equipment settings
        layout.addWidget(self._create_equipment_section())

        # API settings
        layout.addWidget(self._create_api_section())

        # Printer settings
        layout.addWidget(self._create_printer_section())

        layout.addStretch()

        # Save button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("설정 저장")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

    def _apply_styles(self):
        """Apply styles for the settings page."""
        text_secondary = theme.get('colors.grey.300')
        bg_elevated = theme.get('colors.background.elevated')
        border_light = theme.get('colors.border.light')
        text_primary = theme.get('colors.text.primary')
        brand = theme.get('colors.brand.main')
        grey_400 = theme.get('colors.grey.400')
        text_on_brand = theme.get('colors.text.onBrand')
        bg_hover = theme.get('colors.background.hover')
        brand_light = theme.get('colors.brand.light')

        self.setStyleSheet(f"""
            QLabel {{
                color: {text_secondary};
                font-size: 13px;
            }}

            QLineEdit, QComboBox {{
                background-color: {bg_elevated};
                border: 1px solid {border_light};
                border-radius: 4px;
                padding: 6px 10px;
                color: {text_primary};
                font-size: 12px;
                min-height: 16px;
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
                border-radius: 4px;
                padding: 6px 12px;
                color: {text_primary};
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }}

            QPushButton:hover {{
                background-color: {bg_hover};
            }}

            #save_button {{
                background-color: {brand};
                border: none;
                color: {text_on_brand};
                font-weight: 600;
                padding: 8px 20px;
            }}

            #save_button:hover {{
                background-color: {brand_light};
            }}
        """)

    def _create_section_frame(self, title: str) -> tuple:
        """Create a styled section frame with layout."""
        bg_paper = theme.get('colors.background.paper')
        border = theme.get('colors.border.default')
        brand = theme.get('colors.brand.main')

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_paper};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {brand}; font-size: 14px; font-weight: 600; border: none;")
        layout.addWidget(title_label)

        return frame, layout

    def _create_process_section(self) -> QFrame:
        """Create process settings section."""
        frame, layout = self._create_section_frame("공정 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # Process selection with refresh button
        process_layout = QHBoxLayout()
        self.process_combo = QComboBox()
        self.process_combo.addItem("(공정 선택)", None)
        process_layout.addWidget(self.process_combo, 1)

        # Refresh button for processes
        process_refresh_btn = QPushButton("새로고침")
        process_refresh_btn.setFixedWidth(70)
        process_refresh_btn.clicked.connect(self._refresh_processes)
        process_layout.addWidget(process_refresh_btn)

        form_layout.addRow("공정:", process_layout)

        layout.addLayout(form_layout)
        return frame

    def _create_folder_section(self) -> QFrame:
        """Create folder settings section."""
        frame, layout = self._create_section_frame("파일 감시 폴더")

        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self.config.watch_folder)
        folder_layout.addWidget(self.folder_input)

        browse_button = QPushButton("찾아보기")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_button)

        layout.addLayout(folder_layout)
        return frame

    def _create_equipment_section(self) -> QFrame:
        """Create equipment settings section."""
        frame, layout = self._create_section_frame("설비 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # Production line selection
        line_layout = QHBoxLayout()
        self.line_combo = QComboBox()
        self.line_combo.addItem("(생산라인 선택)", None)
        line_layout.addWidget(self.line_combo, 1)

        # Refresh button for production lines
        line_refresh_btn = QPushButton("새로고침")
        line_refresh_btn.setFixedWidth(70)
        line_refresh_btn.clicked.connect(self._refresh_production_lines)
        line_layout.addWidget(line_refresh_btn)

        form_layout.addRow("생산라인:", line_layout)

        # Equipment selection
        equip_layout = QHBoxLayout()
        self.equipment_combo = QComboBox()
        self.equipment_combo.addItem("(장비 선택)", None)
        equip_layout.addWidget(self.equipment_combo, 1)

        # Refresh button for equipment
        equip_refresh_btn = QPushButton("새로고침")
        equip_refresh_btn.setFixedWidth(70)
        equip_refresh_btn.clicked.connect(self._refresh_equipment)
        equip_layout.addWidget(equip_refresh_btn)

        form_layout.addRow("장비:", equip_layout)

        layout.addLayout(form_layout)
        return frame

    def _load_api_data(self):
        """Load processes, production lines and equipment from API."""
        if not self.api_client:
            logger.warning("API client not available, skipping data load")
            return

        self._refresh_processes()
        self._refresh_production_lines()
        self._refresh_equipment()

    def _refresh_processes(self):
        """Refresh processes from API."""
        if not self.api_client:
            QMessageBox.warning(self, "경고", "API 클라이언트가 설정되지 않았습니다.")
            return

        try:
            self._processes = self.api_client.get_processes()

            # Clear and repopulate combo
            self.process_combo.clear()
            self.process_combo.addItem("(공정 선택)", None)

            for process in self._processes:
                process_num = process.get('process_number', 0)
                process_name = process.get('process_name_ko', '')
                display_text = f"{process_num}. {process_name}"
                self.process_combo.addItem(display_text, process)
                logger.debug(f"Added process item: '{display_text}'")

            # Log combo box state
            logger.info(f"Process combo count: {self.process_combo.count()}")

            # Restore saved selection
            saved_id = self.config.process_db_id
            logger.debug(f"Saved process_db_id: {saved_id}, process_number: {self.config.process_number}")

            if saved_id:
                for i in range(1, self.process_combo.count()):
                    data = self.process_combo.itemData(i)
                    if data and data.get('id') == saved_id:
                        self.process_combo.setCurrentIndex(i)
                        logger.debug(f"Restored selection by db_id: index {i}")
                        break
            else:
                # Fallback to process_number if db_id not set
                saved_number = self.config.process_number
                if saved_number:
                    for i in range(1, self.process_combo.count()):
                        data = self.process_combo.itemData(i)
                        if data and data.get('process_number') == saved_number:
                            self.process_combo.setCurrentIndex(i)
                            logger.debug(f"Restored selection by process_number: index {i}")
                            break

            # Force UI update
            self.process_combo.update()

            logger.info(f"Loaded {len(self._processes)} processes, current index: {self.process_combo.currentIndex()}")

        except Exception as e:
            logger.error(f"Failed to load processes: {e}")
            QMessageBox.warning(self, "오류", f"공정 목록 로드 실패: {str(e)}")

    def _refresh_production_lines(self):
        """Refresh production lines from API."""
        if not self.api_client:
            QMessageBox.warning(self, "경고", "API 클라이언트가 설정되지 않았습니다.")
            return

        try:
            self._production_lines = self.api_client.get_production_lines()

            # Clear and repopulate combo
            self.line_combo.clear()
            self.line_combo.addItem("(생산라인 선택)", None)

            for line in self._production_lines:
                display_text = f"{line['line_code']} - {line['line_name']}"
                self.line_combo.addItem(display_text, line)

            # Restore saved selection
            saved_id = self.config.line_id
            if saved_id:
                for i in range(1, self.line_combo.count()):
                    data = self.line_combo.itemData(i)
                    if data and data.get('id') == saved_id:
                        self.line_combo.setCurrentIndex(i)
                        break

            logger.info(f"Loaded {len(self._production_lines)} production lines")

        except Exception as e:
            logger.error(f"Failed to load production lines: {e}")
            QMessageBox.warning(self, "오류", f"생산라인 목록 로드 실패: {str(e)}")

    def _refresh_equipment(self):
        """Refresh equipment list from API."""
        if not self.api_client:
            QMessageBox.warning(self, "경고", "API 클라이언트가 설정되지 않았습니다.")
            return

        try:
            self._equipment_list = self.api_client.get_equipment()

            # Clear and repopulate combo
            self.equipment_combo.clear()
            self.equipment_combo.addItem("(장비 선택)", None)

            for equip in self._equipment_list:
                display_text = f"{equip['equipment_code']} - {equip['equipment_name']}"
                self.equipment_combo.addItem(display_text, equip)

            # Restore saved selection
            saved_id = self.config.equipment_id
            if saved_id:
                for i in range(1, self.equipment_combo.count()):
                    data = self.equipment_combo.itemData(i)
                    if data and data.get('id') == saved_id:
                        self.equipment_combo.setCurrentIndex(i)
                        break

            logger.info(f"Loaded {len(self._equipment_list)} equipment")

        except Exception as e:
            logger.error(f"Failed to load equipment: {e}")
            QMessageBox.warning(self, "오류", f"장비 목록 로드 실패: {str(e)}")

    def _create_api_section(self) -> QFrame:
        """Create API settings section."""
        frame, layout = self._create_section_frame("API 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.api_input = QLineEdit(self.config.api_base_url)
        form_layout.addRow("백엔드 URL:", self.api_input)

        layout.addLayout(form_layout)
        return frame

    def _create_printer_section(self) -> QFrame:
        """Create printer settings section."""
        frame, layout = self._create_section_frame("프린터 설정")

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        # Printer selection
        self.printer_combo = QComboBox()
        self.printer_combo.addItem("(프린터 선택)", "")
        self._populate_printers()
        form_layout.addRow("프린터:", self.printer_combo)

        # ZPL template path
        zpl_layout = QHBoxLayout()
        self.zpl_input = QLineEdit(self.config.zpl_template_path)
        self.zpl_input.setPlaceholderText("ZPL 템플릿 파일 경로 (선택)")
        zpl_layout.addWidget(self.zpl_input)

        zpl_browse_button = QPushButton("찾아보기")
        zpl_browse_button.clicked.connect(self.browse_zpl_template)
        zpl_layout.addWidget(zpl_browse_button)
        form_layout.addRow("ZPL 템플릿:", zpl_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Advanced config button
        advanced_button = QPushButton("고급 설정")
        advanced_button.setProperty("variant", "secondary")
        advanced_button.clicked.connect(self.open_printer_config)
        button_layout.addWidget(advanced_button)

        test_button = QPushButton("테스트 출력")
        test_button.clicked.connect(self.test_print)
        button_layout.addWidget(test_button)

        form_layout.addRow("", button_layout)

        layout.addLayout(form_layout)
        return frame

    def browse_folder(self):
        """Open folder browser."""
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def browse_zpl_template(self):
        """Open file browser for ZPL template."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ZPL 템플릿 선택",
            self.zpl_input.text(),
            "ZPL Files (*.zpl *.prn *.txt);;All Files (*)"
        )
        if file_path:
            self.zpl_input.setText(file_path)

    def _populate_printers(self):
        """Populate printer combo box with available printers."""
        printers = []

        if self.print_service:
            printers = self.print_service.get_available_printers()
        elif PRINT_SERVICE_AVAILABLE:
            try:
                temp_service = PrintService(self.config)
                printers = temp_service.get_available_printers()
            except Exception as e:
                logger.warning(f"Failed to get printer list: {e}")

        for printer in printers:
            self.printer_combo.addItem(printer, printer)

        current_printer = self.config.printer_queue
        if current_printer:
            index = self.printer_combo.findData(current_printer)
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)

    def open_printer_config(self):
        """Open advanced printer configuration dialog."""
        dialog = PrinterConfigDialog(self.config, self.print_service, self)
        dialog.printer_configured.connect(self._on_printer_configured)
        dialog.exec()

    def _on_printer_configured(self, config_data: dict):
        """Handle printer configuration saved."""
        logger.info(f"Printer configured: {config_data}")

        # Refresh printer list if USB printer was configured
        if config_data.get("printer_type") == "usb":
            self._populate_printers()

        QMessageBox.information(self, "설정 완료", "프린터 설정이 적용되었습니다.")

    def test_print(self):
        """Test print with selected printer."""
        selected_printer = self.printer_combo.currentData()

        if not selected_printer:
            QMessageBox.warning(self, "경고", "프린터를 선택해주세요.")
            return

        self.config.printer_queue = selected_printer
        self.config.zpl_template_path = self.zpl_input.text()

        if self.print_service:
            self.print_service.set_printer(selected_printer)
            success = self.print_service.test_print()
        elif PRINT_SERVICE_AVAILABLE:
            try:
                temp_service = PrintService(self.config)
                temp_service.set_printer(selected_printer)
                success = temp_service.test_print()
            except Exception as e:
                QMessageBox.critical(self, "오류", f"테스트 출력 실패: {str(e)}")
                return
        else:
            QMessageBox.warning(self, "경고", "Zebra 라이브러리가 설치되지 않았습니다.")
            return

        if success:
            QMessageBox.information(self, "성공", "테스트 라벨이 출력되었습니다.")
        else:
            QMessageBox.warning(self, "실패", "테스트 출력에 실패했습니다.")

    def save_settings(self):
        """Save settings to config."""
        try:
            # Save process selection
            process_data = self.process_combo.currentData()
            if process_data:
                self.config.process_db_id = process_data.get('id', 0)
                self.config.process_number = process_data.get('process_number', 1)
                self.config.process_code = process_data.get('process_code', '')
                self.config.process_name = process_data.get('process_name_ko', '')
                self.config.process_name_en = process_data.get('process_name_en', '')
            else:
                self.config.process_db_id = 0
                self.config.process_number = 1
                self.config.process_code = ''
                self.config.process_name = ''
                self.config.process_name_en = ''

            self.config.watch_folder = self.folder_input.text()

            # Save production line selection
            line_data = self.line_combo.currentData()
            if line_data:
                self.config.line_id = line_data.get('id', 0)
                self.config.line_code = line_data.get('line_code', '')
                self.config.line_name = line_data.get('line_name', '')
            else:
                self.config.line_id = 0
                self.config.line_code = ''
                self.config.line_name = ''

            # Save equipment selection
            equip_data = self.equipment_combo.currentData()
            if equip_data:
                self.config.equipment_id = equip_data.get('id', 0)
                self.config.equipment_code = equip_data.get('equipment_code', '')
                self.config.equipment_name = equip_data.get('equipment_name', '')
            else:
                self.config.equipment_id = 0
                self.config.equipment_code = ''
                self.config.equipment_name = ''

            self.config.api_base_url = self.api_input.text()
            self.config.printer_queue = self.printer_combo.currentData() or ""
            self.config.zpl_template_path = self.zpl_input.text()

            logger.info("Settings saved successfully")
            self.settings_saved.emit()
            QMessageBox.information(self, "저장 완료", "설정이 저장되었습니다.")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "오류", f"설정 저장 실패: {str(e)}")
