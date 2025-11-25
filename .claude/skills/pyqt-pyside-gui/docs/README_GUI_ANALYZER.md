# GUI Code Analyzer - 정적 코드 분석 도구

## 개요

PySide6/PyQt6 UI 코드를 정적으로 분석하여 종합적인 리포트를 생성하는 도구입니다.

## 주요 기능

### 🌳 Widget Tree 자동 생성
- Python 코드에서 위젯 계층 구조 자동 추출
- 부모-자식 관계 시각화
- 레이아웃 관계 분석

### 🔍 Widget Property 분석
각 위젯별로 다음 속성 분석:
- **Geometry**: 위치 및 크기 (x, y, width, height)
- **Visibility**: 표시/숨김 상태
- **Min/Max Size**: 최소/최대 크기 설정
- **Stylesheet**: 적용된 스타일시트
- **Parent/Children**: 부모-자식 관계
- **Layout Type**: 레이아웃 타입

### ⚠️ 자동 이슈 감지

#### 1. Size Issues
- 너무 작은 위젯 (10px 미만)
- Min/Max size 충돌
- 비정상적인 크기 설정

#### 2. Visibility Issues
- 숨겨진 위젯 (setVisible(False))
- 비활성화된 위젯 (setEnabled(False))

#### 3. Overlapping Detection
- 위젯 간 겹침 감지
- 좌표 기반 충돌 검사
- 같은 위치에 여러 위젯 배치 경고

#### 4. Layout Issues
- 부모 없는 위젯 (메모리 누수 위험)
- 레이아웃에 추가되지 않은 위젯
- 레이아웃 충돌

#### 5. Naming Issues
- 의미 없는 변수명 (widget1, var2 등)
- 네이밍 컨벤션 위반

### ✅ skill.md Best Practices 검증

- **Theme Manager 사용**: `get_theme()` 호출 확인
- **Themed Components 사용**: ThemedCard, ThemedLabel 등 사용 여부
- **하드코딩 색상 제거**: 코드에 #RRGGBB 형식의 색상 있는지 검사
- **Object Names 사용**: setObjectName() 사용 여부
- **Docstrings 존재**: 문서화 수준 확인

### 📊 HTML Report 생성

다음 내용을 포함한 종합 리포트:
- Statistics Dashboard
- Widget Tree Visualization
- Widget Details Table
- Issues List (severity별)
- Best Practices Checklist
- Widget Type Distribution

## 사용 방법

### 기본 사용
```bash
cd .claude/skills/pyqt-pyside-gui/tools
python gui_analyzer.py <path_to_ui_file.py>
```

### 예시
```bash
# Main window 분석
python gui_analyzer.py ../../../../neurohub_client/views/main_window.py

# Dialog 분석
python gui_analyzer.py ../../../../neurohub_client/views/login_dialog.py

# Widget 분석
python gui_analyzer.py ../../../../neurohub_client/widgets/lot_display_card.py
```

### 출력 결과
```
🔍 Analyzing: views/main_window.py
✅ Analysis complete: 5 widgets, 5 issues
📄 Report generated: main_window_analysis_report.html

============================================================
📊 Analysis Summary:
============================================================
Total Widgets: 5
Total Issues: 5
  - Errors: 0
  - Warnings: 5
  - Info: 0

✅ Report saved to: main_window_analysis_report.html
```

## HTML Report 구조

### 1. Statistics Section
- Total Widgets
- Total Issues
- Errors/Warnings/Info 개수
- Lines of Code

### 2. Widget Tree
```
ROOT
├── QMainWindow MainWindow
    ├── QWidget central_widget
    │   ├── QVBoxLayout layout
    │   │   ├── InfoCard lot_card
    │   │   ├── QLabel status_label
    │   │   └── ThemedLabel recent_label
    └── QStatusBar status_bar
        └── StatusIndicator connection_indicator
```

### 3. Widget Details Table
| Name | Type | Parent | Geometry | Visible | Issues |
|------|------|--------|----------|---------|--------|
| lot_card | InfoCard | central_widget | (0, 0, 800, 120) | ✅ | None |
| status_label | QLabel | layout | N/A | ✅ | No parent |

### 4. Issues Detected
각 이슈는 다음 정보 포함:
- **Severity**: error/warning/info
- **Category**: size/visibility/overlap/layout/naming
- **Widget**: 문제가 있는 위젯
- **Message**: 상세 설명
- **Line Number**: 코드 라인 번호

### 5. Best Practices Checklist
- ✅ Uses Theme Manager (get_theme())
- ✅ Uses Themed Components
- ❌ No Hardcoded Colors (found 3)
- ❌ Uses Object Names (setObjectName)
- ✅ Has Docstrings

### 6. Widget Type Distribution
위젯 타입별 개수와 그래프

## 분석 알고리즘

### AST 기반 파싱
Python의 `ast` 모듈을 사용하여 코드를 추상 구문 트리로 파싱:

```python
tree = ast.parse(code)
```

### Widget 감지
1. **Class Definition 분석**: Qt 위젯을 상속하는 클래스 찾기
2. **Assignment 분석**: `self.widget = QWidget()` 패턴 감지
3. **Method Call 분석**: `setGeometry()`, `setStyleSheet()` 등 호출 추적

