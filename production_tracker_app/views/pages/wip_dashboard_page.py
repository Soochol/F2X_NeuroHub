"""
WIP Dashboard Page for Production Tracker App.

Displays WIP statistics with charts and real-time updates.
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QListWidget, QListWidgetItem, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter

from utils.theme_manager import get_theme
from widgets.toast_notification import Toast
from utils.exception_handler import safe_slot

# Try to import QtCharts (optional)
try:
    from PySide6.QtCharts import (
        QChart, QChartView, QBarSeries, QBarSet,
        QBarCategoryAxis, QValueAxis
    )
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    logging.warning("PySide6-QtCharts not installed. Chart features disabled.")

logger = logging.getLogger(__name__)
theme = get_theme()


class WIPDashboardPage(QWidget):
    """WIP Dashboard page with statistics and charts."""

    def __init__(self, viewmodel, config):
        """
        Initialize WIPDashboardPage.

        Args:
            viewmodel: WIPDashboardViewModel instance
            config: AppConfig instance
        """
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config

        self.setup_ui()
        self.connect_signals()

        # Start auto-refresh
        self.viewmodel.start_auto_refresh()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        spacing = theme.get("spacing.lg", 16)
        layout.setSpacing(spacing)
        layout.setContentsMargins(spacing, spacing, spacing, spacing)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("WIP 현황 대시보드")
        title.setProperty("variant", "page_title")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Auto-refresh toggle
        self.auto_refresh_check = QCheckBox("자동 새로고침")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self._on_auto_refresh_toggled)
        header_layout.addWidget(self.auto_refresh_check)

        # Manual refresh button
        refresh_btn = QPushButton("새로고침")
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.clicked.connect(self._on_refresh_clicked)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Total WIP count
        self.total_label = QLabel("총 WIP: --")
        self.total_label.setProperty("variant", "stat_value")
        layout.addWidget(self.total_label)

        # Charts section (if available)
        if CHARTS_AVAILABLE:
            chart_group = QGroupBox("공정별 WIP 수량")
            chart_layout = QVBoxLayout(chart_group)

            # Create chart
            self.chart = QChart()
            self.chart.setTitle("공정별 WIP 분포")
            self.chart.setAnimationOptions(QChart.SeriesAnimations)

            self.chart_view = QChartView(self.chart)
            self.chart_view.setRenderHint(QPainter.Antialiasing)
            self.chart_view.setMinimumHeight(300)

            chart_layout.addWidget(self.chart_view)
            layout.addWidget(chart_group)
        else:
            # Fallback: Show notice
            notice = QLabel("차트를 표시하려면 PySide6-QtCharts를 설치하세요")
            notice.setProperty("variant", "help_text")
            layout.addWidget(notice)

        # Two-column layout for LOT progress and alerts
        bottom_layout = QHBoxLayout()

        # LOT progress section
        lot_group = QGroupBox("LOT별 진행률")
        lot_layout = QVBoxLayout(lot_group)

        self.lot_table = QTableWidget()
        self.lot_table.setColumnCount(4)
        self.lot_table.setHorizontalHeaderLabels([
            "LOT 번호", "총 수량", "완료", "진행률"
        ])

        header = self.lot_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.lot_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lot_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.lot_table.setAlternatingRowColors(True)

        lot_layout.addWidget(self.lot_table)
        bottom_layout.addWidget(lot_group)

        # Alerts section
        alert_group = QGroupBox("문제 WIP 알림")
        alert_layout = QVBoxLayout(alert_group)

        self.alert_list = QListWidget()
        alert_layout.addWidget(self.alert_list)
        bottom_layout.addWidget(alert_group)

        layout.addLayout(bottom_layout)

    def connect_signals(self):
        """Connect ViewModel signals."""
        self.viewmodel.statistics_updated.connect(self._on_statistics_updated)
        self.viewmodel.error_occurred.connect(self._on_error)

    @safe_slot("통계 업데이트 실패")
    def _on_statistics_updated(self, stats: dict):
        """Handle statistics updated."""
        logger.debug("Statistics updated")

        # Update total WIP
        total_wip = stats.get("total_wip", 0)
        self.total_label.setText(f"총 WIP: {total_wip}")

        # Update chart (if available)
        if CHARTS_AVAILABLE:
            self._update_chart(stats)

        # Update LOT progress table
        self._update_lot_table(stats)

        # Update alerts
        self._update_alerts(stats)

    def _update_chart(self, stats: dict):
        """Update bar chart with process WIP counts."""
        by_process = stats.get("by_process", {})

        if not by_process:
            return

        # Clear existing series
        self.chart.removeAllSeries()

        # Create bar set
        bar_set = QBarSet("WIP 수량")
        categories = []

        for process_name, count in by_process.items():
            bar_set.append(count)
            categories.append(process_name)

        # Create bar series
        series = QBarSeries()
        series.append(bar_set)

        # Add series to chart
        self.chart.addSeries(series)

        # Setup axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Find max value for Y axis
        max_value = max(by_process.values()) if by_process.values() else 10
        axis_y = QValueAxis()
        axis_y.setRange(0, max_value + 5)
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

    def _update_lot_table(self, stats: dict):
        """Update LOT progress table."""
        by_lot = stats.get("by_lot", [])

        # Clear table
        self.lot_table.setRowCount(0)

        # Populate table
        for lot_data in by_lot:
            row = self.lot_table.rowCount()
            self.lot_table.insertRow(row)

            # LOT 번호
            lot_number = lot_data.get("lot_number", "")
            self.lot_table.setItem(row, 0, QTableWidgetItem(lot_number))

            # 총 수량
            total = lot_data.get("total_quantity", 0)
            self.lot_table.setItem(row, 1, QTableWidgetItem(str(total)))

            # 완료
            completed = lot_data.get("completed_quantity", 0)
            self.lot_table.setItem(row, 2, QTableWidgetItem(str(completed)))

            # 진행률
            if total > 0:
                progress = int(completed / total * 100)
                progress_text = f"{progress}%"
            else:
                progress_text = "--"
            self.lot_table.setItem(row, 3, QTableWidgetItem(progress_text))

    def _update_alerts(self, stats: dict):
        """Update alert list."""
        alerts = stats.get("alerts", [])

        # Clear list
        self.alert_list.clear()

        if not alerts:
            item = QListWidgetItem("문제 없음")
            item.setForeground(
                theme.get_qt_color("colors.semantic.success", "#10B981")
            )
            self.alert_list.addItem(item)
            return

        # Add alerts
        for alert in alerts:
            wip_id = alert.get("wip_id", "")
            reason = alert.get("reason", "")
            text = f"{wip_id}: {reason}"

            item = QListWidgetItem(text)
            item.setForeground(
                theme.get_qt_color("colors.semantic.warning", "#F59E0B")
            )
            self.alert_list.addItem(item)

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        self.viewmodel.refresh_statistics()
        Toast.info(self, "새로고침 중...")

    def _on_auto_refresh_toggled(self, state: int):
        """Handle auto-refresh toggle."""
        if state == Qt.Checked:
            self.viewmodel.start_auto_refresh()
            Toast.info(self, "자동 새로고침 활성화")
        else:
            self.viewmodel.stop_auto_refresh()
            Toast.info(self, "자동 새로고침 비활성화")

    @safe_slot("에러 처리 실패")
    def _on_error(self, error_msg: str):
        """Handle error."""
        logger.error(f"Error: {error_msg}")
        Toast.danger(self, f"오류: {error_msg}")

    def cleanup(self):
        """Clean up resources."""
        self.viewmodel.cleanup()
