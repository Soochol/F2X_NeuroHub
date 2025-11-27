"""
Measurement Panel Widget for displaying equipment measurement data.

Shows measurement items with values, specs, and pass/fail status.
"""
from typing import Any, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
)


class MeasurementItemWidget(QFrame):
    """Widget for displaying a single measurement item."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("measurementItem")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Left: Name and code
        left_layout = QVBoxLayout()
        left_layout.setSpacing(2)

        self.name_label = QLabel()
        self.name_label.setObjectName("measurementName")
        font = self.name_label.font()
        font.setPointSize(11)
        font.setBold(True)
        self.name_label.setFont(font)

        self.code_label = QLabel()
        self.code_label.setObjectName("measurementCode")
        self.code_label.setStyleSheet("color: #a8a8a8;")

        left_layout.addWidget(self.name_label)
        left_layout.addWidget(self.code_label)
        layout.addLayout(left_layout, 2)

        # Center: Value and unit
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value_label = QLabel()
        self.value_label.setObjectName("measurementValue")
        font = self.value_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        center_layout.addWidget(self.value_label)
        layout.addLayout(center_layout, 2)

        # Right: Spec range
        spec_layout = QVBoxLayout()
        spec_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.spec_label = QLabel()
        self.spec_label.setObjectName("measurementSpec")
        self.spec_label.setStyleSheet("color: #a8a8a8; font-size: 10px;")
        self.spec_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        spec_layout.addWidget(self.spec_label)
        layout.addLayout(spec_layout, 2)

        # Result indicator
        self.result_label = QLabel()
        self.result_label.setObjectName("measurementResult")
        self.result_label.setFixedWidth(60)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.result_label.font()
        font.setBold(True)
        self.result_label.setFont(font)
        layout.addWidget(self.result_label)

    def set_data(self, item: Any) -> None:
        """
        Set measurement item data.

        Args:
            item: MeasurementItem dataclass
        """
        self.name_label.setText(item.name)
        self.code_label.setText(item.code)

        # Format value with unit
        value_text = f"{item.value}"
        if item.unit:
            value_text += f" {item.unit}"
        self.value_label.setText(value_text)

        # Format spec
        if item.spec:
            spec_parts = []
            if item.spec.min is not None:
                spec_parts.append(f"Min: {item.spec.min}")
            if item.spec.target is not None:
                spec_parts.append(f"Target: {item.spec.target}")
            if item.spec.max is not None:
                spec_parts.append(f"Max: {item.spec.max}")
            self.spec_label.setText(" | ".join(spec_parts))
        else:
            self.spec_label.setText("")

        # Set result style
        if item.result == "PASS":
            self.result_label.setText("PASS")
            self.result_label.setStyleSheet(
                "background-color: #4CAF50; color: white; "
                "border-radius: 4px; padding: 4px 8px;"
            )
            self.value_label.setStyleSheet("color: #4CAF50;")
        else:
            self.result_label.setText("FAIL")
            self.result_label.setStyleSheet(
                "background-color: #F44336; color: white; "
                "border-radius: 4px; padding: 4px 8px;"
            )
            self.value_label.setStyleSheet("color: #F44336;")


class MeasurementPanel(QFrame):
    """
    Panel widget for displaying equipment measurement data.

    Shows overall result, list of measurements, and action buttons.
    """

    # Signals
    confirm_clicked = Signal()  # User confirmed completion
    cancel_clicked = Signal()   # User cancelled

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("measurementPanel")
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("측정 결과")
        title_label.setObjectName("panelTitle")
        font = title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.result_badge = QLabel()
        self.result_badge.setObjectName("resultBadge")
        self.result_badge.setFixedSize(80, 32)
        self.result_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.result_badge.font()
        font.setPointSize(12)
        font.setBold(True)
        self.result_badge.setFont(font)
        header_layout.addWidget(self.result_badge)

        layout.addLayout(header_layout)

        # Scroll area for measurements
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.items_container = QWidget()
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(8)

        scroll.setWidget(self.items_container)
        layout.addWidget(scroll, 1)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)

        self.confirm_btn = QPushButton("완공 확인")
        self.confirm_btn.setObjectName("confirmButton")
        self.confirm_btn.setFixedHeight(40)
        self.confirm_btn.clicked.connect(self.confirm_clicked.emit)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn, 1)

        layout.addLayout(button_layout)

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            #measurementPanel {
                background-color: #1f1f1f;
                border: 1px solid #1a1a1a;
                border-radius: 8px;
            }
            #measurementItem {
                background-color: #252525;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
            }
            #cancelButton {
                background-color: #1f1f1f;
                border: 1px solid #1a1a1a;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                color: #ededed;
            }
            #cancelButton:hover {
                background-color: #252525;
            }
            #confirmButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: bold;
            }
            #confirmButton:hover {
                background-color: #1976D2;
            }
            #confirmButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)

    def set_data(self, equipment_data: Any) -> None:
        """
        Set equipment measurement data to display.

        Args:
            equipment_data: EquipmentData object from TCP server
        """
        # Clear existing items
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Set overall result badge
        if equipment_data.result == "PASS":
            self.result_badge.setText("PASS")
            self.result_badge.setStyleSheet(
                "background-color: #4CAF50; color: white; "
                "border-radius: 6px; font-weight: bold;"
            )
            self.confirm_btn.setEnabled(True)
            self.confirm_btn.setText("완공 확인")
        else:
            self.result_badge.setText("FAIL")
            self.result_badge.setStyleSheet(
                "background-color: #F44336; color: white; "
                "border-radius: 6px; font-weight: bold;"
            )
            self.confirm_btn.setEnabled(True)
            self.confirm_btn.setText("불량 등록")

        # Add measurement items
        for item in equipment_data.measurements:
            item_widget = MeasurementItemWidget()
            item_widget.set_data(item)
            self.items_layout.addWidget(item_widget)

        # Add stretch at the end
        self.items_layout.addStretch()

    def clear(self) -> None:
        """Clear all measurement data."""
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.result_badge.setText("")
        self.result_badge.setStyleSheet("")