### Property 추출
```python
# Example: setGeometry(10, 20, 300, 200)
widget.geometry = (10, 20, 300, 200)

# Example: setMinimumSize(100, 50)
widget.properties['min_size'] = (100, 50)
```

### 겹침 감지 알고리즘
```python
def rectangles_overlap(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    return not (x1 + w1 < x2 or x2 + w2 < x1 or
               y1 + h1 < y2 or y2 + h2 < y1)
```

## 지원 위젯 타입

### Qt Standard Widgets
- QMainWindow, QWidget, QDialog
- QLabel, QPushButton, QLineEdit, QTextEdit
- QComboBox, QCheckBox, QRadioButton
- QSpinBox, QDoubleSpinBox, QSlider
- QListWidget, QTreeWidget, QTableWidget
- QTabWidget, QGroupBox, QFrame
- QMenuBar, QToolBar, QStatusBar

### Qt Layouts
- QVBoxLayout, QHBoxLayout
- QGridLayout, QFormLayout
- QStackedLayout

### Custom Themed Components
- ThemedCard, ThemedLabel, ThemedButton
- InfoCard, StatusIndicator, StatBadge
- LotDisplayCard, StatsCard

## 한계 및 제약사항

### 1. 동적 코드 분석 불가
- 런타임에 생성되는 위젯은 감지 못함
- 조건문/반복문 내부의 위젯 생성은 제한적

### 2. 복잡한 표현식
- 변수나 함수 호출로 전달되는 값은 추적 어려움
- 예: `setGeometry(*calculate_geometry())`

### 3. 외부 모듈
- 다른 파일에서 import한 위젯은 타입만 인식

## Visual Debugger와의 비교

| 특성 | GUI Analyzer (정적) | Visual Debugger (동적) |
|------|-------------------|---------------------|
| 분석 시점 | 코드 작성 후 | 앱 실행 중 |
| 위젯 감지 | AST 파싱 | 실제 위젯 트리 |
| 동적 위젯 | ❌ 감지 불가 | ✅ 모두 감지 |
| 실제 크기 | ❌ 코드 기반 추정 | ✅ 실제 렌더링 크기 |
| 실행 필요 | ❌ 불필요 | ✅ 필요 |
| 리포트 | ✅ HTML 저장 | ⚠️ 실시간만 |
| 코드 품질 | ✅ Best practices | ❌ 미지원 |

**권장 사용법:**
1. **개발 중**: GUI Analyzer로 코드 품질 검증
2. **테스트**: Visual Debugger로 실제 렌더링 확인
3. **디버깅**: 두 도구 병행 사용

## 활용 사례

### 1. 코드 리뷰
```bash
# PR 전에 모든 UI 파일 분석
python gui_analyzer.py views/main_window.py
python gui_analyzer.py views/settings_dialog.py
python gui_analyzer.py widgets/custom_card.py
```

### 2. 리팩토링
- 하드코딩된 색상 찾기
- 테마 시스템 적용 여부 확인
- 네이밍 컨벤션 검증

### 3. 품질 관리
- CI/CD 파이프라인에 통합
- 자동 리포트 생성
- 이슈 추적

### 4. 문서화
- 위젯 구조 자동 문서화
- 새 팀원 온보딩 자료
- 아키텍처 설명

## 향후 개선 계획

### Phase 1 (현재)
- ✅ Basic AST parsing
- ✅ Widget tree generation
- ✅ Issue detection
- ✅ HTML report

### Phase 2 (계획)
- [ ] 더 정교한 동적 분석 (eval 사용)
- [ ] Layout 최적화 제안
- [ ] 접근성 검사 (WCAG)
- [ ] 다국어 지원

### Phase 3 (미래)
- [ ] 자동 수정 제안 (Auto-fix)
- [ ] VS Code Extension
- [ ] GitHub Action Integration
- [ ] Performance metrics

## 예제 출력

### Console Output
```
🔍 Analyzing: views/main_window.py
✅ Analysis complete: 15 widgets, 3 issues
📄 Report generated: main_window_analysis_report.html

============================================================
📊 Analysis Summary:
============================================================
Total Widgets: 15
Total Issues: 3
  - Errors: 0
  - Warnings: 2
  - Info: 1

✅ Report saved to: main_window_analysis_report.html
```

### HTML Report Preview
![Example Report](https://placeholder.com/report-preview.png)

## 문제 해결

### ImportError: No module named 'ast'
```bash
# Python 3.9+ 필요
python --version
```

### UnicodeDecodeError
```bash
# 파일 인코딩 확인
file --mime-encoding your_file.py
```

### 위젯이 감지되지 않음
- 코드가 표준 패턴을 따르는지 확인
- `self.widget = QWidget()` 형식 사용
- 동적 생성은 감지 불가

## 기여 방법

이슈나 개선 제안은 다음으로:
- GitHub Issues
- Pull Requests
- Email: support@f2x.com

## 라이선스

Copyright (c) 2025 F2X. All rights reserved.

## 참고 자료

- [skill.md](../skill.md) - PySide6/PyQt6 Best Practices
- [visual_debugger.py](../../../neurohub_client/visual_debugger.py) - 동적 디버거
- [ARCHITECTURE.md](../../../neurohub_client/ARCHITECTURE.md) - 아키텍처 가이드