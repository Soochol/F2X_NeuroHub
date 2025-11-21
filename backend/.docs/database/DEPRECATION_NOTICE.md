# 📢 문서 사용 중단 공지 (Deprecation Notice)

## ⚠️ 중요 공지

이 폴더의 모든 데이터베이스 문서는 **2025-11-21부터 더 이상 사용되지 않습니다**.

### 📍 새로운 위치

모든 데이터베이스 요구사항 문서는 다음 위치로 통합되었습니다:

```
database/.docs/requirements/
```

---

## 📋 문서 마이그레이션 현황

| 기존 파일 | 새 위치 | 상태 | 마이그레이션 날짜 |
|---------|-------|------|-----------------|
| 05-index-strategy.md | database/.docs/requirements/04-index-strategy.md | ✅ 완료 | 2025-11-21 |
| 06-migration-plan.md | database/.docs/requirements/05-migration-plan.md | ✅ 완료 | 2025-11-21 |
| 07-data-dictionary.md | database/.docs/requirements/06-data-dictionary.md | ✅ 완료 | 2025-11-21 |
| 04-business-rules.md | database/.docs/requirements/DATABASE-REQUIREMENTS.md (Section 6) | ✅ 병합 | 2025-11-21 |
| 02-entity-definitions.md | database/.docs/requirements/02-entity-definitions.md | ✅ 유지 | - |
| 03-relationship-specs.md | database/.docs/requirements/03-relationship-specifications.md | ✅ 유지 | - |

---

## 🔍 변경 사항 요약

### 추가된 내용
- **WIP 시스템 통합**: 모든 문서에 WIP (Work-In-Progress) 추적 시스템 관련 내용 추가
  - 신규 테이블: wip_items, wip_process_history
  - 신규 인덱스: 10개 (WIP 관련)
  - 신규 컬럼: 24개

### 강화된 내용
- **BR-008, BR-009, BR-010**: 원본 비즈니스 규칙을 DATABASE-REQUIREMENTS.md에 통합
- **새로운 README.md**: 모든 문서에 대한 가이드 및 네비게이션 추가

### 개선된 내용
- 모든 내부 링크를 새 위치로 업데이트
- 통일된 문서 구조 및 네이밍

---

## 🚀 마이그레이션 안내

### 개발자를 위해

**새로운 시작:**
1. [database/.docs/requirements/README.md](../../database/.docs/requirements/README.md) 읽기
2. [database/.docs/requirements/DATABASE-REQUIREMENTS.md](../../database/.docs/requirements/DATABASE-REQUIREMENTS.md) 참고

**북마크 업데이트:**
- ❌ `backend/.docs/database/` 폴더
- ✅ `database/.docs/requirements/` 폴더

### 프로젝트 관리자를 위해

**문서 참조:**
- 모든 프로젝트 가이드 및 위키에서 경로 업데이트
- CI/CD 파이프라인에서 문서 경로 변경

---

## 📞 문의

이 통합과 관련된 질문이 있으면:
- GitHub Issues: F2X_NeuroHub 프로젝트
- Email: database-team@withforce.com

---

## 📅 타임라인

| 날짜 | 이벤트 |
|------|--------|
| 2025-11-21 | 문서 통합 완료 |
| 2025-12-01 | 기존 문서 삭제 예정 |

**2025-12-01 이후**: 이 폴더의 문서는 삭제될 예정입니다.

---

**마지막 업데이트**: 2025-11-21

---

## 📚 관련 링크

- [새 위치: database/.docs/requirements/README.md](../../database/.docs/requirements/README.md)
- [DATABASE-REQUIREMENTS.md](../../database/.docs/requirements/DATABASE-REQUIREMENTS.md)
- [마이그레이션 계획](../../database/.docs/requirements/05-migration-plan.md)

---

**이 폴더는 더 이상 유지보수되지 않습니다.** ⛔
