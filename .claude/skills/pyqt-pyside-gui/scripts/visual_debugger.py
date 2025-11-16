"""
Visual GUI Debugger for PySide6/PyQt6

Interactive visual debugger with live preview and inspector.
Shows your app side-by-side with debug information.

Usage:
    from visual_debugger import launch_with_debugger
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Launch with visual debugger
    launch_with_debugger(window)
    
    sys.exit(app.exec())
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QTextEdit, QGroupBox,
    QCheckBox, QScrollArea, QFrame, QToolBar, QStatusBar, QTabWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QFont


class WidgetInspector(QWidget):
    """실시간 위젯 정보 표시"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 위젯 정보
        info_group = QGroupBox("Widget Info")
        info_layout = QVBoxLayout(info_group)
        
        self.name_label = QLabel("Name: -")
        self.type_label = QLabel("Type: -")
        self.size_label = QLabel("Size: -")
        self.pos_label = QLabel("Position: -")
        self.visible_label = QLabel("Visible: -")
        self.enabled_label = QLabel("Enabled: -")
        
        for label in [self.name_label, self.type_label, self.size_label, 
                     self.pos_label, self.visible_label, self.enabled_label]:
            label.setFont(QFont("Monospace", 10))
            info_layout.addWidget(label)
        
        layout.addWidget(info_group)
        
        # 레이아웃 정보
        layout_group = QGroupBox("Layout Info")
        layout_info_layout = QVBoxLayout(layout_group)
        
        self.layout_type_label = QLabel("Type: -")
        self.layout_margins_label = QLabel("Margins: -")
        self.layout_spacing_label = QLabel("Spacing: -")
        self.layout_count_label = QLabel("Items: -")
        
        for label in [self.layout_type_label, self.layout_margins_label,
                     self.layout_spacing_label, self.layout_count_label]:
            label.setFont(QFont("Monospace", 10))
            layout_info_layout.addWidget(label)
        
        layout.addWidget(layout_group)
        
        # 스타일 정보
        style_group = QGroupBox("Style")
        style_layout = QVBoxLayout(style_group)
        
        self.style_text = QTextEdit()
        self.style_text.setReadOnly(True)
        self.style_text.setMaximumHeight(150)
        self.style_text.setFont(QFont("Monospace", 9))
        style_layout.addWidget(self.style_text)
        
        layout.addWidget(style_group)
        layout.addStretch()
    
    def update_widget_info(self, widget):
        """위젯 정보 업데이트"""
        if widget is None:
            self.clear()
            return
        
        # 기본 정보
        self.name_label.setText(f"Name: {widget.objectName() or '(unnamed)'}")
        self.type_label.setText(f"Type: {widget.__class__.__name__}")
        self.size_label.setText(f"Size: {widget.width()} × {widget.height()}")
        self.pos_label.setText(f"Position: ({widget.x()}, {widget.y()})")
        self.visible_label.setText(f"Visible: {'Yes ✓' if widget.isVisible() else 'No ✗'}")
        self.enabled_label.setText(f"Enabled: {'Yes ✓' if widget.isEnabled() else 'No ✗'}")
        
        # 레이아웃 정보
        layout = widget.layout()
        if layout:
            self.layout_type_label.setText(f"Type: {layout.__class__.__name__}")
            margins = layout.contentsMargins()
            self.layout_margins_label.setText(
                f"Margins: L:{margins.left()} T:{margins.top()} "
                f"R:{margins.right()} B:{margins.bottom()}"
            )
            self.layout_spacing_label.setText(f"Spacing: {layout.spacing()}")
            self.layout_count_label.setText(f"Items: {layout.count()}")
        else:
            self.layout_type_label.setText("Type: None")
            self.layout_margins_label.setText("Margins: -")
            self.layout_spacing_label.setText("Spacing: -")
            self.layout_count_label.setText("Items: -")
        
        # 스타일 정보
        style = widget.styleSheet()
        if style:
            self.style_text.setPlainText(style)
        else:
            self.style_text.setPlainText("(no custom stylesheet)")
    
    def clear(self):
        """정보 초기화"""
        for label in [self.name_label, self.type_label, self.size_label,
                     self.pos_label, self.visible_label, self.enabled_label,
                     self.layout_type_label, self.layout_margins_label,
                     self.layout_spacing_label, self.layout_count_label]:
            label.setText(label.text().split(':')[0] + ": -")
        self.style_text.clear()


