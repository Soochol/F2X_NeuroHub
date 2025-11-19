# PySide6 QSS 체계적 적용 가이드

고품질 PySide6 GUI를 위한 체계적인 QSS(Qt Style Sheet) 적용 시스템 구축 가이드입니다.

## 목차

1. [핵심 원칙](#핵심-원칙)
2. [아키텍처 구조](#아키텍처-구조)
3. [테마 시스템 설계](#테마-시스템-설계)
4. [QSS 작성 규칙](#qss-작성-규칙)
5. [컴포넌트별 스타일링](#컴포넌트별-스타일링)
6. [Best Practices](#best-practices)
7. [트러블슈팅](#트러블슈팅)

---

## 핵심 원칙

### 1. 단일 진실 소스 (Single Source of Truth)

모든 디자인 토큰은 **JSON 테마 파일 하나**에서만 정의합니다.

```python
# ❌ Bad: 하드코딩
button.setStyleSheet("background-color: #3498db;")

# ✅ Good: 테마에서 참조
theme = get_theme()
color = theme.get("colors.brand.primary")
```

### 2. 변수 기반 디자인 시스템

색상, 간격, 폰트 등을 시맨틱 변수로 정의합니다.

```json
{
  "colors": {
    "brand": { "primary": "#3ECF8E" },
    "semantic": { "success": "#10B981", "error": "#EF4444" }
  },
  "spacing": { "sm": 8, "md": 12, "lg": 16 },
  "radius": { "sm": 4, "md": 8 }
}
```

### 3. 계층적 스타일 구조

```
Global (App) → Container (Card) → Component (Button) → State (Hover)
```

### 4. Property 기반 Variant 시스템

```python
button.setProperty("variant", "primary")  # QSS에서 [variant="primary"] 셀렉터로 적용
```

---

## 아키텍처 구조

### 권장 프로젝트 구조

```
your_app/
├── main.py                    # 앱 진입점
├── themes/
│   ├── default.json           # 기본 라이트 테마
│   ├── dark.json              # 다크 테마 (선택)
│   └── components/            # 컴포넌트별 QSS (선택)
│       ├── buttons.qss
│       └── inputs.qss
├── utils/
│   ├── __init__.py
│   └── theme_manager.py       # ThemeManager 클래스
├── widgets/
│   ├── __init__.py
│   └── themed_components.py   # 테마 적용 위젯
└── views/
    └── main_window.py
```

### 핵심 컴포넌트

1. **ThemeManager**: JSON 로드 → QSS 생성 → 앱 적용
2. **Theme JSON**: 디자인 토큰 정의
3. **Themed Widgets**: Property 기반 variant 지원

---

## 테마 시스템 설계

### JSON 테마 구조

```json
{
  "name": "App Theme",
  "version": "1.0.0",

  "colors": {
    "brand": {
      "primary": "#3ECF8E",
      "secondary": "#1DB7B0",
      "accent": "#7C3AED"
    },
    "background": {
      "primary": "#FFFFFF",
      "secondary": "#F5F5F5",
      "tertiary": "#EBEBEB"
    },
    "text": {
      "primary": "#171717",
      "secondary": "#737373",
      "disabled": "#A3A3A3"
    },
    "border": {
      "default": "#E5E5E5",
      "focus": "#3ECF8E"
    },
    "semantic": {
      "success": "#10B981",
      "warning": "#F59E0B",
      "error": "#EF4444",
      "info": "#3B82F6"
    },
    "neutral": {
      "50": "#FAFAFA",
      "100": "#F5F5F5",
      "200": "#E5E5E5",
      "300": "#D4D4D4",
      "400": "#A3A3A3",
      "500": "#737373",
      "600": "#525252",
      "700": "#404040",
      "800": "#262626",
      "900": "#171717"
    }
  },

  "typography": {
    "fontFamily": "Segoe UI, -apple-system, sans-serif",
    "sizes": {
      "xs": 10,
      "sm": 12,
      "base": 14,
      "lg": 16,
      "xl": 20,
      "2xl": 24,
      "3xl": 30
    },
    "weights": {
      "normal": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    }
  },

  "spacing": {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "2xl": 32
  },

  "radius": {
    "none": 0,
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "full": 9999
  },

  "shadows": {
    "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px rgba(0, 0, 0, 0.15)"
  },

  "components": {
    "button": {
      "minHeight": 36,
      "paddingX": 16,
      "paddingY": 8
    },
    "input": {
      "minHeight": 40,
      "padding": 12
    },
    "card": {
      "padding": 16,
      "borderRadius": 12
    }
  }
}
```

### ThemeManager 사용법

```python
from utils.theme_manager import load_theme, get_theme

# 1. 앱 생성 직후 테마 로드
app = QApplication(sys.argv)
load_theme(app, "themes/default.json")

# 2. 어디서든 테마 값 참조
theme = get_theme()
primary = theme.get("colors.brand.primary")
spacing = theme.get("spacing.md", 12)  # 기본값 지원
```

---

## QSS 작성 규칙

### 셀렉터 타입

```css
/* 1. 타입 셀렉터 - 모든 위젯에 적용 */
QPushButton { }

/* 2. ID 셀렉터 - objectName 기반 */
#submitButton { }

/* 3. 속성 셀렉터 - Property 기반 */
QPushButton[variant="primary"] { }
QLabel[status="error"] { }

/* 4. 상태 셀렉터 - 위젯 상태 */
QPushButton:hover { }
QPushButton:pressed { }
QPushButton:disabled { }
QPushButton:checked { }
QPushButton:focus { }

/* 5. 자손 셀렉터 */
QGroupBox QPushButton { }      /* 모든 자손 */
QGroupBox > QPushButton { }    /* 직계 자손만 */

/* 6. 서브컨트롤 */
QComboBox::drop-down { }
QScrollBar::handle:vertical { }
QCheckBox::indicator { }
```

### 우선순위 규칙

1. 인라인 `setStyleSheet()` > `app.setStyleSheet()`
2. ID 셀렉터 > 속성 셀렉터 > 타입 셀렉터
3. 더 구체적인 셀렉터가 우선

### 지원 속성

```css
/* 박스 모델 */
margin: 10px;
padding: 8px 16px;
border: 1px solid #E5E5E5;
border-radius: 8px;

/* 색상 */
background-color: #FFFFFF;
color: #171717;
selection-background-color: #3ECF8E;
selection-color: white;

/* 폰트 */
font-family: "Segoe UI";
font-size: 14px;
font-weight: 500;

/* 크기 */
min-height: 36px;
max-width: 200px;

/* 정렬 */
text-align: center;
```

### ⚠️ CSS와 다른 점

- `box-shadow` 미지원 (이미지로 대체)
- `flex`, `grid` 레이아웃 미지원
- `transition`, `animation` 제한적
- 일부 속성은 특정 위젯에서만 작동

---

## 컴포넌트별 스타일링

### QPushButton

```css
QPushButton {
    background-color: #F5F5F5;
    color: #171717;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 36px;
}

QPushButton:hover {
    background-color: #E5E5E5;
}

QPushButton:pressed {
    background-color: #D4D4D4;
}

QPushButton:disabled {
    background-color: #F5F5F5;
    color: #A3A3A3;
}

/* Variants */
QPushButton[variant="primary"] {
    background-color: #3ECF8E;
    color: white;
    border: none;
}

QPushButton[variant="primary"]:hover {
    background-color: #35b87d;
}

QPushButton[variant="secondary"] {
    background-color: transparent;
    color: #3ECF8E;
    border: 1px solid #3ECF8E;
}

QPushButton[variant="danger"] {
    background-color: #EF4444;
    color: white;
    border: none;
}
```

### QLineEdit / QTextEdit

```css
QLineEdit, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 12px;
    selection-background-color: #3ECF8E;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #3ECF8E;
}

QLineEdit:disabled {
    background-color: #F5F5F5;
    color: #A3A3A3;
}

QLineEdit[state="error"] {
    border-color: #EF4444;
}
```

### QComboBox

```css
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 36px;
}

QComboBox:hover {
    border-color: #3ECF8E;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #737373;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    selection-background-color: #3ECF8E;
    selection-color: white;
}
```

### QGroupBox (Card)

```css
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 500;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #171717;
}
```

### QTableWidget

```css
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    gridline-color: #E5E5E5;
}

QTableWidget::item {
    padding: 12px;
}

QTableWidget::item:selected {
    background-color: #3ECF8E;
    color: white;
}

QHeaderView::section {
    background-color: #F5F5F5;
    color: #171717;
    padding: 12px;
    border: none;
    border-bottom: 1px solid #E5E5E5;
    font-weight: 600;
}
```

### QScrollBar

```css
QScrollBar:vertical {
    background-color: #F5F5F5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #D4D4D4;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A3A3A3;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #F5F5F5;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #D4D4D4;
    border-radius: 6px;
    min-width: 30px;
}
```

### QCheckBox / QRadioButton

```css
QCheckBox, QRadioButton {
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #E5E5E5;
    background-color: #FFFFFF;
}

QCheckBox::indicator {
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 9px;
}

QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    background-color: #3ECF8E;
    border-color: #3ECF8E;
}
```

### QProgressBar

```css
QProgressBar {
    background-color: #F5F5F5;
    border: none;
    border-radius: 8px;
    text-align: center;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #3ECF8E;
    border-radius: 8px;
}
```

### QTabWidget

```css
QTabWidget::pane {
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F5F5F5;
    padding: 12px 24px;
    border: 1px solid #E5E5E5;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    border-bottom: 2px solid #3ECF8E;
}
```

---

## Best Practices

### ✅ 필수 체크리스트

#### 스타일 적용
- [ ] 모든 색상은 테마 JSON에서만 정의
- [ ] `QApplication` 생성 직후 `load_theme()` 호출
- [ ] Variant는 `setProperty()` 사용
- [ ] QGroupBox 자손 스타일은 부모(MainWindow)에서 적용

#### 구조화
- [ ] 계층적 JSON 구조 사용 (`colors.brand.primary`)
- [ ] 시맨틱 네이밍 (`success`, `warning`, `error`)
- [ ] 컴포넌트별 QSS 섹션 분리
- [ ] 테마 버전 관리

#### 유지보수
- [ ] 모든 위젯에 `setObjectName()` 설정
- [ ] 테마 변수 용도 문서화
- [ ] 다크 모드 테마 분리 준비

### 스타일 적용 순서

```python
# 1. 앱 생성
app = QApplication(sys.argv)

# 2. 테마 로드 (필수! 윈도우 생성 전)
load_theme(app, "themes/default.json")

# 3. 윈도우 생성 및 표시
window = MainWindow()
window.show()

# 4. 이벤트 루프
sys.exit(app.exec())
```

### Property Variant 패턴

```python
class ThemedButton(QPushButton):
    def __init__(self, text: str, variant: str = "default"):
        super().__init__(text)
        self.setProperty("variant", variant)
        # 스타일 갱신 트리거
        self.style().unpolish(self)
        self.style().polish(self)
```

### 동적 스타일 변경

```python
# Property 변경 후 스타일 갱신
button.setProperty("variant", "danger")
button.style().unpolish(button)
button.style().polish(button)
```

---

## 트러블슈팅

### 일반적인 문제

#### 1. 스타일이 적용되지 않음

**원인**: 테마 로드 순서 문제
```python
# ❌ Wrong
window = MainWindow()
load_theme(app, "theme.json")  # 너무 늦음

# ✅ Correct
load_theme(app, "theme.json")  # 먼저!
window = MainWindow()
```

#### 2. Property 셀렉터가 작동하지 않음

**원인**: 스타일 갱신 필요
```python
widget.setProperty("variant", "primary")
# 스타일 갱신 필수
widget.style().unpolish(widget)
widget.style().polish(widget)
```

#### 3. QGroupBox 자손 스타일이 적용되지 않음

**원인**: 자기 자신에게 setStyleSheet() 호출
```python
# ❌ Wrong - GroupBox 내부에서
class MyGroupBox(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QPushButton { ... }")  # 작동 안함!

# ✅ Correct - MainWindow에서
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 전체 앱 스타일에서 정의
```

#### 4. 색상이 예상과 다름

**원인**: 상속 또는 우선순위 문제
```css
/* 더 구체적인 셀렉터 사용 */
QGroupBox > QPushButton { ... }  /* 직계 자손 */
#specificButton { ... }          /* ID 셀렉터 */
```

### 디버깅 팁

1. **Visual Debugger 사용**: 실제 적용된 스타일 확인
2. **objectName 설정**: 위젯 식별 용이
3. **단계별 적용**: 한 번에 하나씩 스타일 추가
4. **콘솔 출력**: 테마 로드 확인

```python
theme = get_theme()
print(f"Primary color: {theme.get('colors.brand.primary')}")
```

---

## 관련 파일

- [theme_manager_template.py](theme_manager_template.py) - ThemeManager 전체 구현
- [theme_template.json](theme_template.json) - JSON 테마 템플릿
- [qss_guide.md](qss_guide.md) - 기본 QSS 가이드