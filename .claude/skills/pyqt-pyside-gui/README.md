# PyQt/PySide GUI Development Tools

## 개요

PySide6/PyQt6 GUI 개발을 위한 종합 도구 모음입니다.

## 📁 파일 구조

```
pyqt-pyside-gui/
├── skill.md                              # PyQt/PySide Best Practices ⭐
├── README.md                             # 이 파일
│
├── tools/                                # 개발 도구
│   ├── gui_analyzer.py                   # GUI 코드 정적 분석 도구 ⭐
│   └── example_ui.py                     # Analyzer 테스트용 예제
│
├── docs/                                 # 상세 문서
│   ├── README_GUI_ANALYZER.md            # GUI Analyzer 상세 가이드
│   └── GUI_DEBUGGING_TOOLS_SUMMARY.md    # 디버깅 도구 종합 비교
│
├── examples/                             # 학습 예제
│   ├── basic_app.py                      # 기본 PySide6 앱
│   ├── component_example.py              # 컴포넌트 사용 예제
│   ├── dialog_examples.py                # 다이얼로그 예제
│   ├── table_model.py                    # 테이블 모델 예제
│   ├── threaded_app.py                   # 멀티스레딩 예제
│   └── json_theme_example.py             # JSON 테마 시스템 예제
│
├── ui_components/                        # 재사용 가능한 컴포넌트
│   ├── __init__.py
│   ├── components.py                     # 커스텀 위젯
│   ├── constants.py                      # 상수 정의
│   ├── theme.py                          # 테마 관리
│   ├── theme_loader.py                   # 테마 로더
│   └── themes/                           # 테마 JSON 파일들
│       ├── contact-manager.json
│       ├── dark.json
│       └── default.json
│
└── references/                           # 참고 문서
    ├── advanced_patterns.md
    ├── ai_friendly_patterns.md
    ├── component_library.md
    ├── json_theme_guide.md
    └── qss_guide.md
```

## 🔧 GUI Code Analyzer - 정적 분석 도구

### 빠른 시작

```bash
cd .claude/skills/pyqt-pyside-gui/tools

# 예제 파일 분석
python gui_analyzer.py example_ui.py

# 실제 프로젝트 파일 분석
python gui_analyzer.py ../../../../production_tracker_app/views/main_window.py
```

### 주요 기능

#### 🌳 Widget Tree 자동 생성
- AST 파싱을 통한 위젯 계층 구조 추출
- 부모-자식 관계 자동 감지
- 레이아웃 관계 분석

#### 🔍 Widget Property 분석
각 위젯의 다음 속성 분석:
- **Geometry**: 위치 및 크기 (x, y, width, height)
- **Visibility**: 표시/숨김 상태
- **Stylesheet**: 적용된 스타일
- **Parent/Children**: 부모-자식 관계
- **Layout**: 레이아웃 타입

#### ⚠️ 자동 이슈 감지

1. **Size Issues**
   - 너무 작은 위젯 (10px 미만)
   - Min/Max size 충돌
   - 비정상적인 크기 설정

2. **Visibility Issues**
   - 숨겨진 위젯 (setVisible(False))
   - 비활성화된 위젯 (setEnabled(False))

3. **Overlapping Detection**
   - 위젯 간 겹침 감지
   - 좌표 기반 충돌 검사

4. **Layout Issues**
   - 부모 없는 위젯 (메모리 누수 위험)
   - 레이아웃에 추가되지 않은 위젯

5. **Naming Issues**
   - 의미 없는 변수명 (widget1, var2 등)

#### ✅ skill.md Best Practices 검증

