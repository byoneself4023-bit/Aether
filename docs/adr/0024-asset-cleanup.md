# ADR 0024 — 자료 인덱스 정착 + pre-existing 14건 분류 (CL-1)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: CL-1 (자료 정리 / 코드 영역 X)
- **결정 근거**: V-1b 머지 후 자료 영역 누적 (ADR 23건 / audit 14건 정착 + 9건 pre-existing / 폴더 22건 .md 영역) — 사용자 / 본인 모두 파악 어려움

---

## 컨텍스트

V-1b (PR #37) 머지 후 Aether 자료 영역 누적 영역 확인:
- ADR 23건 (0001-0023)
- audit 폴더 22건 .md (정착 14 + pre-existing 8)
- phase3/ 폴더 11건 (Top 10 카드 본문)
- pre-existing untracked 14건 (8건 audit + INTERVIEW + 4 폴더 + 1 자료)
- docs/ 기존 영역 7 폴더 (Design / Differentiation / Guide / Integration / Interview / Phase / Review)

자료 영역 인덱스 X 시점에 6개월 후 본인 답 X / 다른 개발자 인지 X 위험. CL-1 = 자료 인덱스 정착 (코드 정리 = CL-2 / 의존성 정리 = CL-3 영역 분리 / 1책임 의무).

---

## 결정 (6 분기 추적)

### 분기 1: pre-existing untracked 14건 처리 — **B 채택** (분류 본문만 정착 / 자동 이동 X)

옵션 A (모두 docs/archive/ 이동) = 안전 기본값 / 단순 / 다만 사용자 결정 영역 잠식.
옵션 B (선택) = Claude Code 분류 + 추천 본문 (자료 인덱스에 명시) / 자동 이동 X / 사용자 결정 의무 (별도 시점).
옵션 C (그대로 untracked + 인덱스 명시) = V-1b 패턴 일관성 / 다만 분류 본문 X = 사용자 결정 영역 정착 X.

### 분기 2: 자료 인덱스 위치 — **C 채택** (docs/README + audit/README + adr/README 3건)

옵션 A (docs/README만) = 단일 진입점 / 다만 audit 디테일 / ADR 카테고리 영역 X.
옵션 B (audit/README만) = 부분.
옵션 C (선택) = 3건 신규 (root docs 진입 + audit 디테일 + ADR 카테고리) — 영역 분리 + 진입 흐름 정착.

### 분기 3: ADR 인덱스 위치 — **A 채택** (docs/adr/README.md)

옵션 A (선택) = ADR 폴더 내 진입 자연스러움.
옵션 B (docs/adr/INDEX.md) = README 패턴 일관성 X.
옵션 C (docs/README.md 통합) = 자료 분리 X / 영역 ↑↑.

### 분기 4: ADR 카테고리 분류 — **A 채택** (카드별)

옵션 A (선택) = 카드별 (Top 10 / D 시리즈 / 메타+V+CL) — 작업 흐름 인지 ↑.
옵션 B (본질별) = 인프라 / AI / 보안 / 자료 / 메타 — 본질 추적 ↑ / 다만 카드 영역 추적 X.
옵션 C (시간 순서) = 0001 → 0024 — 본질 분리 X.

### 분기 5: ADR 의무 — **A 채택** (ADR 0024)

옵션 A (선택) = 본 ADR / 양면 정책 14 ADR (0011-0024) 정립 / 자료 정리 영역 결정 추적.
옵션 B (ADR X) = 자료 인덱스 = 정착 / 결정 X / 다만 영구 보류 결정 (CL-2 / CL-3 / pre-existing 자동 처리 X) 추적 X.

### 분기 6: 영역 분리 — **A 채택** (CL-1 자료 / CL-2 코드 / CL-3 의존성)

옵션 A (선택) = CL-1 자료 인덱스 / CL-2 코드 정리 / CL-3 의존성 정리 — 영역 한정 / 1책임 의무 (CLAUDE.md §6).
옵션 B (CL-1 통합) = 영역 ↑↑ / 코드 변경 = 회귀 검증 의무 + 자료 변경 + 의존성 변경 = 카드 1책임 위반.

---

## Decision

1. **docs/README.md 신규** (~150 LOC) — Aether 자료 폴더 영역 한 눈에 보기 + 핵심 자료 4건 + 폴더 구조 + 카드 18건 인덱스 + 갱신 정책 + 면접 자료 영역 + 다음 카드 진입.
2. **docs/agent-capability-audit/README.md 신규** (~180 LOC) — audit 자료 본질 + 정착 14건 디테일 + pre-existing 14건 분류 (A 면접/이력서 / B Phase 2 / C PoC / D 코드 영역 / 추천 본문) + 갱신 정책.
3. **docs/adr/README.md 신규** (~150 LOC) — ADR 23건 카테고리별 (Top 10 / D 시리즈 / 메타+V+CL) + 양면 정책 14 ADR (정착 7 / 보류 3 / 메타 4 / 정리 1) + ADR 형식 + 갱신 정책.
4. **ADR 0024** 결정 추적 (본 ADR / 6 분기 / 영구 보류 영역 / CL-2 + CL-3 트리거).
5. **AGENTS.md §7** CL-1 baseline 행 추가 (3 자료 인덱스 정착 + 양면 정책 14 ADR).

---

## 영구 보류 영역 (CL-1 영역 X)

| 영역 | 보류 사유 |
|------|-----------|
| **코드 정리 (CL-2 카드)** | 영역 분리 / 회귀 검증 의무 / 1책임 의무 |
| **의존성 정리 (CL-3 카드)** | 영역 분리 / requirements.txt / package.json |
| **pre-existing untracked 14건 자동 처리** | 사용자 결정 의무 / archive 안전 기본값 X / 분류 본문만 정착 |

---

## 영향

### 시그널 강화 (+)

- **양면 정책 14 ADR 정립**: 0011-**0024** = 시니어 시그널 누적
- **자료 인덱스 정착**: 6개월 후 본인 답 가능 (PRINCIPLES 원칙 5)
- **사용자 파악 가능**: docs/README.md 진입 → audit / ADR 디테일 흐름
- **pre-existing 14건 분류 본문**: 사용자 결정 영역 정착 (자동 처리 X = 안전)
- **카드 1책임 의무**: CL-1 (자료) / CL-2 (코드) / CL-3 (의존성) 영역 분리

### 트레이드오프 (−)

- 자료 4건 신규 (~600 LOC 합산) — 자료 영역 ↑
- pre-existing 14건 즉시 처리 X — 사용자 결정 카드 의무 (다른 시점 / 영역 분리)
- 기존 docs/ 폴더 7 영역 (Design/Differentiation/Guide 등) 디테일 인덱스 X — docs/README.md 단순 명시만

---

## 미적용 영역 (시나리오 B / 다른 카드 트리거)

| 영역 | 트리거 |
|------|--------|
| 코드 정리 (사용자 본문 명시 시점) | CL-2 카드 |
| 의존성 정리 (requirements.txt / package.json) | CL-3 카드 |
| pre-existing 14건 일괄 git add + commit | 사용자 결정 카드 (커밋 / archive / 제거 영역) |
| 기존 docs/ 폴더 7 영역 디테일 인덱스 | 시나리오 B 진입 / 또는 별도 정리 카드 |
| 시연 가이드 (TG-1) | D-4 audit 결과 활용 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|------|--------|------|
| **CL-2** | CL-1 머지 후 / 사용자 본문 | 코드 정리 (회귀 검증 의무) |
| **CL-3** | CL-1 / CL-2 머지 후 | 의존성 정리 (requirements / package) |
| **TG-1** | CL-1 ~ CL-3 머지 후 | 시연 가이드 (D-4 audit + 자료 인덱스 활용) |
| **I-1** | TG-1 머지 후 | 면접 답변 시뮬 (KARPATHY §6 + INTERVIEW + Top 10) |

---

## ADR 의존성

| ADR | 인용 위치 |
|-----|-----------|
| 0011 D-1 보류 | 양면 정책 ADR 형식 시작 |
| 0014 D-9 보류 | 양면 정책 ADR 형식 일관성 |
| 0020 D-4 Audit | D-4 패턴 일관성 (자료 동시 갱신 의무) |
| 0021 P-1 메타 | 메타 ADR 영역 / 자료 인덱스 본질 |
| 0022 V-1 검증 | 누적 자료 검증 (의문 7건) |
| 0023 V-1b KARPATHY | KARPATHY_MAPPING §1 재작성 / V-1b 결과 |
| **0024 (본 ADR)** | CL-1 자료 인덱스 정착 (docs README 3건 / pre-existing 14건 분류) |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|------|------|------|
| 2026-05-07 | v1 | 초기 Accepted (docs/README.md / docs/agent-capability-audit/README.md / docs/adr/README.md 신규 + pre-existing 14건 분류 본문 + 영구 보류 3건 + 양면 정책 14 ADR (0011-0024) 정립) |
