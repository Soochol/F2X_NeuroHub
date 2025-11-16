# 연락처 관리 앱

**PyQt/PySide GUI Skill**을 완전히 활용한 연락처 관리 애플리케이션입니다.

Skill 아키텍처 패턴을 따라 **커스텀 JSON 테마**와 **재사용 가능한 컴포넌트**로 구현되었습니다.

## 기능

- ✅ 연락처 추가 (이름, 전화번호, 이메일)
- ✅ 연락처 목록 조회
- ✅ 연락처 수정
- ✅ 연락처 삭제
- ✅ 연락처 검색 (이름, 전화번호, 이메일)
- ✅ JSON 파일로 데이터 저장
- ✅ 다크/라이트 테마 전환
- ✅ 폼 유효성 검사

## Skill 아키텍처 (중요!)

이 프로젝트는 `.claude/skills/pyqt-pyside-gui` Skill의 철학을 따릅니다:

### 1. 커스텀 JSON 테마 ✨

**파일**: `.claude/skills/pyqt-pyside-gui/scripts/ui_components/themes/contact-manager.json`

```json
{
  "colors": {
    "primary": { "main": "#2563eb" },    // 파란색 계열
    "success": { "main": "#10b981" },    // 초록색 (추가 버튼)
    "danger": { "main": "#ef4444" }      // 빨간색 (삭제 버튼)
  }
}
```

**사용법**:
```python
from ui_components import load_theme

app = QApplication(sys.argv)
load_theme(app, "contact-manager")  # 커스텀 테마 로드
```

### 2. 재사용 가능한 컴포넌트 🔧

**파일**: `contact_manager/contact_components.py`

모든 컴포넌트는 `BaseComponent`를 상속받아 다른 프로젝트에서도 재사용 가능합니다:

#### ContactCard
```python
from contact_components import ContactCard

card = ContactCard(
    contact=contact,
    on_edit=lambda c: edit_contact(c),
    on_delete=lambda c: delete_contact(c)
)
layout.addWidget(card.get_widget())
```

#### ContactForm
```python
from contact_components import ContactForm

form = ContactForm(
    on_submit=lambda values: add_contact(values),
    on_clear=lambda: refresh_ui()
)
layout.addWidget(form.get_widget())

# 폼 값 가져오기
values = form.get_values()  # {"name": "...", "phone": "...", "email": "..."}

# 폼 채우기
form.populate(name="홍길동", phone="010-1234-5678", email="hong@example.com")
```

#### ContactSearchBar
```python
from contact_components import ContactSearchBar

search = ContactSearchBar(on_search=lambda query: filter_contacts(query))
layout.addWidget(search.get_widget())
```

## 사용 기술

- **PySide6** - Qt GUI 프레임워크
- **ui_components** - 커스텀 컴포넌트 라이브러리
- **JSON** - 데이터 저장 및 테마 관리

## 프로젝트 구조

```
contact_manager/
├── main.py                  # 앱 실행 진입점
├── contact_manager.py       # 메인 UI 윈도우
├── contact_components.py    # 재사용 가능한 컴포넌트 ⭐
│   ├── ContactCard
│   ├── ContactForm
│   └── ContactSearchBar
├── models.py               # Contact 데이터 클래스
├── storage.py              # JSON 저장/로드 및 CRUD
├── contacts.json           # 데이터 파일 (자동 생성)
├── requirements.txt        # 의존성
└── README.md              # 이 파일

.claude/skills/pyqt-pyside-gui/scripts/ui_components/themes/
└── contact-manager.json    # 커스텀 테마 ⭐
```

## 설치 및 실행

### 방법 1: uv 사용 (추천) ⚡

가장 빠르고 간단한 방법입니다:

```bash
cd contact_manager

# PySide6 설치
uv pip install PySide6

# 앱 실행
uv run main.py
```

또는 pyproject.toml을 사용하여 자동 설치:

```bash
cd contact_manager
uv sync  # 의존성 자동 설치
uv run main.py
```

### 방법 2: pip 사용

```bash
cd contact_manager

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
python main.py
```

## 사용법

### 연락처 추가
1. "새 연락처 추가" 섹션에서 이름, 전화번호, 이메일 입력
2. "추가" 버튼 클릭
3. 폼이 자동으로 초기화되고 목록에 추가됨

### 연락처 검색
- 상단 검색창에 이름, 전화번호, 이메일 입력
- 실시간으로 필터링됨

