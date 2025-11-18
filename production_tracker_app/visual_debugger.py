"""
Visual Debugger for Production Tracker App.

Based on skill.md best practices - Interactive widget inspector and analyzer.

Features:
- Widget tree with real-time status
- Inspector panel with detailed widget information
- Visual overlay highlighting selected widgets
- Automatic issue detection
- Export screenshots and reports

Usage:
    from visual_debugger import launch_with_debugger

    app = QApplication(sys.argv)
    window = MainWindow()
    debugger = launch_with_debugger(window)
    sys.exit(app.exec())
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
    QCheckBox, QPushButton, QSplitter, QTabWidget
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen
import logging

logger = logging.getLogger(__name__)


class WidgetOverlay(QWidget):
    """Transparent overlay to highlight selected widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.highlighted_widget = None

    def highlight_widget(self, widget):
        """Highlight a specific widget."""
        self.highlighted_widget = widget
        if widget:
            # Position overlay over target window
            target_window = widget.window()
            self.setGeometry(target_window.geometry())
        self.update()

    def paintEvent(self, event):
        """Draw highlight rectangle around selected widget."""
        if not self.highlighted_widget:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget geometry relative to overlay
        target_window = self.highlighted_widget.window()
        widget_rect = self.highlighted_widget.rect()
        global_pos = self.highlighted_widget.mapToGlobal(widget_rect.topLeft())
        local_pos = self.mapFromGlobal(global_pos)
        rect = QRect(local_pos, widget_rect.size())

        # Draw highlight
        pen = QPen(QColor(62, 207, 142), 3, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(rect)

        # Draw fill
        fill_color = QColor(62, 207, 142, 30)
        painter.fillRect(rect, fill_color)


class VisualDebugger(QMainWindow):
    """Visual debugger main window."""

    def __init__(self, target_window):
        super().__init__()
        self.target_window = target_window
        self.overlay = WidgetOverlay()

        self.setWindowTitle("🔍 Visual Debugger - Production Tracker")
        self.setGeometry(100, 100, 900, 700)
        self.setup_ui()
        self.load_widget_tree()

    def setup_ui(self):
        """Setup debugger UI."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left: Widget Tree
        left_panel = self.create_tree_panel()
        splitter.addWidget(left_panel)

        # Right: Inspector Tabs
        right_panel = self.create_inspector_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([400, 500])
        layout.addWidget(splitter)

        # Bottom toolbar
        toolbar = self.create_toolbar()
        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        main_layout.addWidget(toolbar)
        central.setLayout(main_layout)

    def create_tree_panel(self):
        """Create widget tree panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        title = QLabel("📂 Widget Tree")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Widget", "Type", "Visible"])
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        layout.addWidget(self.tree_widget)

        return panel

    def create_inspector_panel(self):
        """Create inspector tabs panel."""
        tabs = QTabWidget()

        # Properties tab
        self.properties_text = QTextEdit()
        self.properties_text.setReadOnly(True)
        self.properties_text.setStyleSheet("font-family: 'Courier New'; font-size: 12px;")
        tabs.addTab(self.properties_text, "🔧 Properties")

        # Style tab
        self.style_text = QTextEdit()
        self.style_text.setReadOnly(True)
        self.style_text.setStyleSheet("font-family: 'Courier New'; font-size: 12px;")
        tabs.addTab(self.style_text, "🎨 Stylesheet")

        # Issues tab
        self.issues_text = QTextEdit()
        self.issues_text.setReadOnly(True)
        self.issues_text.setStyleSheet("font-family: 'Courier New'; font-size: 12px;")
        tabs.addTab(self.issues_text, "⚠️ Issues")

        return tabs

    def create_toolbar(self):
        """Create bottom toolbar."""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)

        self.show_borders_checkbox = QCheckBox("Show All Borders")
        self.show_borders_checkbox.toggled.connect(self.toggle_show_borders)
        layout.addWidget(self.show_borders_checkbox)

        layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_widget_tree)
        layout.addWidget(refresh_btn)

        export_btn = QPushButton("📸 Export Report")
        export_btn.clicked.connect(self.export_report)
        layout.addWidget(export_btn)

        return toolbar

    def load_widget_tree(self):
        """Load widget tree from target window."""
        self.tree_widget.clear()
        self.add_widget_to_tree(self.target_window, None)
        self.tree_widget.expandAll()

    def add_widget_to_tree(self, widget, parent_item):
        """Recursively add widgets to tree."""
        widget_name = widget.objectName() or "<unnamed>"
        widget_type = widget.__class__.__name__
        visible = "✓" if widget.isVisible() else "✗"

        if parent_item:
            item = QTreeWidgetItem(parent_item, [widget_name, widget_type, visible])
        else:
            item = QTreeWidgetItem(self.tree_widget, [widget_name, widget_type, visible])

        item.setData(0, Qt.UserRole, widget)

        # Add children
        for child in widget.children():
            if isinstance(child, QWidget):
                self.add_widget_to_tree(child, item)

    def on_tree_item_clicked(self, item, column):
        """Handle tree item click."""
        widget = item.data(0, Qt.UserRole)
        if not widget:
            return

        # Highlight widget
        self.overlay.highlight_widget(widget)
        self.overlay.show()

        # Update inspector
        self.show_widget_properties(widget)
        self.show_widget_stylesheet(widget)
        self.detect_widget_issues(widget)

    def show_widget_properties(self, widget):
        """Display widget properties."""
        props = []
        props.append(f"Widget: {widget.__class__.__name__}")
        props.append(f"Object Name: {widget.objectName() or '<unnamed>'}")
        props.append(f"Visible: {widget.isVisible()}")
        props.append(f"Enabled: {widget.isEnabled()}")
        props.append(f"Geometry: {widget.geometry()}")
        props.append(f"Size: {widget.size().width()}x{widget.size().height()}")
        props.append(f"Position: ({widget.x()}, {widget.y()})")
        props.append(f"Parent: {widget.parent().__class__.__name__ if widget.parent() else 'None'}")

        # Text content if applicable
        if hasattr(widget, 'text'):
            try:
                text = widget.text()
                props.append(f"Text: {text[:100]}")
            except:
                pass

        self.properties_text.setPlainText("\n".join(props))

    def show_widget_stylesheet(self, widget):
        """Display widget stylesheet."""
        stylesheet = widget.styleSheet() or "<No stylesheet>"
        self.style_text.setPlainText(stylesheet)

    def detect_widget_issues(self, widget):
        """Detect common widget issues."""
        issues = []

        # Check if widget is too small
        if widget.width() < 10 or widget.height() < 10:
            issues.append("⚠️ Widget size is very small (possibly hidden)")

        # Check if widget is invisible
        if not widget.isVisible():
            issues.append("⚠️ Widget is not visible")

        # Check if widget has no parent
        if not widget.parent() and widget != self.target_window:
            issues.append("⚠️ Widget has no parent (may cause memory leak)")

        # Check stylesheet
        if widget.styleSheet() and "background" not in widget.styleSheet():
            issues.append("ℹ️ Stylesheet doesn't specify background")

        if not issues:
            issues.append("✅ No issues detected")

        self.issues_text.setPlainText("\n".join(issues))

    def toggle_show_borders(self, checked):
        """Toggle border visibility for all widgets."""
        if checked:
            self.apply_debug_borders(self.target_window)
        else:
            self.remove_debug_borders(self.target_window)

    def apply_debug_borders(self, widget):
        """Apply debug borders to widget and children."""
        if not hasattr(widget, '_original_stylesheet'):
            widget._original_stylesheet = widget.styleSheet()

        new_style = widget.styleSheet() + "\nborder: 1px solid red;"
        widget.setStyleSheet(new_style)

        for child in widget.children():
            if isinstance(child, QWidget):
                self.apply_debug_borders(child)

    def remove_debug_borders(self, widget):
        """Remove debug borders from widget and children."""
        if hasattr(widget, '_original_stylesheet'):
            widget.setStyleSheet(widget._original_stylesheet)
            delattr(widget, '_original_stylesheet')

        for child in widget.children():
            if isinstance(child, QWidget):
                self.remove_debug_borders(child)

    def export_report(self):
        """Export debugger report."""
        logger.info("Export functionality not yet implemented")

    def closeEvent(self, event):
        """Clean up on close."""
        self.overlay.close()
        event.accept()


def launch_with_debugger(target_window):
    """
    Launch visual debugger for target window.

    Args:
        target_window: QMainWindow instance to debug

    Returns:
        VisualDebugger instance
    """
    debugger = VisualDebugger(target_window)
    debugger.show()
    logger.info("🔍 Visual Debugger launched")
    return debugger
