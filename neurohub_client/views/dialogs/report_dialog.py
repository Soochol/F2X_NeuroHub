"""
Report Dialog for generating and exporting production reports.
"""
import logging
from datetime import datetime
from typing import Any, Optional

from PySide6.QtCore import QDate, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget
)

from utils.exception_handler import safe_slot
from utils.export_utils import ExcelExporter, PDFExporter
from utils.report_generator import ReportData, ReportGenerator
from utils.theme_manager import get_theme
from widgets.toast_notification import Toast

logger = logging.getLogger(__name__)
theme = get_theme()


class ReportGenerationWorker(QThread):
    """Background worker for report generation."""

    progress = Signal(int, str)  # Progress percentage, message
    finished = Signal(object)    # ReportData
    error = Signal(str)          # Error message

    def __init__(
        self,
        report_generator: ReportGenerator,
        report_type: str,
        **kwargs: Any
    ) -> None:
        super().__init__()
        self.report_generator = report_generator
        self.report_type = report_type
        self.kwargs = kwargs

    def run(self) -> None:
        """Execute report generation."""
        try:
            self.progress.emit(10, "보고서 생성 중...")

            if self.report_type == "daily_production":
                report = self.report_generator.generate_daily_production_report(**self.kwargs)
            elif self.report_type == "lot_progress":
                report = self.report_generator.generate_lot_progress_report(**self.kwargs)
            elif self.report_type == "wip_status":
                report = self.report_generator.generate_wip_status_report(**self.kwargs)
            elif self.report_type == "process_performance":
                report = self.report_generator.generate_process_performance_report(**self.kwargs)
            elif self.report_type == "defect_analysis":
                report = self.report_generator.generate_defect_analysis_report(**self.kwargs)
            else:
                raise ValueError(f"Unknown report type: {self.report_type}")

            self.progress.emit(90, "보고서 처리 중...")
            self.progress.emit(100, "완료")
            self.finished.emit(report)

        except Exception as e:
            error_msg = f"보고서 생성 실패: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)