class WidgetTreeView(QTreeWidget):
    """위젯 트리 뷰"""
    
    widget_selected = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["Widget", "Size", "Status"])
        self.setColumnWidth(0, 200)
        self.target_window = None
        self.widget_to_item = {}
        
        self.itemClicked.connect(self.on_item_clicked)
    
    def build_tree(self, window):
        """위젯 트리 빌드"""
        self.clear()
        self.widget_to_item.clear()
        self.target_window = window
        
        root = QTreeWidgetItem(self)
        self._build_widget_tree(window, root)
        self.expandAll()
    
    def _build_widget_tree(self, widget, parent_item):
        """재귀적으로 위젯 트리 생성"""
        # 위젯 정보
        name = widget.objectName() or widget.__class__.__name__
        size = f"{widget.width()}×{widget.height()}"
        
        # 상태 표시
        if not widget.isVisible():
            status = "Hidden"
            color = QColor(255, 100, 100)
        elif widget.width() == 0 or widget.height() == 0:
            status = "Zero Size"
            color = QColor(255, 200, 100)
        else:
            status = "OK"
            color = QColor(100, 255, 100)
        
        # 아이템 생성
        item = QTreeWidgetItem(parent_item)
        item.setText(0, name)
        item.setText(1, size)
        item.setText(2, status)
        item.setBackground(2, color)
        item.setData(0, Qt.UserRole, widget)
        
        self.widget_to_item[id(widget)] = item
        
        # 자식 위젯
        for child in widget.findChildren(QWidget, options=Qt.FindDirectChildrenOnly):
            self._build_widget_tree(child, item)
    
    def on_item_clicked(self, item, column):
        """아이템 클릭 핸들러"""
        widget = item.data(0, Qt.UserRole)
        if widget:
            self.widget_selected.emit(widget)
    
    def refresh(self):
        """트리 새로고침"""
        if self.target_window:
            self.build_tree(self.target_window)


