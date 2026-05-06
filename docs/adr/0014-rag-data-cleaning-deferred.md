# ADR 0014 — RAG 데이터 정제 보류 결정 (D-9)

- **상태**: Accepted (보류 결정)
- **일자**: 2026-05-06
- **관련 카드**: D-9 / D9_PRE_CHECK (`docs/agent-capability-audit/D9_PRE_CHECK.md`)
- **결정 근거**: D9_PRE_CHECK §3.3 + §4.4 분기 3 + PRINCIPLES 패턴 6 ("미적용 결정 = 명시한 결정만큼 강한 시그널") + ADR 0011 형식 인용

---

## 컨텍스트

D-9 (RAG 데이터 정제) 카드 진입 전 본질 진단 결과 (`D9_PRE_CHECK.md`):

| 진단 영역 | 결과 |
|---|---|
| RAG 사용처 | **약함** — ReAct agent 호출 0건 / `/api/chat`에서 티커 < 2 fallback 한정 |
| RAG 입력 데이터 | **정적 4 md** (554 LOC, `app/data/knowledge_base/`) — 이미 정형 |
| Qdrant 컬렉션 | **0건** (현재 chromadb 사용 중, T-6 어댑터 미전환) |
| ReAct 4 도구 | analyze_portfolio / explain_risk / summarize_backtest / get_recommendation — RAG 도구 0건 |

D-9의 본질 ("데이터 정제")는 **시나리오 A 부적합** — 정제 대상 자체 부재. PRINCIPLES 패턴 6 직격 적용으로 보류 결정 ADR 형식 정착.

---

## 결정

### 1. D-9 (RAG 데이터 정제) 보류

본 카드 머지 시점부터 D-9 카드는 **시나리오 B 진입 트리거 발생 시까지 보류**. 본 카드는 보류 결정 자체를 시그널로 정착.

### 2. 정제 후보 6 영역 모두 시나리오 A 부적합 명시

| 정제 후보 | 시나리오 A 적합도 |
|---|---|
| 비정형 → 정형 | **X** (이미 정형 md) |
| 노이즈 제거 (광고 / 중복 / 깨짐) | **X** (사용자 직접 작성, 노이즈 0) |
| 중복 청크 제거 | **X** (## 헤더 분할 + chunk_size 친화) |
| 메타데이터 정규화 | **X** (이미 source / title / chunk_index 포함) |
| 다국어 정제 | **X** (한국어 단일) |
| HTML / PDF / 표 처리 | **X** (마크다운 단일 포맷) |

### 3. 우선순위 재정렬

D-9 → **D-8** (RAG 평가 메트릭) **격상** → D-7 (Chunking 정책) → D-5 (RAG 도구 추가).

### 4. 진입 트리거 (재활성화 조건)

다음 중 하나 충족 시 D-9 후속 카드 진입:

- **트리거 1 — 시나리오 B 진입**: 실 사용자 1+ 명 + 비정형 데이터 발생 (PDF / HTML / 사용자 입력 텍스트 등)
- **트리거 2 — Houseman Phase 7-12 도메인 검증**: knowledge_base 확장 + 외부 데이터 통합 시점
- **트리거 3 — 외부 포맷 통합**: PDF 보고서 / HTML 스크래핑 / 다국어 데이터 도입 시점

---

## 영향

### 시그널 강화 (+)

- PRINCIPLES 패턴 6 직격: 보류 결정 + 트리거 명시 = 시니어 의사결정 시그널
- 면접 답변 자료: "정제 안 한 이유" 답 가능 = 본질 적합 판단 입증
- ADR 0011 (D-1 보류) + 0014 (D-9 보류) = 보류 정책 본능 정착

### 트레이드오프 (−)

- 공고 우대 "RAG 데이터 정제" 매칭 일부 어긋남
- 단 답 가능 시그널 강함 ("왜 정제 안 했나" → "시나리오 A 정제 대상 부재 + 시나리오 B 트리거 명시")로 상쇄

### Reversibility (Type 1)

- 코드 변경 0 / 문서 1 파일 신규 + 1 갱신 + 1 staging
- git revert 1줄로 즉시 롤백 가능

---

## 부록 — chromadb sync 미전환 본질 (T-6b 후속 카드 후보)

D9_PRE_CHECK §1.1 진단 중 발견 사항:

| 발견 | 상세 |
|---|---|
| T-6 (Qdrant 어댑터) 머지 상태 | 머지 완료 (commit `64620dd`) |
| `vector_store` default | `chromadb` (`llm-service/app/config.py:33`) |
| Qdrant 컬렉션 | 0건 (`{"collections":[]}`) |
| chromadb 데이터 | `llm-service/data/chroma/chroma.sqlite3` 존재 — 사용 중 |
| 패턴 매칭 | WORK_PATTERNS 문제 19 (sync 누락 패턴) — F-1a HS512 sync 누락과 동일 패턴 |

본 발견은 **본 ADR 0014 결정 외 사항**으로, 후속 카드 후보 `T-6b` 트리거 명시:

| 트리거 | 본질 |
|---|---|
| **D-8 (RAG 평가) 진입 시점** | Qdrant 평가 환경 통합 의도 발생 시 default 전환 권고 |
| **별도 카드 분리** | 시나리오 B 진입 시 분산 backend 전환 시점 |

본 부록은 sync 누락 패턴 추적 자료 — 본 ADR에서 chromadb / Qdrant 전환 결정 X (별도 카드 본질).

---

## 후속 카드

| 카드 | 트리거 | 우선순위 |
|---|---|---|
| **D-8** (RAG 평가 메트릭) | ADR 0014 머지 후 즉시 | **격상** (D-9 → D-8) |
| **T-6b** (chromadb → Qdrant 전환) | D-8 진입 시점 또는 별도 | 조건부 |
| **D-7** (Chunking 정책 튜닝) | D-8 머지 후 | D-8 결과 기반 |
| **D-5** (ReAct에 RAG 도구 추가) | D-7 머지 후 | 차별화 |
| **F-N (시나리오 B 정제)** | 트리거 1/2/3 발생 | 조건부 (D-9 재활성화) |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-06 | v1 | 초기 Accepted (D-9 보류 결정 + 정제 6 영역 부재 명시 + chromadb sync 부록 + 시나리오 B 트리거 3건). ADR 0011 형식 적용. |
