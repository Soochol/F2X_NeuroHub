# PySide6 GUI 개발 - Agent 요약

> Claude Agent를 위한 핵심 참조 문서

---

## 🎯 5가지 핵심 원칙

1. **JSON 테마 시스템** - 모든 색상/간격을 JSON에서만 정의
2. **ThemeManager 싱글톤** - 테마 로드 및 QSS 자동 생성
3. **Property Variant** - `setProperty("variant", "primary")`로 스타일링
4. **QApplication 직후 테마 로드** - 윈도우 생성 전에 반드시 로드
5. **컴포넌트 재사용** - 테마 기반 위젯 라이브러리 구축

---

## ⚡ Quick Start (3단계)

```python
# Step 1: QApplication 생성 직후 테마 로드
from utils.theme_manager import load_theme, get_theme
app = QApplication(sys.argv)
load_theme(app, "themes/default.json")

# Step 2: 테마 값 사용
theme = get_theme()
primary_color = theme.get("colors.brand.primary", "#007bff")

# Step 3: Property Variant 적용
button = QPushButton("확인")
button.setProperty("variant", "primary")
```

---

## ✅ Best Practices 체크리스트

### 필수 사항
- ✅ `QApplication` 생성 직후 `load_theme()` 호출
- ✅ 색상은 반드시 `theme.get("colors.xxx")` 사용
- ✅ 위젯에 `setObjectName()` 설정
- ✅ Docstrings 작성
- ✅ Property Variant로 스타일 적용

### 금지 사항
- ❌ 하드코딩 색상 (`#ffffff`, `rgb(255,255,255)`)
- ❌ 윈도우 생성 후 테마 로드
- ❌ 개별 위젯에 `setStyleSheet()` 직접 호출
- ❌ 의미없는 변수명 (`widget1`, `button2`)
- ❌ QGroupBox 내부에서 setStyleSheet

### 자주 하는 실수
1. **테마 로드 순서** - 반드시 윈도우 생성 전에 로드
2. **Property 설정 후 미갱신** - `style().unpolish(widget); style().polish(widget)` 필요
3. **점 표기법 오류** - 항상 default 값 제공: `theme.get("key", "default")`

---

## 📁 파일 레퍼런스 맵

| 질문/작업 | 참조 파일 |
|-----------|-----------|
| 새 테마 만들기 | `references/theme_template.json` |
| ThemeManager 구현 | `references/theme_manager_template.py` |
| QSS 셀렉터/Variant | `references/qss_systematic_guide.md` |
| 커스텀 위젯 만들기 | `references/advanced_patterns.md` |
| 컴포넌트 라이브러리 | `ui_components/components.py` |
| 코드 품질 검증 | `tools/gui_analyzer.py` |
| 멀티스레딩 | `examples/threaded_app.py` |
| 테이블 구현 | `examples/table_model.py` |
| 다이얼로그 | `examples/dialog_examples.py` |

---

## 🎨 JSON 테마 기본 구조

```json
{
  "colors": {
    "brand": {
      "primary": "#007bff",
      "secondary": "#6c757d",
      "accent": "#28a745"
    },
    "background": {
      "primary": "#ffffff",
      "secondary": "#f8f9fa",
      "tertiary": "#e9ecef"
    },
    "text": {
      "primary": "#212529",
      "secondary": "#6c757d",
      "disabled": "#adb5bd"
    },
    "semantic": {
      "success": "#28a745",
      "warning": "#ffc107",
      "error": "#dc3545",
      "info": "#17a2b8"
    }
  },
  "typography": {
    "fontFamily": "Segoe UI",
    "sizes": {
      "sm": "11px",
      "base": "13px",
      "lg": "15px",
      "xl": "18px"
    }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "radius": {
    "sm": "4px",
    "md": "8px",
    "lg": "12px"
  }
}
```

---

## 🔧 Property Variant 사용법