### 연락처 수정
1. 목록에서 수정할 연락처의 "수정" 버튼 클릭
2. 폼에 기존 정보가 자동 입력됨
3. 정보 수정 후 "추가" 버튼으로 저장

### 연락처 삭제
1. 목록에서 삭제할 연락처의 "삭제" 버튼 클릭
2. 확인 대화상자에서 "Yes" 클릭

### 테마 전환
- 우측 상단 테마 버튼 클릭
- 🌙 Dark / ☀️ Light 토글
- 커스텀 contact-manager 테마 ↔ dark 테마

## Skill 패턴 학습 포인트

이 프로젝트를 통해 다음을 학습할 수 있습니다:

### 1. JSON 기반 CSS 관리 ✅
- `.json` 파일로 테마 정의
- 일관된 색상, 타이포그래피, 간격
- 런타임 테마 전환 지원

### 2. 재사용 가능한 컴포넌트 ✅
- `BaseComponent` 상속
- `.get_widget()` 패턴 사용
- Signal/Slot 통합
- 다른 프로젝트에서 import 가능

### 3. Component-First 개발 ✅
- UI 로직을 컴포넌트로 캡슐화
- 메인 앱 코드 간결화
- 테스트 용이성 향상

### 4. 테마 시스템 활용 ✅
- `load_theme(app, "contact-manager")`
- 색상 변경 시 JSON만 수정
- 코드 변경 불필요

## 사용된 ui_components

### 기본 컴포넌트
- `Card` - 폼 섹션과 검색 바
- `FormField` - 유효성 검사가 있는 입력 필드
- `Input` - 검색 필드
- `Button` - 액션 버튼
- `ButtonGroup` - 버튼 그룹화
- `Label` - 텍스트 표시
- `Spacing` - 일관된 간격
- `load_theme()` - 테마 관리

### 커스텀 컴포넌트 (이 프로젝트)
- `ContactCard` - 연락처 카드 (수정/삭제 버튼 포함)
- `ContactForm` - 연락처 입력 폼 (유효성 검사 포함)
- `ContactSearchBar` - 검색 입력

## 데이터 저장

연락처 데이터는 `contacts.json` 파일에 자동으로 저장됩니다.

```json
{
  "contacts": [
    {
      "id": "uuid-string",
      "name": "홍길동",
      "phone": "010-1234-5678",
      "email": "hong@example.com"
    }
  ]
}
```

## Skill 베스트 프랙티스

### ✅ 좋은 프롬프트 예시

```
PySide6로 연락처 관리 앱 만들어줘:
- ui_components의 ContactCard, ContactForm 컴포넌트 사용
- load_theme(app, 'contact-manager')로 커스텀 테마 로드
- ContactCard는 수정/삭제 버튼 포함
- 창 크기 700x800
```

### ❌ 나쁜 프롬프트 예시

```
연락처 앱 만들어줘
색상 바꿔줘
```

**차이점**: 좋은 프롬프트는 정확한 컴포넌트 이름, 테마 이름, 크기 등을 명시합니다.

## 다른 프로젝트에서 컴포넌트 재사용하기

```python
# 1. contact_components.py를 프로젝트에 복사
# 2. 원하는 컴포넌트 import

from contact_components import ContactCard, ContactForm

# ContactCard 사용
card = ContactCard(
    contact=my_contact,
    on_edit=my_edit_handler,
    on_delete=my_delete_handler
)

# ContactForm 사용
form = ContactForm(
    on_submit=my_submit_handler,
    title="새 회원 등록"  # 제목 커스터마이징 가능
)
```

## 개선 아이디어

- [ ] 연락처 그룹/카테고리 기능 → **GroupSelector** 컴포넌트 생성
- [ ] 연락처 이미지 추가 → **AvatarUploader** 컴포넌트 생성
- [ ] CSV/Excel 내보내기/가져오기 → **DataExporter** 컴포넌트 생성
- [ ] 연락처 즐겨찾기 → ContactCard에 **favorite** 변형 추가
- [ ] 고급 검색 필터 → **AdvancedSearchBar** 컴포넌트 생성
- [ ] 연락처 중복 확인 → ContactForm에 **validation** 로직 추가

## 라이선스

이 프로젝트는 학습 목적으로 제작되었습니다.

## 기여

컴포넌트 개선 사항이나 새로운 컴포넌트 아이디어가 있다면 자유롭게 제안해주세요!