- Theme Manager 사용 (`get_theme()`)
- Themed Components 사용
- 하드코딩 색상 검사 (#RRGGBB)
- Object Names 사용 (setObjectName)
- Docstrings 존재

#### 📊 HTML Report 생성

다음 내용을 포함한 종합 리포트:
- Statistics Dashboard
- Widget Tree Visualization
- Widget Details Table
- Issues List (severity별)
- Best Practices Checklist
- Widget Type Distribution

### 사용 예시

#### 1. 예제 파일 분석
```bash
python gui_analyzer.py example_ui.py
```

**출력:**
```
🔍 Analyzing: example_ui.py
✅ Analysis complete: 16 widgets, 21 issues
📄 Report generated: example_ui_analysis_report.html

============================================================
📊 Analysis Summary:
============================================================
Total Widgets: 16
Total Issues: 21
  - Errors: 0
  - Warnings: 18
  - Info: 3

✅ Report saved to: example_ui_analysis_report.html
```

#### 2. 실제 프로젝트 분석
```bash
python gui_analyzer.py ../../../production_tracker_app/views/main_window.py
```

**출력:**
```
🔍 Analyzing: main_window.py
✅ Analysis complete: 5 widgets, 5 issues
📄 Report generated: main_window_analysis_report.html
```

### HTML Report 구조

생성된 HTML 리포트는 다음을 포함합니다:

1. **Statistics Section**
   - Total Widgets, Total Issues
   - Errors/Warnings/Info 개수

2. **Widget Tree**
   - 계층 구조 시각화
   - 각 위젯의 타입과 이름

3. **Widget Details Table**
   - 위젯별 상세 속성
   - Geometry, Visibility, Issues

4. **Issues Detected**
   - Severity별 이슈 목록
   - 라인 번호 포함

5. **Best Practices Checklist**
   - skill.md 준수 여부
   - ✅/❌ 표시

6. **Widget Type Distribution**
   - 위젯 타입별 통계
   - 그래프 시각화

## 📚 관련 도구

### 1. Visual Debugger (동적 분석)
**위치**: `production_tracker_app/visual_debugger.py`

**사용법:**
```python
from visual_debugger import launch_with_debugger

app = QApplication(sys.argv)
window = MainWindow()
debugger = launch_with_debugger(window)
sys.exit(app.exec())
```

**특징:**
- 실행 중인 앱 분석
- 실시간 위젯 하이라이트
- 동적 생성 위젯 감지

### 2. Hot Reload (개발 도구)
**위치**: `production_tracker_app/hot_reload.py`

**사용법:**
```bash
python hot_reload.py
```

**특징:**
- 파일 변경 시 자동 재시작
- `.py`, `.json` 파일 감지
- 개발 생산성 극대화

## 🔄 권장 워크플로우

```
1. Hot Reload 실행 (개발 중)
   └─> 파일 변경 시 자동 재시작

2. Visual Debugger 실행 (디버깅)
   └─> 실제 위젯 구조 확인
   └─> 렌더링 크기 확인

3. GUI Analyzer 실행 (코드 리뷰 전)
   └─> python gui_analyzer.py your_file.py
   └─> HTML 리포트 확인
   └─> Best practices 검증
   └─> 이슈 수정

4. 프로덕션 배포 ✅
```

## 📖 상세 문서

- **[skill.md](skill.md)** - PyQt/PySide Best Practices 전체 가이드
- **[docs/README_GUI_ANALYZER.md](docs/README_GUI_ANALYZER.md)** - GUI Analyzer 상세 문서
- **[docs/GUI_DEBUGGING_TOOLS_SUMMARY.md](docs/GUI_DEBUGGING_TOOLS_SUMMARY.md)** - 3가지 도구 비교
- **[tools/example_ui.py](tools/example_ui.py)** - 테스트용 예제 파일

## 📚 학습 예제

- **[examples/basic_app.py](examples/basic_app.py)** - PySide6 기본 앱 구조
- **[examples/component_example.py](examples/component_example.py)** - 커스텀 컴포넌트 사용법
- **[examples/dialog_examples.py](examples/dialog_examples.py)** - 다양한 다이얼로그 패턴
- **[examples/table_model.py](examples/table_model.py)** - QTableView + Model/View
- **[examples/threaded_app.py](examples/threaded_app.py)** - QThread 멀티스레딩
- **[examples/json_theme_example.py](examples/json_theme_example.py)** - JSON 테마 시스템

## 🎯 활용 사례

### 코드 리뷰
```bash
# PR 전에 모든 UI 파일 분석
python gui_analyzer.py views/main_window.py
python gui_analyzer.py views/settings_dialog.py
python gui_analyzer.py widgets/custom_card.py
```

### 리팩토링
- 하드코딩된 색상 찾기
- 테마 시스템 적용 여부 확인
- 네이밍 컨벤션 검증

### 문서화
- 위젯 구조 자동 문서화
- 새 팀원 온보딩 자료
- 아키텍처 설명

## ⚙️ 설정

### Python 버전
- Python 3.9 이상 필요

### 의존성
```bash
# GUI Analyzer는 표준 라이브러리만 사용
# ast, re, json, pathlib, typing, dataclasses, datetime
```

## 🐛 문제 해결

### 위젯이 감지되지 않음
- 코드가 표준 패턴을 따르는지 확인
- `self.widget = QWidget()` 형식 사용
- 동적 생성은 감지 불가 (Visual Debugger 사용)

### UnicodeDecodeError
```bash
# 파일 인코딩 확인
file --mime-encoding your_file.py
```

### AST 파싱 오류
- 문법 오류가 있는지 확인
- Python 3.9+ 구문 사용

## 📝 라이선스

Copyright (c) 2025 F2X. All rights reserved.

## 👥 지원

문제가 발생하면:
- GitHub Issues
- Email: support@f2x.com