### QSS 정의 (전역)
```css
/* Primary 버튼 */
QPushButton[variant="primary"] {
    background-color: {colors.brand.primary};
    color: white;
    border: none;
    border-radius: {radius.md};
    padding: {spacing.sm} {spacing.md};
}

/* Secondary 버튼 */
QPushButton[variant="secondary"] {
    background-color: transparent;
    color: {colors.brand.primary};
    border: 1px solid {colors.brand.primary};
}

/* Danger 버튼 */
QPushButton[variant="danger"] {
    background-color: {colors.semantic.error};
    color: white;
}
```

### Python 적용
```python
# Variant 설정
button.setProperty("variant", "primary")

# 동적 변경 시 스타일 갱신 필요
button.setProperty("variant", "danger")
button.style().unpolish(button)
button.style().polish(button)
```

---

## 🛠️ 도구 사용법

### GUI Analyzer (정적 분석)
```bash
# 단일 파일 분석
python .claude/skills/pyqt-pyside-gui/tools/gui_analyzer.py path/to/file.py

# 출력: HTML 리포트 생성
# - 위젯 트리
# - 이슈 목록 (size, visibility, layout, naming)
# - Best Practices 체크리스트
```

### 디버깅 워크플로우
```
개발 중: Hot Reload (실시간 수정)
    ↓
디버깅: Visual Debugger (런타임 분석)
    ↓
검증: GUI Analyzer (정적 분석)
    ↓
배포
```

---

## 📋 기본 앱 템플릿

```python
"""PySide6 기본 애플리케이션 템플릿."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from utils.theme_manager import load_theme, get_theme


class MainWindow(QMainWindow):
    """메인 윈도우."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application")
        self.setMinimumSize(800, 600)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Add widgets here
        self._setup_ui(layout)

    def _setup_ui(self, layout):
        """UI 구성."""
        pass


def main():
    """애플리케이션 진입점."""
    app = QApplication(sys.argv)
    app.setApplicationName("MyApp")

    # 테마 로드 (윈도우 생성 전!)
    load_theme(app, "themes/default.json")

    # 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

---

## 🔍 자주 사용하는 Import

```python
# Qt Core
from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer, QSettings

# Qt Widgets
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QRadioButton, QSpinBox,
    QTableView, QListView, QTreeView,
    QMessageBox, QFileDialog,
    QStatusBar, QMenuBar, QToolBar,
    QGroupBox, QFrame, QScrollArea, QSplitter
)

# Qt GUI
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

# Theme
from utils.theme_manager import load_theme, get_theme
```

---

## 📊 위젯 타입별 스타일링

### Input 필드
```python
input_field = QLineEdit()
input_field.setPlaceholderText("입력하세요")
input_field.setProperty("variant", "default")  # or "error"
```

### Card 컨테이너
```python
card = QFrame()
card.setProperty("variant", "elevated")  # or "outlined"
card.setObjectName("card")
```

### Label 변형
```python
# Heading
label = QLabel("제목")
label.setProperty("variant", "heading")

# Caption
caption = QLabel("설명 텍스트")
caption.setProperty("variant", "caption")

# Error
error = QLabel("오류 메시지")
error.setProperty("variant", "error")
```

---

## 🚨 문제 해결

### 스타일이 적용되지 않음
1. 테마가 로드되었는지 확인
2. Property 이름 오타 확인
3. QSS에 해당 셀렉터가 정의되어 있는지 확인
4. `unpolish/polish` 호출 필요 여부 확인

### 위젯이 보이지 않음
1. `show()` 호출 여부
2. 레이아웃에 추가되었는지
3. 크기가 0이 아닌지 (`setMinimumSize`)
4. 부모 위젯 존재 여부

### 테마 값을 찾을 수 없음
```python
# 잘못된 예
color = theme.get("colors.brand.primary")  # KeyError 가능

# 올바른 예
color = theme.get("colors.brand.primary", "#007bff")  # 기본값 제공
```

---

> **전체 문서 참조:** `skill.md` (한국어 완전 가이드)