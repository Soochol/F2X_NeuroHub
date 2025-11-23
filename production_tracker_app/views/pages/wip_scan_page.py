"""
WIP Scan Page for Production Tracker App.

Displays large barcode input field and WIP information.
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.theme_manager import get_theme
from widgets.toast_notification import Toast
from utils.exception_handler import safe_slot

logger = logging.getLogger(__name__)
theme = get_theme()


class WIPScanPage(QWidget):
    """WIP Scan page with barcode input and information display."""

    # Signals
    wip_selected = Signal(str)  # WIP ID selected

    def __init__(self, viewmodel, config):
        """
        Initialize WIPScanPage.

        Args:
            viewmodel: WIPScanViewModel instance
            config: AppConfig instance
        """
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        spacing = theme.get("spacing.lg", 16)
        layout.setSpacing(spacing)
        layout.setContentsMargins(spacing, spacing, spacing, spacing)

        # Header
        title = QLabel("WIP 바코드 스캔")
        title.setProperty("variant", "page_title")
        layout.addWidget(title)

        # Barcode input section
        input_group = QGroupBox("바코드 입력")
        input_layout = QVBoxLayout(input_group)

        help_label = QLabel("Serial 번호를 스캔하거나 입력하세요")
        help_label.setProperty("variant", "help_text")
        input_layout.addWidget(help_label)

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Serial 번호 (예: KR01PSA2511001)")
        self.barcode_input.returnPressed.connect(self._on_scan)

        # Large font for barcode input
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.barcode_input.setFont(font)
        self.barcode_input.setMinimumHeight(60)

        input_layout.addWidget(self.barcode_input)

        # Scan button
        scan_btn = QPushButton("스캔")
        scan_btn.setProperty("variant", "primary")
        scan_btn.clicked.connect(self._on_scan)
        scan_btn.setMinimumHeight(50)
        input_layout.addWidget(scan_btn)

        layout.addWidget(input_group)

        # WIP Information section
        info_group = QGroupBox("WIP 정보")
        info_layout = QVBoxLayout(info_group)

        # LOT 정보
        lot_layout = QHBoxLayout()
        lot_label = QLabel("LOT:")
        lot_label.setProperty("variant", "label")
        self.lot_value = QLabel("--")
        self.lot_value.setProperty("variant", "value")
        lot_layout.addWidget(lot_label)
        lot_layout.addWidget(self.lot_value)
        lot_layout.addStretch()
        info_layout.addLayout(lot_layout)

        # 제품 정보
        product_layout = QHBoxLayout()
        product_label = QLabel("제품:")
        product_label.setProperty("variant", "label")
        self.product_value = QLabel("--")
        self.product_value.setProperty("variant", "value")
        product_layout.addWidget(product_label)
        product_layout.addWidget(self.product_value)
        product_layout.addStretch()
        info_layout.addLayout(product_layout)

        # 현재 공정
        process_layout = QHBoxLayout()
        process_label = QLabel("현재 공정:")
        process_label.setProperty("variant", "label")
        self.process_value = QLabel("--")
        self.process_value.setProperty("variant", "value")
        process_layout.addWidget(process_label)
        process_layout.addWidget(self.process_value)
        process_layout.addStretch()
        info_layout.addLayout(process_layout)

        # 공정 상태
        status_layout = QHBoxLayout()
        status_label = QLabel("상태:")
        status_label.setProperty("variant", "label")
        self.status_value = QLabel("--")
        self.status_value.setProperty("variant", "value")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_value)
        status_layout.addStretch()
        info_layout.addLayout(status_layout)

        layout.addWidget(info_group)

        # Scan history section
        history_group = QGroupBox("스캔 이력")
        history_layout = QVBoxLayout(history_group)

        history_header = QHBoxLayout()
        history_title = QLabel("최근 스캔")
        history_header.addWidget(history_title)
        history_header.addStretch()

        clear_btn = QPushButton("이력 지우기")
        clear_btn.setProperty("variant", "secondary")
        clear_btn.clicked.connect(self._on_clear_history)
        history_header.addWidget(clear_btn)
        history_layout.addLayout(history_header)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(200)
        history_layout.addWidget(self.history_list)

        layout.addWidget(history_group)

        layout.addStretch()

        # Focus on input
        self.barcode_input.setFocus()

    def connect_signals(self):
        """Connect ViewModel signals."""
        self.viewmodel.wip_scanned.connect(self._on_wip_scanned)
        self.viewmodel.scan_history_updated.connect(self._on_history_updated)
        self.viewmodel.error_occurred.connect(self._on_error)

    def _on_scan(self):
        """Handle scan button click."""
        wip_id = self.barcode_input.text().strip().upper()

        if not wip_id:
            Toast.warning(self, "Serial 번호를 입력하세요")
            return

        # Clear input
        self.barcode_input.clear()

        # Scan WIP
        self.viewmodel.scan_wip(wip_id)

        # Re-focus input
        self.barcode_input.setFocus()

    @safe_slot("WIP 스캔 결과 표시 실패")
    def _on_wip_scanned(self, wip_info: dict):
        """Handle WIP scanned."""
        logger.info(f"WIP scanned: {wip_info}")

        # Update LOT
        lot_number = wip_info.get("lot_number", "--")
        self.lot_value.setText(lot_number)

        # Update Product
        product_name = wip_info.get("product_name", "--")
        self.product_value.setText(product_name)

        # Update Process
        current_process = wip_info.get("current_process", "--")
        self.process_value.setText(current_process)

        # Update Status (with color coding)
        status = wip_info.get("status", "UNKNOWN")
        self.status_value.setText(status)

        if status == "PASS":
            self.status_value.setStyleSheet(
                f"color: {theme.get('colors.semantic.success', '#10B981')}; font-weight: bold;"
            )
        elif status == "FAIL":
            self.status_value.setStyleSheet(
                f"color: {theme.get('colors.semantic.error', '#EF4444')}; font-weight: bold;"
            )
        elif status == "IN_PROGRESS":
            self.status_value.setStyleSheet(
                f"color: {theme.get('colors.semantic.warning', '#F59E0B')}; font-weight: bold;"
            )
        else:
            self.status_value.setStyleSheet(
                f"color: {theme.get('colors.text.secondary', '#737373')};"
            )

        Toast.success(self, f"WIP 스캔 완료: {lot_number}")

        # Emit selection signal
        serial_number = wip_info.get("serial_number", "")
        if serial_number:
            self.wip_selected.emit(serial_number)

    @safe_slot("스캔 이력 업데이트 실패")
    def _on_history_updated(self, history: list):
        """Handle scan history updated."""
        self.history_list.clear()

        for entry in history:
            timestamp = entry.get("timestamp", "")
            wip_id = entry.get("wip_id", "")
            success = entry.get("success", False)

            # Format timestamp
            time_str = timestamp.split("T")[1][:8] if "T" in timestamp else timestamp

            if success:
                lot_number = entry.get("lot_number", "")
                text = f"[{time_str}] {wip_id} - {lot_number}"
                item = QListWidgetItem(text)
                item.setForeground(
                    theme.get_qt_color("colors.semantic.success", "#10B981")
                )
            else:
                error = entry.get("error", "")
                text = f"[{time_str}] {wip_id} - 실패: {error}"
                item = QListWidgetItem(text)
                item.setForeground(
                    theme.get_qt_color("colors.semantic.error", "#EF4444")
                )

            self.history_list.addItem(item)

    def _on_clear_history(self):
        """Handle clear history button."""
        self.viewmodel.clear_history()
        Toast.info(self, "이력이 지워졌습니다")

    @safe_slot("에러 처리 실패")
    def _on_error(self, error_msg: str):
        """Handle error."""
        logger.error(f"Error: {error_msg}")
        Toast.danger(self, f"오류: {error_msg}")

    def focus_input(self):
        """Focus on barcode input field."""
        self.barcode_input.setFocus()
        self.barcode_input.selectAll()

    def cleanup(self):
        """Clean up resources."""
        self.viewmodel.cleanup()