class VisualOverlay(QWidget):
    """앱 위에 오버레이되는 시각적 하이라이트"""
    
    def __init__(self, target_window):
        super().__init__(target_window)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(target_window.rect())
        
        self.highlighted_widget = None
        self.show_all_borders = False
        
        # 타겟 윈도우 크기 변경 추적
        target_window.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """윈도우 크기 변경 감지"""
        if event.type() == event.Resize:
            self.setGeometry(obj.rect())
        return super().eventFilter(obj, event)
    
    def set_highlighted_widget(self, widget):
        """하이라이트할 위젯 설정"""
        self.highlighted_widget = widget
        self.update()
    
    def set_show_all_borders(self, show):
        """모든 위젯 테두리 표시 여부"""
        self.show_all_borders = show
        self.update()
    
    def paintEvent(self, event):
        """오버레이 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.show_all_borders:
            # 모든 위젯 테두리 표시
            for widget in self.parent().findChildren(QWidget):
                if widget.isVisible():
                    self._draw_widget_border(painter, widget, QColor(255, 0, 0, 100), 1)
        
        if self.highlighted_widget and self.highlighted_widget.isVisible():
            # 선택된 위젯 강조 표시
            self._draw_widget_border(painter, self.highlighted_widget, 
                                    QColor(0, 255, 0), 3)
            self._draw_widget_info(painter, self.highlighted_widget)
    
    def _draw_widget_border(self, painter, widget, color, width):
        """위젯 테두리 그리기"""
        try:
            pos = widget.mapTo(self.parent(), widget.rect().topLeft())
            rect = QRect(pos, widget.size())
            painter.setPen(QPen(color, width))
            painter.drawRect(rect)
        except RuntimeError:
            pass
    
    def _draw_widget_info(self, painter, widget):
        """위젯 정보 텍스트 그리기"""
        try:
            pos = widget.mapTo(self.parent(), widget.rect().topLeft())
            rect = QRect(pos, widget.size())
            
            name = widget.objectName() or widget.__class__.__name__
            info = f"{name}\n{widget.width()}×{widget.height()}"
            
            painter.setFont(QFont("Monospace", 10, QFont.Bold))
            text_rect = painter.boundingRect(rect, Qt.AlignTop | Qt.AlignLeft, info)
            
            # 배경
            painter.fillRect(text_rect.adjusted(-4, -2, 4, 2), QColor(0, 0, 0, 200))
            
            # 텍스트
            painter.setPen(QPen(Qt.yellow))
            painter.drawText(rect, Qt.AlignTop | Qt.AlignLeft, info)
        except RuntimeError:
            pass


class IssueDetector(QWidget):
    """레이아웃 문제 자동 감지"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 헤더
        header = QLabel("Layout Issues")
        header.setFont(QFont("", 12, QFont.Bold))
        layout.addWidget(header)
        
        # 이슈 목록
        self.issue_text = QTextEdit()
        self.issue_text.setReadOnly(True)
        self.issue_text.setFont(QFont("Monospace", 9))
        layout.addWidget(self.issue_text)
        
        # 검사 버튼
        self.scan_btn = QPushButton("🔍 Scan for Issues")
        self.scan_btn.clicked.connect(self.scan_requested)
        layout.addWidget(self.scan_btn)
    
    def scan_requested(self):
        """검사 요청 시그널 (부모에서 처리)"""
        pass
    
    def display_issues(self, window):
        """문제 검사 및 표시"""
        issues = []
        
        # 1. 숨겨진 위젯
        for widget in window.findChildren(QWidget):
            if not widget.isVisible() and widget.parent():
                issues.append(f"⚠️  Hidden: {self._get_widget_path(widget)}")
        
        # 2. 크기가 0인 위젯
        for widget in window.findChildren(QWidget):
            if widget.isVisible() and (widget.width() == 0 or widget.height() == 0):
                issues.append(f"❌ Zero size: {self._get_widget_path(widget)}")
        
        # 3. 레이아웃 없이 여러 자식
        for widget in window.findChildren(QWidget):
            children = widget.findChildren(QWidget, options=Qt.FindDirectChildrenOnly)
            if len(children) > 1 and widget.layout() is None:
                issues.append(f"⚠️  No layout: {self._get_widget_path(widget)} "
                            f"({len(children)} children)")
        
        # 4. 너무 큰 마진/스페이싱
        for widget in window.findChildren(QWidget):
            layout = widget.layout()
            if layout:
                margins = layout.contentsMargins()
                if any(m > 50 for m in [margins.left(), margins.top(), 
                                       margins.right(), margins.bottom()]):
                    issues.append(f"⚠️  Large margins: {self._get_widget_path(widget)}")
                
                if layout.spacing() > 50:
                    issues.append(f"⚠️  Large spacing: {self._get_widget_path(widget)}")
        
        # 결과 표시
        if issues:
            self.issue_text.setPlainText("\n".join(issues))
        else:
            self.issue_text.setPlainText("✓ No issues found!")
    
    def _get_widget_path(self, widget):
        """위젯 경로 생성"""
        path = []
        current = widget
        while current:
            name = current.objectName() or current.__class__.__name__
            path.append(name)
            current = current.parent() if isinstance(current.parent(), QWidget) else None
        return " > ".join(reversed(path))


