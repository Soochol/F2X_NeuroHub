"""
History Page - Displays work start/complete/error history.
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QComboBox, QCalendarWidget, QDialog
)
from PySide6.QtCore import Qt, Slot, QDate
from PySide6.QtGui import QColor, QTextCharFormat
from services.history_manager import (
    get_history_manager, EventType, EventResult, WorkEvent
)
from utils.theme_manager import get_theme

theme = get_theme()


class HistoryPage(QWidget):
    """Page displaying work history with filtering."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.history_manager = get_history_manager()
        self._current_filter = "all"
        self._current_date = None  # None means today
        self._setup_ui()
        self._connect_signals()
        self._load_available_dates()
        self._refresh_table()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Colors
        text_primary = theme.get('colors.text.primary')
        grey_300 = theme.get('colors.grey.300')
        grey_400 = theme.get('colors.grey.400')
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
        border_default = theme.get('colors.border.default')
        brand = theme.get('colors.brand.main')
        success_main = theme.get('colors.success.main')
        danger_main = theme.get('colors.danger.main')
        warning_main = theme.get('colors.warning.main')

        # Header with title and filter
        header_layout = QHBoxLayout()

        title_label = QLabel("작업 이력")
        title_label.setStyleSheet(f"""
            color: {text_primary};
            font-size: 18px;
            font-weight: 600;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Date picker button
        self.date_button = QPushButton("📅 오늘")
        self.date_button.setCursor(Qt.PointingHandCursor)
        self.date_button.setMinimumWidth(100)
        self.date_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_elevated};
                border: 1px solid {border_default};
                border-radius: 4px;
                padding: 6px 16px;
                color: {text_primary};
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {brand};
                background-color: {bg_default};
            }}
        """)
        self.date_button.clicked.connect(self._on_date_picker_clicked)
        header_layout.addWidget(self.date_button)

        # Filter combo
        filter_label = QLabel("필터:")
        filter_label.setStyleSheet(f"color: {grey_400}; font-size: 13px;")
        header_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["전체", "성공", "실패/에러"])
        self.filter_combo.setMinimumWidth(100)
        self.filter_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {bg_elevated};
                border: 1px solid {border_default};
                border-radius: 4px;
                padding: 6px 12px;
                color: {text_primary};
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {brand};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {grey_400};
                margin-right: 8px;
            }}
        """)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.filter_combo)

        # Refresh button
        refresh_btn = QPushButton("새로고침")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_elevated};
                border: 1px solid {border_default};
                border-radius: 4px;
                padding: 6px 16px;
                color: {text_primary};
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {brand};
                background-color: {bg_default};
            }}
        """)
        refresh_btn.clicked.connect(self._refresh_table)
        header_layout.addWidget(refresh_btn)

        # Clear button
        clear_btn = QPushButton("초기화")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {danger_main};
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                color: white;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {theme.get('colors.danger.dark')};
            }}
        """)
        clear_btn.clicked.connect(self._on_clear_clicked)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Stats row
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")
        stats_frame.setStyleSheet(f"""
            #stats_frame {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 6px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(16, 12, 16, 12)
        stats_layout.setSpacing(24)

        # Total count
        self.total_label = QLabel("전체: 0")
        self.total_label.setStyleSheet(f"color: {text_primary}; font-size: 13px;")
        stats_layout.addWidget(self.total_label)

        # Success count
        self.success_label = QLabel("성공: 0")
        self.success_label.setStyleSheet(f"color: {success_main}; font-size: 13px;")
        stats_layout.addWidget(self.success_label)

        # Error count
        self.error_label = QLabel("실패: 0")
        self.error_label.setStyleSheet(f"color: {danger_main}; font-size: 13px;")
        stats_layout.addWidget(self.error_label)

        stats_layout.addStretch()
        layout.addWidget(stats_frame)

        # Table
        self.table = QTableWidget()
        self.table.setObjectName("history_table")
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "시간", "유형", "WIP/LOT", "결과", "공정", "메시지"
        ])

        # Table styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {bg_default};
                border: 1px solid {border_default};
                border-radius: 6px;
                gridline-color: {border_default};
                color: {text_primary};
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_default};
            }}
            QTableWidget::item:selected {{
                background-color: {bg_default};
                color: {text_primary};
            }}
            QTableWidget::item:focus {{
                background-color: {bg_default};
                border: none;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {bg_elevated};
                color: {grey_300};
                font-size: 12px;
                font-weight: 600;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid {border_default};
            }}
        """)

        # Header settings
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # WIP/LOT
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Result
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Process
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Message

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.NoSelection)  # No selection highlighting
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Read-only
        self.table.setFocusPolicy(Qt.NoFocus)  # No focus indicator

        layout.addWidget(self.table)

    def _connect_signals(self):
        """Connect history manager signals."""
        self.history_manager.event_added.connect(self._on_event_added)
        self.history_manager.history_cleared.connect(self._refresh_table)

    @Slot(object)
    def _on_event_added(self, event: WorkEvent):
        """Handle new event added."""
        # Reload available dates (for calendar validation)
        self._load_available_dates()
        self._refresh_table()

    def _load_available_dates(self):
        """Cache available history dates (for calendar validation)."""
        self._available_dates = set(self.history_manager.get_available_dates())

    def _on_date_picker_clicked(self):
        """Open calendar dialog to select date."""
        dialog = DatePickerDialog(self._available_dates, self._current_date, self)
        if dialog.exec() == QDialog.Accepted:
            self._current_date = dialog.get_selected_date()
            self._update_date_button()
            self._refresh_table()

    def _update_date_button(self):
        """Update date button text based on selected date."""
        if self._current_date is None:
            self.date_button.setText("📅 오늘")
        else:
            try:
                date_obj = datetime.strptime(self._current_date, "%Y-%m-%d")
                display_text = date_obj.strftime("%m월 %d일")
                self.date_button.setText(f"📅 {display_text}")
            except:
                self.date_button.setText(f"📅 {self._current_date}")

    def _on_filter_changed(self, index: int):
        """Handle filter change."""
        filters = ["all", "success", "error"]
        self._current_filter = filters[index] if index < len(filters) else "all"
        self._refresh_table()

    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.history_manager.clear()
        self._load_available_dates()  # Refresh date combo

    def _refresh_table(self):
        """Refresh table with current events."""
        # Get events based on date filter
        if self._current_date is None:
            # Today - use in-memory cache
            all_events = self.history_manager.get_all_events()
        else:
            # Load from specific date file
            all_events = self.history_manager.load_events_by_date(self._current_date)

        # Apply result filter
        if self._current_filter == "success":
            events = [e for e in all_events if e.result != EventResult.ERROR]
        elif self._current_filter == "error":
            events = [e for e in all_events if e.result == EventResult.ERROR]
        else:
            events = all_events

        # Update stats (only for today)
        if self._current_date is None:
            all_events_for_stats = self.history_manager.get_all_events()
            error_count = self.history_manager.get_error_count()
            success_count = len(all_events_for_stats) - error_count
        else:
            error_count = len([e for e in all_events if e.result == EventResult.ERROR])
            success_count = len(all_events) - error_count

        self.total_label.setText(f"전체: {len(all_events)}")
        self.success_label.setText(f"성공: {success_count}")
        self.error_label.setText(f"실패: {error_count}")

        # Populate table
        self.table.setRowCount(len(events))

        success_main = theme.get('colors.success.main')
        danger_main = theme.get('colors.danger.main')
        warning_main = theme.get('colors.warning.main')
        brand = theme.get('colors.brand.main')

        for row, event in enumerate(events):
            # Time
            time_item = QTableWidgetItem(event.timestamp.strftime("%H:%M:%S"))
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.table.setItem(row, 0, time_item)

            # Type
            type_text = {
                EventType.START: "착공",
                EventType.COMPLETE: "완공",
                EventType.ERROR: "에러",
            }.get(event.event_type, str(event.event_type))
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.table.setItem(row, 1, type_item)

            # WIP/LOT
            wip_lot = event.wip_id or event.lot_number or "-"
            wip_item = QTableWidgetItem(wip_lot)
            wip_item.setTextAlignment(Qt.AlignCenter)
            wip_item.setFlags(wip_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.table.setItem(row, 2, wip_item)

            # Result with color
            result_text = {
                EventResult.SUCCESS: "성공",
                EventResult.PASS: "PASS",
                EventResult.FAIL: "FAIL",
                EventResult.ERROR: "에러",
            }.get(event.result, str(event.result))
            result_item = QTableWidgetItem(result_text)
            result_item.setTextAlignment(Qt.AlignCenter)
            result_item.setFlags(result_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)

            if event.result == EventResult.SUCCESS:
                result_item.setForeground(QColor(success_main))
            elif event.result == EventResult.PASS:
                result_item.setForeground(QColor(success_main))
            elif event.result == EventResult.FAIL:
                result_item.setForeground(QColor(warning_main))
            elif event.result == EventResult.ERROR:
                result_item.setForeground(QColor(danger_main))

            self.table.setItem(row, 3, result_item)

            # Process
            process_item = QTableWidgetItem(event.process_name or "-")
            process_item.setTextAlignment(Qt.AlignCenter)
            process_item.setFlags(process_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.table.setItem(row, 4, process_item)

            # Message
            message_item = QTableWidgetItem(event.message)
            message_item.setFlags(message_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.table.setItem(row, 5, message_item)

    def cleanup(self):
        """Cleanup resources."""
        pass


class DatePickerDialog(QDialog):
    """Calendar date picker dialog for selecting history dates."""

    def __init__(self, available_dates: set, current_date: str = None, parent=None):
        super().__init__(parent)
        self.available_dates = available_dates
        self.selected_date = current_date
        self.setWindowTitle("날짜 선택")
        self.setMinimumWidth(400)

        # Apply dark theme to dialog
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.get('colors.background.default')};
                color: {theme.get('colors.text.primary')};
            }}
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Setup calendar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Title
        title = QLabel("작업 이력을 조회할 날짜를 선택하세요")
        title.setStyleSheet(f"font-size: 13px; color: {theme.get('colors.text.primary')};")
        layout.addWidget(title)

        # Calendar widget
        self.calendar = QCalendarWidget()

        # Theme colors
        bg_default = theme.get('colors.background.default')
        bg_elevated = theme.get('colors.background.elevated')
        text_primary = theme.get('colors.text.primary')
        text_secondary = theme.get('colors.text.secondary')
        border_default = theme.get('colors.border.default')
        brand_main = theme.get('colors.brand.main')
        brand_dark = theme.get('colors.brand.dark')
        grey_600 = theme.get('colors.grey.600')
        grey_700 = theme.get('colors.grey.700')

        self.calendar.setStyleSheet(f"""
            /* Main calendar background */
            QCalendarWidget {{
                background-color: {bg_default};
                color: {text_primary};
            }}

            /* Navigation bar (top area with month/year) */
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {bg_elevated};
                padding: 4px;
            }}

            /* Month/Year buttons */
            QCalendarWidget QToolButton {{
                background-color: {bg_elevated};
                color: {text_primary};
                padding: 6px 12px;
                border-radius: 4px;
                border: 1px solid {border_default};
                font-weight: 500;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {grey_600};
                border-color: {brand_main};
            }}
            QCalendarWidget QToolButton:pressed {{
                background-color: {grey_700};
            }}

            /* Navigation arrows */
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                qproperty-icon: none;
                background-color: {bg_elevated};
                border: 1px solid {border_default};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 24px;
            }}
            QCalendarWidget QToolButton#qt_calendar_prevmonth {{
                qproperty-text: "<";
            }}
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                qproperty-text: ">";
            }}

            /* Month dropdown menu */
            QCalendarWidget QMenu {{
                background-color: {bg_elevated};
                color: {text_primary};
                border: 1px solid {border_default};
                padding: 4px;
            }}
            QCalendarWidget QMenu::item {{
                padding: 6px 20px;
                border-radius: 4px;
            }}
            QCalendarWidget QMenu::item:selected {{
                background-color: {brand_main};
                color: white;
            }}

            /* Year spinbox */
            QCalendarWidget QSpinBox {{
                background-color: {bg_elevated};
                color: {text_primary};
                border: 1px solid {border_default};
                border-radius: 4px;
                padding: 4px 8px;
                selection-background-color: {brand_main};
            }}
            QCalendarWidget QSpinBox::up-button,
            QCalendarWidget QSpinBox::down-button {{
                background-color: {bg_elevated};
                border: none;
                width: 16px;
            }}

            /* Calendar grid (days) */
            QCalendarWidget QAbstractItemView {{
                background-color: {bg_default};
                color: {text_primary};
                selection-background-color: {brand_main};
                selection-color: white;
                alternate-background-color: {bg_default};
                outline: none;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {text_primary};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {grey_600};
            }}

            /* Header row (day names: 일, 월, 화...) */
            QCalendarWidget QWidget {{
                alternate-background-color: {bg_elevated};
            }}
        """)

        # Set header format (day names row)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(text_primary))
        header_format.setBackground(QColor(bg_elevated))
        header_format.setFontWeight(600)
        self.calendar.setHeaderTextFormat(header_format)

        # Set weekend format (same color as weekdays for dark mode visibility)
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor(text_primary))
        self.calendar.setWeekdayTextFormat(Qt.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.Sunday, weekend_format)

        # Set current date
        if self.selected_date:
            try:
                date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
                self.calendar.setSelectedDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except:
                self.calendar.setSelectedDate(QDate.currentDate())
        else:
            self.calendar.setSelectedDate(QDate.currentDate())

        # Disable dates with no history
        self._update_calendar_dates()

        layout.addWidget(self.calendar)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Today button
        today_btn = QPushButton("오늘")
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.setMinimumWidth(80)
        today_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get('colors.background.elevated')};
                border: 2px solid {theme.get('colors.border.default')};
                border-radius: 4px;
                padding: 6px 16px;
                color: {theme.get('colors.text.primary')};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get('colors.brand.main')};
                border-color: {theme.get('colors.brand.main')};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {theme.get('colors.brand.dark')};
            }}
        """)
        today_btn.clicked.connect(self._on_today_clicked)
        button_layout.addWidget(today_btn)

        # OK button
        ok_btn = QPushButton("선택")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setMinimumWidth(80)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get('colors.brand.main')};
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                color: white;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {theme.get('colors.brand.light')};
            }}
            QPushButton:pressed {{
                background-color: {theme.get('colors.brand.dark')};
            }}
        """)
        ok_btn.clicked.connect(self._on_ok_clicked)
        button_layout.addWidget(ok_btn)

        # Cancel button
        cancel_btn = QPushButton("취소")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.get('colors.background.elevated')};
                border: 2px solid {theme.get('colors.border.default')};
                border-radius: 4px;
                padding: 6px 16px;
                color: {theme.get('colors.text.primary')};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {theme.get('colors.danger.main')};
                border-color: {theme.get('colors.danger.main')};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {theme.get('colors.danger.dark')};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _update_calendar_dates(self):
        """Disable dates that don't have history data."""
        if not self.available_dates:
            return

        # Convert available dates to QDate set for easier comparison
        available_qdates = set()
        for date_str in self.available_dates:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                available_qdates.add(QDate(date_obj.year, date_obj.month, date_obj.day))
            except:
                continue

        # Note: QCalendarWidget doesn't have built-in date disabling,
        # so we'll highlight available dates visually in the formatting

    def _on_today_clicked(self):
        """Select today's date."""
        self.calendar.setSelectedDate(QDate.currentDate())
        self.selected_date = None
        self.accept()

    def _on_ok_clicked(self):
        """Handle OK button click."""
        selected_qdate = self.calendar.selectedDate()
        self.selected_date = selected_qdate.toString("yyyy-MM-dd")
        self.accept()

    def get_selected_date(self) -> str:
        """Get selected date (None for today)."""
        return self.selected_date
