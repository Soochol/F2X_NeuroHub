"""F2X NeuroHub MES - Reusable UI Components

재사용 가능한 UI 컴포넌트:
- Button: 버튼 (primary, success, danger, outline 변형)
- Label: 라벨 (title, heading, normal, small 변형)
- Card: 카드 컨테이너
- StatCard: 통계 카드 (숫자 + 라벨 + 색상 테두리)
- SidebarButton: 사이드바 네비게이션 버튼
"""

from typing import Optional
from PySide6.QtWidgets import (
    QPushButton, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .theme_loader import get_current_theme, ThemeLoader


class BaseComponent:
    """기본 컴포넌트 클래스 (지연 생성 패턴)"""

    def __init__(self):
        self._widget: Optional[QWidget] = None

    def get_widget(self) -> QWidget:
        """위젯 반환 (아직 생성되지 않았으면 생성)"""
        if self._widget is None:
            self._widget = self.create()
        return self._widget

    def create(self) -> QWidget:
        """서브클래스에서 구현: 위젯 생성"""
        raise NotImplementedError("Subclasses must implement create()")


class Button(BaseComponent):
    """버튼 컴포넌트

    Args:
        text: 버튼 텍스트
        variant: 변형 (default, primary, success, danger, outline)
        on_click: 클릭 콜백 함수
    """

    def __init__(
        self,
        text: str,
        variant: str = "default",
        on_click: Optional[callable] = None
    ):
        super().__init__()
        self.text = text
        self.variant = variant
        self.on_click = on_click

    def create(self) -> QPushButton:
        """버튼 위젯 생성"""
        button = QPushButton(self.text)
        button.setObjectName(f"btn_{self.variant}")

        # 테마에서 스타일 가져오기
        theme = get_current_theme()
        if theme:
            styles = ThemeLoader.get_component_style_dict("button", self.variant, theme)

            # QSS 생성
            qss_parts = [f"QPushButton#btn_{self.variant} {{"]

            if "background" in styles:
                qss_parts.append(f"    background-color: {styles['background']};")
            if "color" in styles:
                qss_parts.append(f"    color: {styles['color']};")
            if "border" in styles:
                qss_parts.append(f"    border: {styles['border']};")
            if "borderRadius" in styles:
                qss_parts.append(f"    border-radius: {styles['borderRadius']}px;")
            if "padding" in styles:
                qss_parts.append(f"    padding: {styles['padding']};")
            if "fontSize" in styles:
                qss_parts.append(f"    font-size: {styles['fontSize']}px;")
            if "fontWeight" in styles:
                qss_parts.append(f"    font-weight: {styles['fontWeight']};")

            qss_parts.append("}")

            # hover 스타일
            if "hoverBackground" in styles:
                qss_parts.append(f"QPushButton#btn_{self.variant}:hover {{")
                qss_parts.append(f"    background-color: {styles['hoverBackground']};")
                qss_parts.append("}")

            # pressed 스타일
            if "pressedBackground" in styles:
                qss_parts.append(f"QPushButton#btn_{self.variant}:pressed {{")
                qss_parts.append(f"    background-color: {styles['pressedBackground']};")
                qss_parts.append("}")

            button.setStyleSheet("\n".join(qss_parts))

        # 클릭 이벤트 연결
        if self.on_click:
            button.clicked.connect(self.on_click)

        return button


class Label(BaseComponent):
    """라벨 컴포넌트

    Args:
        text: 라벨 텍스트
        variant: 변형 (title, heading, normal, small)
    """

    def __init__(self, text: str, variant: str = "normal"):
        super().__init__()
        self.text = text
        self.variant = variant

    def create(self) -> QLabel:
        """라벨 위젯 생성"""
        label = QLabel(self.text)
        label.setObjectName(f"label_{self.variant}")

        # 테마에서 스타일 가져오기
        theme = get_current_theme()
        if theme:
            styles = ThemeLoader.get_component_style_dict("label", self.variant, theme)

            qss_parts = [f"QLabel#label_{self.variant} {{"]

            if "color" in styles:
                qss_parts.append(f"    color: {styles['color']};")
            if "fontSize" in styles:
                qss_parts.append(f"    font-size: {styles['fontSize']}px;")
            if "fontWeight" in styles:
                qss_parts.append(f"    font-weight: {styles['fontWeight']};")

            qss_parts.append("}")
            label.setStyleSheet("\n".join(qss_parts))

        return label


class Card(BaseComponent):
    """카드 컨테이너 컴포넌트

    Args:
        title: 카드 제목 (옵션)
        content_widget: 카드 내용 위젯 (옵션)
    """

    def __init__(
        self,
        title: Optional[str] = None,
        content_widget: Optional[QWidget] = None
    ):
        super().__init__()
        self.title = title
        self.content_widget = content_widget

    def create(self) -> QFrame:
        """카드 위젯 생성"""
        card = QFrame()
        card.setObjectName("card_default")

        # 테마에서 스타일 가져오기
        theme = get_current_theme()
        if theme:
            styles = ThemeLoader.get_component_style_dict("card", "default", theme)

            qss_parts = ["QFrame#card_default {"]

            if "background" in styles:
                qss_parts.append(f"    background-color: {styles['background']};")
            if "border" in styles:
                qss_parts.append(f"    border: {styles['border']};")
            if "borderRadius" in styles:
                qss_parts.append(f"    border-radius: {styles['borderRadius']}px;")
            if "padding" in styles:
                qss_parts.append(f"    padding: {styles['padding']};")

            qss_parts.append("}")
            card.setStyleSheet("\n".join(qss_parts))

        # 레이아웃 생성
        layout = QVBoxLayout(card)

        # 제목 추가
        if self.title:
            title_label = QLabel(self.title)
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            layout.addWidget(title_label)

        # 내용 위젯 추가
        if self.content_widget:
            layout.addWidget(self.content_widget)

        return card

    def set_content(self, widget: QWidget):
        """카드 내용 설정 (동적 변경)"""
        if self._widget:
            layout = self._widget.layout()
            if layout:
                # 기존 내용 제거 (제목 제외)
                start_index = 1 if self.title else 0
                for i in reversed(range(start_index, layout.count())):
                    item = layout.itemAt(i)
                    if item.widget():
                        item.widget().deleteLater()

                # 새 내용 추가
                layout.addWidget(widget)


class StatCard(BaseComponent):
    """통계 카드 컴포넌트

    숫자 + 라벨 + 색상 테두리로 구성

    Args:
        label_text: 라벨 텍스트 (예: "착공")
        value: 초기 값 (예: "0")
        variant: 변형 (default, success, completed, danger, inProgress)
    """

    def __init__(
        self,
        label_text: str,
        value: str = "0",
        variant: str = "default"
    ):
        super().__init__()
        self.label_text = label_text
        self.value = value
        self.variant = variant
        self.value_label: Optional[QLabel] = None

    def create(self) -> QFrame:
        """통계 카드 위젯 생성"""
        card = QFrame()
        card.setObjectName(f"stat_card_{self.variant}")

        # 테마에서 스타일 가져오기
        theme = get_current_theme()
        if theme:
            styles = ThemeLoader.get_component_style_dict("statCard", self.variant, theme)

            qss_parts = [f"QFrame#stat_card_{self.variant} {{"]

            if "background" in styles:
                qss_parts.append(f"    background-color: {styles['background']};")
            if "border" in styles:
                qss_parts.append(f"    border: {styles['border']};")
            if "borderLeft" in styles:
                qss_parts.append(f"    border-left: {styles['borderLeft']};")
            if "borderRadius" in styles:
                qss_parts.append(f"    border-radius: {styles['borderRadius']}px;")
            if "padding" in styles:
                qss_parts.append(f"    padding: {styles['padding']};")
            if "minHeight" in styles:
                qss_parts.append(f"    min-height: {styles['minHeight']}px;")

            qss_parts.append("}")
            card.setStyleSheet("\n".join(qss_parts))

        # 레이아웃 생성
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        # 라벨
        label = QLabel(self.label_text)
        label.setAlignment(Qt.AlignCenter)
        label_font = QFont()
        label_font.setPointSize(12)
        label.setFont(label_font)
        layout.addWidget(label)

        # 값 (큰 숫자)
        self.value_label = QLabel(self.value)
        self.value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setBold(True)
        self.value_label.setFont(value_font)

        # 변형에 따른 색상 적용
        if theme:
            color_map = {
                'success': theme.get('colors.success.main', '#2e7d32'),
                'completed': theme.get('colors.completed.main', '#f57c00'),
                'danger': theme.get('colors.danger.main', '#d32f2f'),
                'inProgress': theme.get('colors.inProgress.main', '#0288d1'),
                'default': theme.get('colors.text.primary', '#212121')
            }
            color = color_map.get(self.variant, '#212121')
            self.value_label.setStyleSheet(f"color: {color};")

        layout.addWidget(self.value_label)

        return card

    def set_value(self, value: str):
        """값 업데이트"""
        if self.value_label:
            self.value_label.setText(str(value))


class SidebarButton(BaseComponent):
    """사이드바 네비게이션 버튼 컴포넌트

    Args:
        text: 버튼 텍스트
        icon: 아이콘 텍스트 (예: "📊")
        is_active: 활성 상태 여부
    """

    clicked = Signal()

    def __init__(
        self,
        text: str,
        icon: str = "",
        is_active: bool = False
    ):
        super().__init__()
        self.text = text
        self.icon = icon
        self.is_active = is_active
        self._button: Optional[QPushButton] = None

    def create(self) -> QPushButton:
        """사이드바 버튼 위젯 생성"""
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        self._button = QPushButton(display_text)
        self._button.setCursor(Qt.PointingHandCursor)

        # 초기 스타일 적용
        self._apply_style()

        # 클릭 이벤트
        self._button.clicked.connect(self.clicked.emit)

        return self._button

    def _apply_style(self):
        """스타일 적용"""
        if not self._button:
            return

        variant = "active" if self.is_active else "default"
        self._button.setObjectName(f"sidebar_btn_{variant}")

        # 테마에서 스타일 가져오기
        theme = get_current_theme()
        if theme:
            styles = ThemeLoader.get_component_style_dict("sidebarButton", variant, theme)

            qss_parts = [f"QPushButton#sidebar_btn_{variant} {{"]

            if "background" in styles:
                qss_parts.append(f"    background-color: {styles['background']};")
            if "color" in styles:
                qss_parts.append(f"    color: {styles['color']};")
            if "border" in styles:
                qss_parts.append(f"    border: {styles['border']};")
            if "borderRadius" in styles:
                qss_parts.append(f"    border-radius: {styles['borderRadius']}px;")
            if "padding" in styles:
                qss_parts.append(f"    padding: {styles['padding']};")
            if "fontSize" in styles:
                qss_parts.append(f"    font-size: {styles['fontSize']}px;")
            if "fontWeight" in styles:
                qss_parts.append(f"    font-weight: {styles['fontWeight']};")
            if "textAlign" in styles:
                qss_parts.append(f"    text-align: {styles['textAlign']};")

            qss_parts.append("}")

            # hover 스타일
            if "hoverBackground" in styles:
                qss_parts.append(f"QPushButton#sidebar_btn_{variant}:hover {{")
                qss_parts.append(f"    background-color: {styles['hoverBackground']};")
                qss_parts.append("}")

            self._button.setStyleSheet("\n".join(qss_parts))

    def set_active(self, is_active: bool):
        """활성 상태 변경"""
        self.is_active = is_active
        self._apply_style()


def create_horizontal_group(*widgets: QWidget, spacing: int = 8) -> QWidget:
    """
    수평 그룹 생성 유틸리티

    Args:
        *widgets: 추가할 위젯들
        spacing: 위젯 간 간격

    Returns:
        QWidget (수평 레이아웃)
    """
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setSpacing(spacing)
    layout.setContentsMargins(0, 0, 0, 0)

    for widget in widgets:
        layout.addWidget(widget)

    return container
