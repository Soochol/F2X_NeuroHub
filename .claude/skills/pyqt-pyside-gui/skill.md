---
name: pyqt-pyside-gui
description: PySide6 GUI 개발 가이드. 테마 시스템, 컴포넌트 라이브러리, QSS 스타일링, 스레딩 패턴 포함.
---

# PySide6 GUI Development

PySide6를 사용한 프로덕션 수준의 데스크톱 앱 개발 가이드입니다.

## 핵심 원칙

1. **JSON 테마 시스템**: 모든 색상/간격을 JSON에서 정의
2. **ThemeManager**: 테마 로드 및 QSS 자동 생성
3. **Property Variant**: `setProperty("variant", "primary")`로 스타일링
4. **컴포넌트 재사용**: 프로젝트별 테마 컴포넌트 구축

---

## Quick Start

### 1. 테마 로드 (필수)

```python
from utils.theme_manager import load_theme, get_theme

app = QApplication(sys.argv)
load_theme(app, "themes/default.json")  # 앱 생성 직후!

window = MainWindow()
window.show()
```

### 2. 테마 값 사용

```python
theme = get_theme()
primary = theme.get("colors.brand.primary")
spacing = theme.get("spacing.md", 12)
```

### 3. Property Variant 적용

```python
button = QPushButton("저장")
button.setProperty("variant", "primary")

label = QLabel("에러 메시지")
label.setProperty("status", "error")
```

---

## 프로젝트 구조

```
your_app/
├── main.py
├── themes/
│   └── default.json        # 테마 정의
├── utils/
│   └── theme_manager.py    # ThemeManager 클래스
├── widgets/
│   └── themed_components.py # 테마 컴포넌트
└── views/
    └── main_window.py
```

---

## JSON 테마 구조

```json
{
  "colors": {
    "brand": { "primary": "#3ECF8E", "secondary": "#1DB7B0" },
    "background": { "primary": "#FFFFFF", "secondary": "#F5F5F5" },
    "text": { "primary": "#171717", "secondary": "#737373" },
    "semantic": { "success": "#10B981", "error": "#EF4444" }
  },
  "typography": {
    "fontFamily": "Segoe UI",
    "sizes": { "sm": 12, "base": 14, "lg": 16, "xl": 20 }
  },
  "spacing": { "sm": 8, "md": 12, "lg": 16, "xl": 24 },
  "radius": { "sm": 4, "md": 8, "lg": 12 }
}
```

---

## 스타일링 패턴

### QSS Variant Selectors

```css
/* 기본 버튼 */
QPushButton {
    background-color: #F5F5F5;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 8px 16px;
}

/* Primary Variant */
QPushButton[variant="primary"] {
    background-color: #3ECF8E;
    color: white;
    border: none;
}

/* Status Labels */
QLabel[status="success"] { color: #10B981; }
QLabel[status="error"] { color: #EF4444; }
```

### 동적 스타일 변경

```python
# Property 변경 후 스타일 갱신
button.setProperty("variant", "danger")
button.style().unpolish(button)
button.style().polish(button)
```

---

## 스레딩

```python
class Worker(QThread):
    progress = Signal(int)
    result = Signal(object)

    def run(self):
        for i in range(100):
            time.sleep(0.1)
            self.progress.emit(i)
        self.result.emit(final_result)

# 사용
self.worker = Worker()
self.worker.progress.connect(self.update_progress)
self.worker.result.connect(self.handle_result)
self.worker.start()
```

---

## Best Practices

### 필수

- [ ] `QApplication` 생성 직후 `load_theme()` 호출
- [ ] 모든 색상은 테마 JSON에서만 정의
- [ ] Property variant로 스타일 변경
- [ ] QGroupBox 자손 스타일은 MainWindow에서 적용

### 금지

- [ ] 하드코딩 색상 (`#3498db` 직접 사용)
- [ ] 윈도우 생성 후 테마 로드
- [ ] 개별 위젯에 전체 스타일시트 적용

---

## 자주 하는 실수

### 1. 테마 로드 순서

```python
# ❌ Wrong
window = MainWindow()
load_theme(app, "theme.json")

# ✅ Correct
load_theme(app, "theme.json")
window = MainWindow()
```

### 2. Property 스타일 미적용

```python
# ❌ Property만 설정
button.setProperty("variant", "primary")

# ✅ 스타일 갱신 추가
button.setProperty("variant", "primary")
button.style().unpolish(button)
button.style().polish(button)
```

### 3. QGroupBox 내부 스타일

```python
# ❌ GroupBox 내부에서 setStyleSheet
class MyGroupBox(QGroupBox):
    def __init__(self):
        self.setStyleSheet("QPushButton { ... }")  # 작동 안함

# ✅ MainWindow/부모에서 적용
class MainWindow(QMainWindow):
    def __init__(self):
        # 전체 앱 스타일에서 정의
```

---

## AI 요청 가이드

### 좋은 요청

```python
"themes/default.json에서 colors.brand.primary를 #7C3AED로 변경해줘"

"QPushButton에 variant='success' 스타일 추가해줘:
- background: semantic.success 색상
- hover 시 10% 어둡게"

"FormField 컴포넌트 만들어줘:
- QLabel + QLineEdit
- required 시 라벨에 * 표시
- error 상태에서 border 빨간색"
```

### 나쁜 요청

```
"버튼을 파란색으로 만들어줘"  # 어떤 파란색? 테마 변수?
"폼이 이상해 보여"  # 무엇이 어떻게 이상한지?
"색상 수정해줘"  # 어느 파일? 어떤 색상?
```

---

## References

### 핵심 가이드

- **[qss_systematic_guide.md](references/qss_systematic_guide.md)** - 체계적 QSS 적용 (셀렉터, Best Practices)
- **[theme_manager_template.py](references/theme_manager_template.py)** - ThemeManager 전체 구현
- **[theme_template.json](references/theme_template.json)** - JSON 테마 템플릿

### 추가 참조

- **[json_theme_guide.md](references/json_theme_guide.md)** - JSON 테마 상세 가이드
- **[component_library_guide.md](references/component_library_guide.md)** - 컴포넌트 라이브러리 사용법
- **[advanced_patterns.md](references/advanced_patterns.md)** - 고급 패턴 (애니메이션, D&D, 설정)

---

## 기본 템플릿

```python
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
from utils.theme_manager import load_theme, get_theme


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setMinimumSize(800, 600)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        theme = get_theme()
        spacing = theme.get("spacing.lg", 16)

        layout = QVBoxLayout(central)
        layout.setSpacing(spacing)
        layout.setContentsMargins(spacing, spacing, spacing, spacing)

        # 헤더
        header = QLabel("Welcome")
        header.setProperty("variant", "title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 버튼
        btn = QPushButton("시작하기")
        btn.setProperty("variant", "primary")
        btn.clicked.connect(self._on_start)
        layout.addWidget(btn)

        layout.addStretch()

    def _on_start(self):
        print("시작!")


def main():
    app = QApplication(sys.argv)
    load_theme(app, str(PROJECT_ROOT / "themes" / "default.json"))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## 표준 Imports

```python
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QCheckBox, QRadioButton,
    QGroupBox, QTabWidget, QScrollArea, QStackedWidget,
    QTableWidget, QListWidget, QTreeWidget,
    QMessageBox, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap
```
