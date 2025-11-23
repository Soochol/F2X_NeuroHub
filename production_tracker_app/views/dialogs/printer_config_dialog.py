"""
Printer Configuration Dialog.

Allows configuration of network and USB printers with connection testing.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QRadioButton, QButtonGroup,
    QSpinBox, QTextEdit, QTabWidget, QWidget, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from utils.theme_manager import get_theme
from utils.zebra_printer import ZebraPrinter
from widgets.toast_notification import Toast
from utils.exception_handler import safe_slot

logger = logging.getLogger(__name__)
theme = get_theme()


class PrinterConfigDialog(QDialog):
    """Dialog for configuring printer settings."""

    printer_configured = Signal(dict)  # Emit when printer is successfully configured

    def __init__(self, config, print_service=None, parent=None):
        """
        Initialize PrinterConfigDialog.

        Args:
            config: AppConfig instance
            print_service: PrintService instance (for USB printers)
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.print_service = print_service
        self.network_printer = ZebraPrinter()

        self.setWindowTitle("프린터 설정")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        spacing = theme.get("spacing.lg", 16)
        layout.setSpacing(spacing)

        # Tab widget for USB vs Network
        self.tab_widget = QTabWidget()

        # Network printer tab
        network_tab = self._create_network_tab()
        self.tab_widget.addTab(network_tab, "네트워크 프린터")

        # USB printer tab
        usb_tab = self._create_usb_tab()
        self.tab_widget.addTab(usb_tab, "USB 프린터")

        # Preview tab
        preview_tab = self._create_preview_tab()
        self.tab_widget.addTab(preview_tab, "미리보기")

        layout.addWidget(self.tab_widget)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        test_btn = QPushButton("연결 테스트")
        test_btn.setProperty("variant", "secondary")
        test_btn.clicked.connect(self._on_test_connection)
        button_layout.addWidget(test_btn)

        cancel_btn = QPushButton("취소")
        cancel_btn.setProperty("variant", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("저장")
        save_btn.setProperty("variant", "primary")
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _create_network_tab(self) -> QWidget:
        """Create network printer configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Network settings group
        network_group = QGroupBox("네트워크 설정")
        network_layout = QFormLayout(network_group)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("예: 192.168.1.100")
        network_layout.addRow("IP 주소:", self.ip_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(9100)
        network_layout.addRow("포트:", self.port_input)

        layout.addWidget(network_group)

        # ZPL settings group
        zpl_group = QGroupBox("ZPL 설정")
        zpl_layout = QVBoxLayout(zpl_group)

        barcode_type_layout = QHBoxLayout()
        barcode_type_layout.addWidget(QLabel("바코드 형식:"))

        self.barcode_type_combo = QComboBox()
        self.barcode_type_combo.addItems(["Code128", "QR Code"])
        barcode_type_layout.addWidget(self.barcode_type_combo)
        barcode_type_layout.addStretch()

        zpl_layout.addLayout(barcode_type_layout)

        # Custom ZPL template
        zpl_layout.addWidget(QLabel("커스텀 ZPL 템플릿:"))
        self.zpl_template_input = QTextEdit()
        self.zpl_template_input.setPlaceholderText(
            "커스텀 ZPL 명령을 입력하세요.\n"
            "변수: {SERIAL}, {LOT}\n\n"
            "예:\n"
            "^XA\n"
            "^FO50,50^A0N,40^FD{SERIAL}^FS\n"
            "^FO50,120^BY2^BCN,80,Y^FD{SERIAL}^FS\n"
            "^XZ"
        )
        self.zpl_template_input.setMaximumHeight(150)
        zpl_layout.addWidget(self.zpl_template_input)

        layout.addWidget(zpl_group)
        layout.addStretch()

        return widget

    def _create_usb_tab(self) -> QWidget:
        """Create USB printer configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # USB printer selection
        usb_group = QGroupBox("USB 프린터 선택")
        usb_layout = QVBoxLayout(usb_group)

        # Printer queue selection
        queue_layout = QHBoxLayout()
        queue_layout.addWidget(QLabel("프린터:"))

        self.printer_queue_combo = QComboBox()
        queue_layout.addWidget(self.printer_queue_combo, 1)

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.clicked.connect(self._refresh_printer_list)
        queue_layout.addWidget(refresh_btn)

        usb_layout.addLayout(queue_layout)

        # Status label
        self.usb_status_label = QLabel("프린터 목록을 불러오는 중...")
        self.usb_status_label.setProperty("variant", "caption")
        usb_layout.addWidget(self.usb_status_label)

        layout.addWidget(usb_group)

        # ZPL template path
        template_group = QGroupBox("ZPL 템플릿 파일")
        template_layout = QHBoxLayout(template_group)

        self.template_path_input = QLineEdit()
        self.template_path_input.setPlaceholderText("ZPL 템플릿 파일 경로 (선택 사항)")
        template_layout.addWidget(self.template_path_input)

        browse_btn = QPushButton("찾아보기")
        browse_btn.setProperty("variant", "secondary")
        browse_btn.clicked.connect(self._browse_template)
        template_layout.addWidget(browse_btn)

        layout.addWidget(template_group)

        layout.addStretch()

        # Refresh printer list on tab open
        self._refresh_printer_list()

        return widget

    def _create_preview_tab(self) -> QWidget:
        """Create barcode preview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Test data input
        test_group = QGroupBox("테스트 데이터")
        test_layout = QFormLayout(test_group)

        self.test_serial_input = QLineEdit()
        self.test_serial_input.setPlaceholderText("KR01PSA2511001")
        self.test_serial_input.setText("KR01PSA2511001")
        test_layout.addRow("Serial 번호:", self.test_serial_input)

        self.test_lot_input = QLineEdit()
        self.test_lot_input.setPlaceholderText("WF-KR-251110D-001")
        self.test_lot_input.setText("WF-KR-251110D-001")
        test_layout.addRow("LOT 번호:", self.test_lot_input)

        generate_btn = QPushButton("바코드 생성")
        generate_btn.setProperty("variant", "primary")
        generate_btn.clicked.connect(self._generate_preview)
        test_layout.addRow("", generate_btn)

        layout.addWidget(test_group)

        # Preview area
        preview_group = QGroupBox("미리보기")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("바코드 생성 버튼을 클릭하세요")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet(
            f"border: 1px dashed {theme.get('colors.border.default', '#1a1a1a')}; "
            f"border-radius: 8px;"
        )
        preview_layout.addWidget(self.preview_label)

        # ZPL output
        self.zpl_output = QTextEdit()
        self.zpl_output.setReadOnly(True)
        self.zpl_output.setMaximumHeight(150)
        self.zpl_output.setPlaceholderText("생성된 ZPL 명령")
        preview_layout.addWidget(QLabel("ZPL 명령:"))
        preview_layout.addWidget(self.zpl_output)

        layout.addWidget(preview_group)

        return widget

    def load_settings(self):
        """Load current printer settings from config."""
        # Network printer settings (if stored)
        # For now, leave empty - user will input

        # USB printer queue
        saved_queue = self.config.printer_queue
        if saved_queue:
            index = self.printer_queue_combo.findText(saved_queue)
            if index >= 0:
                self.printer_queue_combo.setCurrentIndex(index)

        # ZPL template path
        template_path = self.config.zpl_template_path
        if template_path:
            self.template_path_input.setText(template_path)

    def _refresh_printer_list(self):
        """Refresh USB printer list."""
        self.printer_queue_combo.clear()
        self.usb_status_label.setText("프린터 목록을 불러오는 중...")

        if not self.print_service:
            self.usb_status_label.setText("USB 프린터 서비스를 사용할 수 없습니다")
            return

        printers = self.print_service.get_available_printers()

        if printers:
            self.printer_queue_combo.addItems(printers)
            self.usb_status_label.setText(f"{len(printers)}개 프린터 발견")
        else:
            self.usb_status_label.setText("프린터를 찾을 수 없습니다")

    def _browse_template(self):
        """Browse for ZPL template file."""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ZPL 템플릿 파일 선택",
            "",
            "ZPL Files (*.zpl);;Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            self.template_path_input.setText(file_path)

    @safe_slot("연결 테스트 실패")
    def _on_test_connection(self):
        """Test printer connection."""
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:  # Network printer
            ip = self.ip_input.text().strip()
            port = self.port_input.value()

            if not ip:
                Toast.warning(self, "IP 주소를 입력하세요")
                return

            self.network_printer.set_printer(ip, port)
            success, message = self.network_printer.test_connection()

            if success:
                Toast.success(self, message)
            else:
                Toast.danger(self, message)

        elif current_tab == 1:  # USB printer
            queue = self.printer_queue_combo.currentText()

            if not queue:
                Toast.warning(self, "프린터를 선택하세요")
                return

            if self.print_service:
                success = self.print_service.set_printer(queue)
                if success:
                    Toast.success(self, f"프린터 연결 성공: {queue}")
                else:
                    Toast.danger(self, "프린터 연결 실패")
            else:
                Toast.warning(self, "USB 프린터 서비스를 사용할 수 없습니다")

    @safe_slot("바코드 미리보기 생성 실패")
    def _generate_preview(self):
        """Generate barcode preview."""
        from utils.barcode_utils import BarcodeGenerator

        serial = self.test_serial_input.text().strip()

        if not serial:
            Toast.warning(self, "Serial 번호를 입력하세요")
            return

        # Get barcode type
        barcode_type = self.barcode_type_combo.currentText().lower()
        if "qr" in barcode_type:
            barcode_type = "qr"
        else:
            barcode_type = "code128"

        # Generate barcode image
        if barcode_type == "qr":
            image_bytes = BarcodeGenerator.generate_qr_image(serial, size=200)
        else:
            image_bytes = BarcodeGenerator.generate_code128_image(serial, width=300, height=100)

        if image_bytes:
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            self.preview_label.setPixmap(pixmap.scaled(
                400, 200,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.preview_label.setText("바코드 생성 실패")

        # Generate ZPL
        zpl = BarcodeGenerator.generate_zpl_label(serial, barcode_type, include_text=True)
        self.zpl_output.setPlainText(zpl)

        Toast.success(self, "바코드 미리보기 생성 완료")

    def _on_save(self):
        """Save printer configuration."""
        current_tab = self.tab_widget.currentIndex()

        config_data = {
            "printer_type": "network" if current_tab == 0 else "usb"
        }

        if current_tab == 0:  # Network printer
            ip = self.ip_input.text().strip()
            port = self.port_input.value()

            if not ip:
                Toast.warning(self, "IP 주소를 입력하세요")
                return

            config_data["ip_address"] = ip
            config_data["port"] = port
            config_data["barcode_type"] = self.barcode_type_combo.currentText()
            config_data["custom_zpl"] = self.zpl_template_input.toPlainText()

        elif current_tab == 1:  # USB printer
            queue = self.printer_queue_combo.currentText()

            if not queue:
                Toast.warning(self, "프린터를 선택하세요")
                return

            config_data["printer_queue"] = queue
            config_data["template_path"] = self.template_path_input.text()

            # Save to config
            self.config.printer_queue = queue
            self.config.zpl_template_path = self.template_path_input.text()

        self.printer_configured.emit(config_data)
        Toast.success(self, "프린터 설정이 저장되었습니다")
        self.accept()