class ReportDialog(QDialog):
    """Report generation and export dialog."""

    # Signals
    report_generated = Signal(object)  # ReportData

    def __init__(
        self,
        api_client: Any,
        config: Any,
        parent: Optional[QWidget] = None
    ) -> None:
        """
        Initialize ReportDialog.

        Args:
            api_client: APIClient instance
            config: AppConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.api_client = api_client
        self.config = config
        self.report_generator = ReportGenerator(api_client)
        self.current_report: ReportData = None
        self.worker: ReportGenerationWorker = None

        self.setWindowTitle("보고서 생성")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI components."""
        layout = QVBoxLayout(self)
        spacing = theme.get("spacing.lg", 16)
        layout.setSpacing(spacing)

        # Header
        header = QLabel("생산 보고서 생성")
        header.setProperty("variant", "page_title")
        layout.addWidget(header)

        # Report type selection
        type_group = QGroupBox("보고서 종류")
        type_layout = QFormLayout(type_group)

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "일일 생산 보고서",
            "LOT 진행 보고서",
            "WIP 현황 보고서",
            "공정 성능 보고서",
            "불량 분석 보고서"
        ])
        self.report_type_combo.currentIndexChanged.connect(self._on_report_type_changed)
        type_layout.addRow("종류:", self.report_type_combo)

        layout.addWidget(type_group)

        # Options group (dynamic based on report type)
        self.options_group = QGroupBox("보고서 옵션")
        self.options_layout = QFormLayout(self.options_group)

        layout.addWidget(self.options_group)

        # Create option widgets
        self._create_option_widgets()
        self._on_report_type_changed(0)  # Initialize with first report type

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Preview area
        preview_group = QGroupBox("미리보기")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        self.preview_text.setPlaceholderText("보고서를 생성하면 요약이 여기에 표시됩니다")
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_group)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.generate_btn = QPushButton("보고서 생성")
        self.generate_btn.setProperty("variant", "primary")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        button_layout.addWidget(self.generate_btn)

        self.export_excel_btn = QPushButton("Excel 내보내기")
        self.export_excel_btn.setProperty("variant", "secondary")
        self.export_excel_btn.clicked.connect(self._on_export_excel_clicked)
        self.export_excel_btn.setEnabled(False)
        button_layout.addWidget(self.export_excel_btn)

        self.export_pdf_btn = QPushButton("PDF 내보내기")
        self.export_pdf_btn.setProperty("variant", "secondary")
        self.export_pdf_btn.clicked.connect(self._on_export_pdf_clicked)
        self.export_pdf_btn.setEnabled(False)
        button_layout.addWidget(self.export_pdf_btn)

        close_btn = QPushButton("닫기")
        close_btn.setProperty("variant", "secondary")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _create_option_widgets(self) -> None:
        """Create option widgets for all report types."""
        # Date widgets
        self.single_date = QDateEdit()
        self.single_date.setCalendarPopup(True)
        self.single_date.setDate(QDate.currentDate())

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        # Filter widgets
        self.line_combo = QComboBox()
        self.line_combo.addItem("전체")
        self._load_production_lines()

        self.process_combo = QComboBox()
        self.process_combo.addItem("전체")
        self._load_processes()

        self.status_combo = QComboBox()
        self.status_combo.addItems(["전체", "CREATED", "IN_PROGRESS", "COMPLETED"])

    def _load_production_lines(self) -> None:
        """Load production lines from API."""
        try:
            lines = self.api_client.get("/api/v1/production-lines/active")
            for line in lines:
                self.line_combo.addItem(
                    f"{line.get('line_code', '')} - {line.get('line_name', '')}",
                    userData=line.get("id")
                )
        except Exception as e:
            logger.warning(f"Failed to load production lines: {e}")

    def _load_processes(self) -> None:
        """Load processes from API."""
        try:
            processes = self.api_client.get("/api/v1/processes/active")
            for process in processes:
                process_name = process.get("process_name_ko", "")
                process_num = process.get("process_number", "")
                self.process_combo.addItem(
                    f"{process_num}. {process_name}",
                    userData=process.get("id")
                )
        except Exception as e:
            logger.warning(f"Failed to load processes: {e}")

    def _on_report_type_changed(self, index: int) -> None:
        """Handle report type selection change."""
        # Clear current options
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Add options based on report type
        if index == 0:  # Daily production
            self.options_layout.addRow("날짜:", self.single_date)
            self.options_layout.addRow("생산라인:", self.line_combo)
            self.options_layout.addRow("공정:", self.process_combo)

        elif index == 1:  # LOT progress
            date_row = QHBoxLayout()
            date_row.addWidget(self.start_date)
            date_row.addWidget(QLabel("~"))
            date_row.addWidget(self.end_date)
            self.options_layout.addRow("기간:", date_row)
            self.options_layout.addRow("상태:", self.status_combo)

        elif index == 2:  # WIP status
            self.options_layout.addRow("공정:", self.process_combo)
            self.options_layout.addRow("생산라인:", self.line_combo)

        elif index == 3:  # Process performance
            date_row = QHBoxLayout()
            date_row.addWidget(self.start_date)
            date_row.addWidget(QLabel("~"))
            date_row.addWidget(self.end_date)
            self.options_layout.addRow("기간:", date_row)
            self.options_layout.addRow("공정:", self.process_combo)

        elif index == 4:  # Defect analysis
            date_row = QHBoxLayout()
            date_row.addWidget(self.start_date)
            date_row.addWidget(QLabel("~"))
            date_row.addWidget(self.end_date)
            self.options_layout.addRow("기간:", date_row)
            self.options_layout.addRow("공정:", self.process_combo)

    @safe_slot("보고서 생성 실패")
    def _on_generate_clicked(self) -> None:
        """Handle generate button click."""
        if self.worker and self.worker.isRunning():
            Toast.warning(self, "보고서 생성 중입니다. 잠시만 기다려 주세요.")
            return

        # Get report parameters
        report_type_index = self.report_type_combo.currentIndex()
        kwargs = {}

        if report_type_index == 0:  # Daily production
            report_type = "daily_production"
            kwargs["date"] = self.single_date.date().toString("yyyy-MM-dd")
            if self.line_combo.currentIndex() > 0:
                kwargs["line_id"] = self.line_combo.currentData()
            if self.process_combo.currentIndex() > 0:
                kwargs["process_id"] = self.process_combo.currentData()

        elif report_type_index == 1:  # LOT progress
            report_type = "lot_progress"
            kwargs["start_date"] = self.start_date.date().toString("yyyy-MM-dd")
            kwargs["end_date"] = self.end_date.date().toString("yyyy-MM-dd")
            if self.status_combo.currentIndex() > 0:
                kwargs["status"] = self.status_combo.currentText()

        elif report_type_index == 2:  # WIP status
            report_type = "wip_status"
            if self.process_combo.currentIndex() > 0:
                kwargs["process_id"] = self.process_combo.currentData()
            if self.line_combo.currentIndex() > 0:
                kwargs["line_id"] = self.line_combo.currentData()

        elif report_type_index == 3:  # Process performance
            report_type = "process_performance"
            kwargs["start_date"] = self.start_date.date().toString("yyyy-MM-dd")
            kwargs["end_date"] = self.end_date.date().toString("yyyy-MM-dd")
            if self.process_combo.currentIndex() > 0:
                kwargs["process_id"] = self.process_combo.currentData()

        elif report_type_index == 4:  # Defect analysis
            report_type = "defect_analysis"
            kwargs["start_date"] = self.start_date.date().toString("yyyy-MM-dd")
            kwargs["end_date"] = self.end_date.date().toString("yyyy-MM-dd")
            if self.process_combo.currentIndex() > 0:
                kwargs["process_id"] = self.process_combo.currentData()

        else:
            Toast.warning(self, "보고서 종류를 선택하세요")
            return

        # Start worker
        self.worker = ReportGenerationWorker(self.report_generator, report_type, **kwargs)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_report_generated)
        self.worker.error.connect(self._on_error)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_btn.setEnabled(False)

        self.worker.start()

    def _on_progress(self, percentage: int, message: str) -> None:
        """Handle progress update."""
        self.progress_bar.setValue(percentage)
        logger.debug(f"Report generation: {percentage}% - {message}")

    @safe_slot("보고서 처리 실패")
    def _on_report_generated(self, report: ReportData) -> None:
        """Handle report generation completion."""
        self.current_report = report

        # Hide progress
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        # Enable export buttons
        self.export_excel_btn.setEnabled(True)
        self.export_pdf_btn.setEnabled(True)

        # Update preview
        self._update_preview(report)

        # Emit signal
        self.report_generated.emit(report)

        Toast.success(self, "보고서가 생성되었습니다")

    def _update_preview(self, report: ReportData) -> None:
        """Update preview with report summary."""
        summary = report.summary
        if not summary:
            self.preview_text.setPlainText("요약 정보가 없습니다")
            return

        # Format summary based on report type
        text = f"보고서 종류: {report.report_type}\n"
        text += f"생성 시간: {datetime.fromisoformat(report.generated_at).strftime('%Y-%m-%d %H:%M:%S')}\n"

        if report.date_range_start:
            text += f"기간: {report.date_range_start}"
            if report.date_range_end and report.date_range_end != report.date_range_start:
                text += f" ~ {report.date_range_end}"
            text += "\n"

        text += "\n=== 요약 ===\n"
        for key, value in summary.items():
            if isinstance(value, (int, float)):
                text += f"{key}: {value}\n"
            elif isinstance(value, dict):
                text += f"\n{key}:\n"
                for k, v in value.items():
                    text += f"  {k}: {v}\n"

        self.preview_text.setPlainText(text)

    def _on_error(self, error_msg: str) -> None:
        """Handle error."""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        Toast.danger(self, error_msg)

    @safe_slot("Excel 내보내기 실패")
    def _on_export_excel_clicked(self) -> None:
        """Handle Excel export button click."""
        if not self.current_report:
            Toast.warning(self, "먼저 보고서를 생성하세요")
            return

        from PySide6.QtWidgets import QFileDialog

        file_name = f"report_{self.current_report.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Excel 내보내기",
            file_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            try:
                self._export_to_excel(file_path)
                Toast.success(self, f"Excel로 내보냈습니다: {file_path}")
            except Exception as e:
                logger.error(f"Excel export failed: {e}")
                Toast.danger(self, f"Excel 내보내기 실패: {str(e)}")

    def _export_to_excel(self, file_path: str) -> None:
        """Export report to Excel file."""
        ExcelExporter.export_report(self.current_report, file_path)
        logger.info(f"Exported report to Excel: {file_path}")

    @safe_slot("PDF 내보내기 실패")
    def _on_export_pdf_clicked(self) -> None:
        """Handle PDF export button click."""
        if not self.current_report:
            Toast.warning(self, "먼저 보고서를 생성하세요")
            return

        from PySide6.QtWidgets import QFileDialog

        file_name = f"report_{self.current_report.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF 내보내기",
            file_name,
            "PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            try:
                self._export_to_pdf(file_path)
                Toast.success(self, f"PDF로 내보냈습니다: {file_path}")
            except Exception as e:
                logger.error(f"PDF export failed: {e}")
                Toast.danger(self, f"PDF 내보내기 실패: {str(e)}")

    def _export_to_pdf(self, file_path: str) -> None:
        """Export report to PDF file."""
        PDFExporter.export_report(self.current_report, file_path)
        logger.info(f"Exported report to PDF: {file_path}")