class VisualDebugger(QMainWindow):
    """비주얼 디버거 메인 윈도우"""
    
    def __init__(self, target_window):
        super().__init__()
        self.target_window = target_window
        self.overlay = VisualOverlay(target_window)
        
        self.setup_ui()
        self.setup_timer()
        
        # 초기 트리 빌드
        self.tree_view.build_tree(target_window)
    
    def setup_ui(self):
        """UI 설정"""
        self.setWindowTitle("Visual GUI Debugger")
        self.setGeometry(100, 100, 1200, 800)
        
        # 메인 스플리터
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # 왼쪽: 트리 뷰
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_header = QLabel("Widget Tree")
        left_header.setFont(QFont("", 12, QFont.Bold))
        left_layout.addWidget(left_header)
        
        self.tree_view = WidgetTreeView()
        self.tree_view.widget_selected.connect(self.on_widget_selected)
        left_layout.addWidget(self.tree_view)
        
        # 새로고침 버튼
        refresh_btn = QPushButton("🔄 Refresh Tree")
        refresh_btn.clicked.connect(self.tree_view.refresh)
        left_layout.addWidget(refresh_btn)
        
        main_splitter.addWidget(left_widget)
        
        # 오른쪽: 탭 위젯
        right_tabs = QTabWidget()
        
        # Inspector 탭
        self.inspector = WidgetInspector()
        right_tabs.addTab(self.inspector, "Inspector")
        
        # Issues 탭
        self.issue_detector = IssueDetector()
        self.issue_detector.scan_btn.clicked.connect(
            lambda: self.issue_detector.display_issues(self.target_window)
        )
        right_tabs.addTab(self.issue_detector, "Issues")
        
        main_splitter.addWidget(right_tabs)
        
        # 비율 설정
        main_splitter.setSizes([400, 800])
        
        # 툴바
        toolbar = self.addToolBar("Tools")
        
        self.show_borders_action = toolbar.addAction("🔲 Show All Borders")
        self.show_borders_action.setCheckable(True)
        self.show_borders_action.toggled.connect(self.on_show_borders_toggled)
        
        toolbar.addSeparator()
        
        toolbar.addAction("📸 Screenshot", self.take_screenshot)
        toolbar.addAction("💾 Save Report", self.save_report)
        
        # 상태바
        self.statusBar().showMessage("Ready")
    
    def setup_timer(self):
        """자동 새로고침 타이머"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh)
        self.timer.start(1000)  # 1초마다
    
    def auto_refresh(self):
        """자동 새로고침"""
        if self.overlay.highlighted_widget:
            self.overlay.update()
    
    def on_widget_selected(self, widget):
        """위젯 선택 시"""
        self.inspector.update_widget_info(widget)
        self.overlay.set_highlighted_widget(widget)
        self.statusBar().showMessage(
            f"Selected: {widget.objectName() or widget.__class__.__name__}"
        )
    
    def on_show_borders_toggled(self, checked):
        """모든 테두리 표시 토글"""
        self.overlay.set_show_all_borders(checked)
    
    def take_screenshot(self):
        """스크린샷 저장"""
        pixmap = self.target_window.grab()
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pixmap.save(filename)
        self.statusBar().showMessage(f"Saved: {filename}", 3000)
    
    def save_report(self):
        """디버그 리포트 저장"""
        self.issue_detector.display_issues(self.target_window)
        self.statusBar().showMessage("Report generated", 3000)
    
    def closeEvent(self, event):
        """종료 시 오버레이 제거"""
        self.overlay.close()
        event.accept()


def launch_with_debugger(target_window):
    """디버거와 함께 앱 실행"""
    debugger = VisualDebugger(target_window)
    debugger.show()
    target_window.show()
    return debugger


# 사용 예제
if __name__ == "__main__":
    from PySide6.QtWidgets import QPushButton, QLineEdit
    
    # 테스트 앱
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Test App")
            self.setGeometry(200, 200, 600, 400)
            
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            
            layout.addWidget(QLabel("Test Label"))
            layout.addWidget(QLineEdit("Test Input"))
            layout.addWidget(QPushButton("Test Button"))
            
            # 문제있는 위젯 (테스트용)
            hidden_widget = QLabel("Hidden")
            hidden_widget.setVisible(False)
            layout.addWidget(hidden_widget)
    
    app = QApplication(sys.argv)
    window = TestWindow()
    debugger = launch_with_debugger(window)
    sys.exit(app.exec())
