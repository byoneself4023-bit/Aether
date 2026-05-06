# D9_PRE_CHECK — RAG 진단 (D-9 진입 본질 명확화)

> **카드**: D-9 진단 전용 (코드 변경 0 / git 작업 0)
> **작성일**: 2026-05-06
> **본질**: 시나리오 A에서 D-9 (RAG 데이터 정제) 카드의 본질 적합도 검증 + 분기 결정
> **결론 한 줄**: **분기 3 확정** — RAG 사용처 약함 + 정제 대상 부재 (이미 정형 4 md). D-9 보류 + D-8 (평가) 우선순위 격상 권고.

---

## §1 RAG 사용처 분석

### §1.1 rag.py 본문 (`llm-service/app/services/rag.py` 617 LOC)

| 함수 | 라인 | 책임 |
|---|---|---|
| `_get_embedding()` / `_get_query_embedding()` | 40-67 | Gemini `gemini-embedding-001` (768차원) — `retrieval_document` / `retrieval_query` 분리 |
| `_load_knowledge_base()` | 91-113 | `app/data/knowledge_base/*.md` 마크다운 로드 |
| `_split_document()` | 116-198 | ## 헤더 분할 + 긴 섹션 청킹 (chunk_size 1000 / overlap 200) |
| `init_vectorstore()` | 253-308 | lifespan startup에서 자동 초기화 — 컬렉션 비어있으면 임베딩 + 주입 |
| `query()` | 332-366 | 유사 문서 검색 (k=3 default) |
| `build_optimized_context()` | 422-483 | 토큰 제한 고려 컨텍스트 빌드 (max 3000 chars) |
| `query_with_llm()` | 486-532 | RAG 검색 + LLM 답변 생성 (prompt_registry `rag_user` / `rag_system`) |

### §1.2 ReAct agent에서 RAG 호출 위치 / 빈도

**RAG 호출 0건**:
- `agents/react_agent.py:27-71` ReActAgent — `_TOOL_NAME_TO_FIELD` 4 도구만 (`analyze_portfolio_tool` / `explain_risk_tool` / `summarize_backtest_tool` / `get_recommendation_tool`)
- `agents/portfolio_tools.py:9-14` import — `services/llm.py`에서 4 함수만 (`analyze_portfolio` / `explain_risk` / `get_recommendation` / `summarize_backtest`)
- **ReAct agent에서 RAG 호출 함수 / 도구 등록 0건 확정**

### §1.3 /api/chat 흐름에서 RAG 결과 사용 방식

`routers/chat.py:191-214` 분석 결과:

```python
# 종목이 없으면 RAG 질문으로 처리
if len(tickers) < 2:
    rag_result = query_with_llm(wrapped_message, k=3)
    return ChatResponse(answer=rag_result["answer"], sources=...)
```

**조건부 분기**:
- 티커 ≥ 2개 → ReAct agent (4 도구 호출, RAG X)
- 티커 < 2개 → RAG fallback (`query_with_llm`)
- **RAG는 "종목 없는 일반 금융 질문" fallback 한정** — 주 흐름 X

### §1.4 /api/rag 라우터 사용처

`routers/rag.py` 5 endpoints:
- `POST /api/rag/query` — RAG 직접 검색
- `POST /api/rag/init` — 벡터스토어 강제 재로드
- `GET /api/rag/status` — 상태 확인
- `GET /api/rag/sources` — 소스 목록

**frontend 사용처**: F-1 검증 + D-2/D-3 Phase 1에서 frontend `lib/api/llm.ts` 호출 0건 확인. `/api/rag/*` dead code 가능성 (외부 API 직접 호출용 노출).

---

## §2 RAG 입력 데이터 명확화

### §2.1 Qdrant 컬렉션 현재 상태

```bash
curl http://localhost:6333/collections
{"result":{"collections":[]},"status":"ok"}

curl http://localhost:6333/collections/aether_knowledge
{"status":{"error":"Not found: Collection `aether_knowledge` doesn't exist!"}}
```

**Qdrant 컬렉션 0건 / aether_knowledge 미존재**. T-6 머지됐지만 Qdrant 미사용 중.

### §2.2 임베딩 대상 텍스트 출처

**정적 4 md 파일** (`llm-service/app/data/knowledge_base/`):

| 파일 | LOC |
|---|---|
| `investment_strategies.md` | 185 |
| `portfolio_theory.md` | 82 |
| `risk_management.md` | 130 |
| `sector_analysis.md` | 157 |
| **합계** | **554** |

**출처 본질**:
- 사용자가 직접 작성한 **정적 FAQ** (Feb 17 작성)
- 외부 보고서 / 자동 수집 / 사용자 입력 **모두 X**
- 이미 정형 마크다운 구조 (## 헤더 + 본문)

### §2.3 데이터 주입 방식

- **자동 lifespan startup** (`app/main.py:36` `init_vectorstore()`)
- 컬렉션 비어있으면 → md 파일 로드 → 임베딩 → 주입
- **현재 chromadb 사용 중** (`config.py: vector_store="chromadb"` default + `data/chroma/chroma.sqlite3` 존재)

### §2.4 정제 대상 식별

| 정제 후보 | 결과 |
|---|---|
| 비정형 텍스트 → 정형 | **X** (이미 정형 md) |
| 노이즈 제거 (광고 / 중복 / 깨짐) | **X** (사용자 직접 작성, 노이즈 0) |
| 중복 청크 제거 | **X** (## 헤더 분할 + chunk_size 친화) |
| 메타데이터 정규화 | **X** (이미 source / title / chunk_index 포함) |
| 다국어 정제 | **X** (한국어 단일) |
| HTML / PDF / 표 처리 | **X** (마크다운 단일 포맷) |

**정제 대상 0건 확정**. D-9 (정제) 본질 적합도 ★ (최저).

---

## §3 시나리오 A 본질 적합도 평가

### §3.1 사용자 0명 = 정제 본능 적합도

- 시나리오 A 정의: 기술 데모 / 면접용 / 사용자 0명 (SCENARIO.md 라인 16-21)
- 정제 본능 = 비정형 데이터 → 정형 / 노이즈 제거 / 다국어 / PDF 등
- 시나리오 A에서 데이터 발생 X = **정제 대상 발생 X** = 정제 본능 부적합

### §3.2 시연 시그널 부합도

- D-9 시연 = "정제 후 검색 정확도 향상" 메시지 → **부재 데이터** = 시연 X
- 대안 시그널 후보:
  - **D-7 (Chunking 정책)**: 정적 4 md 청킹 전략 튜닝 → ★★ (시연 가능)
  - **D-8 (RAG 평가)**: relevance / hit rate / answer quality 메트릭 → **★★★** (시연 직격)
  - **D-5 (RAG 활용 차별화)**: ReAct agent에 RAG 도구 추가 → ★★★ (시그널 강화)

### §3.3 면접 답변 가능성

| 질문 | 답변 가능성 |
|---|---|
| "왜 RAG 도입?" | ✓ — 4 도구로 못 풀리는 일반 금융 질문 fallback |
| "왜 Qdrant 어댑터?" | ✓ — T-6 / ADR 0009 (시나리오 B 진입 시 분산 backend 전환) |
| "어떤 데이터 정제?" | **✗** — 정제 대상 부재 (정적 md 4건만, 이미 정형) |
| "데이터 정제 안 한 이유?" | ✓ — 시나리오 A 본질 X (PRINCIPLES 6번 미적용 결정 명시) |

**면접 답변 가능 — 단 "정제했다" 답변 X** (정제 대상 부재). "정제 안 한 이유" 답변 = 시니어 시그널 강함.

---

## §4 D-9 진입 결정 분기

### §4.1 분기 1 (RAG 입력 명확 → D-9 진행)

**X** — 정제 대상 부재 (정적 4 md 이미 정형).

### §4.2 분기 2 (입력 모호 → D-9 재정의)

**X** — 입력 명확함 (출처 / 구조 / 주입 방식 모두 명시). 모호 X.

### §4.3 분기 3 (RAG 사용처 약함 → D-9 보류 + D-7/D-8 우선)

**✓ 채택**:
- ReAct agent에서 RAG 호출 0건
- /api/chat에서 티커 < 2 fallback 한정
- /api/rag/* 라우터 frontend 호출 0건
- 정제 대상 부재 (정적 md 4건)

### §4.4 결정

**분기 3 확정**:
1. **D-9 보류** — ADR 0014 작성 (보류 결정 + 시나리오 B 트리거 명시, ADR 0011 형식 인용)
2. **D-8 (RAG 평가) 우선순위 격상** — 정적 4 md 기반 evaluation 메트릭 (relevance@k / answer quality / hallucination) 정착 = 시연 시그널 직격
3. **D-7 (Chunking 정책)** — 차순위 (현재 chunk_size 1000 / overlap 200 default — 튜닝 카드 가능)
4. **D-5 (RAG 활용 차별화)** — ReAct agent에 RAG 도구 추가 검토 (T-1c 후속 카드 후보)

**사용자 보고 의무** (G3 Done Definition): D-9 본능 재정의 = ADR 0014 (D-9 보류) 카드 진입 권고.

---

## §5 면접 답변 시나리오 (Why → How → What)

### §5.1 Why (왜 RAG / 왜 정제 안 했나)

> "Aether 시나리오 A는 사용자 0명 기술 데모입니다. RAG는 ReAct agent의 4 도메인 도구 (포트폴리오 분석 / 리스크 / 백테스트 / 추천)로 답변 불가능한 **일반 금융 지식 질문 fallback**으로 도입했습니다. `/api/chat`에서 티커 < 2개일 때만 RAG 호출 분기됩니다."

### §5.2 How (어떻게 정제?)

> "정제 안 했습니다. 그 이유:
> - 입력 데이터 = 정적 마크다운 4 파일 (554 LOC, 사용자 직접 작성)
> - 이미 ## 헤더 / 청크 구조 적용 = 정형 상태
> - 시나리오 A에서 비정형 데이터 발생 X (사용자 0명)
> 
> 정제 본능은 시나리오 B (실 사용자 + PDF / HTML / 다국어 발생) 진입 시점 트리거 명시 (ADR 0014 후보)."

### §5.3 What (무엇을 정제 안 했나)

> "정제 후보 6 영역 모두 시나리오 A 부적합:
> 1. 비정형 → 정형: 이미 정형 md
> 2. 노이즈 제거: 사용자 직접 작성 = 노이즈 0
> 3. 중복 청크: ## 헤더 분할 = 중복 X
> 4. 메타 정규화: source / title / chunk_index 이미 포함
> 5. 다국어: 한국어 단일
> 6. HTML / PDF / 표: 마크다운 단일 포맷
> 
> 대신 D-8 (RAG 평가 메트릭)을 우선 정착했습니다 — relevance@k / answer quality / hallucination rate 기반 검증."

### §5.4 Aether 시나리오 A 답변 가능 여부

**Yes — 시니어 시그널 강함**:
- PRINCIPLES 6번 (미적용 결정 + 트리거 명시) 직격 적용
- "정제했다" 거짓 답변 회피 + "정제 안 한 이유" 답변 = 본질 적합 판단 입증
- D-8 우선 정착 = "어떻게 측정?" 시그널 = 시니어 본능

---

## §6 후속 카드 권고 (D-9 보류 + 우선순위 재정렬)

| 카드 | 본질 | 우선순위 |
|---|---|---|
| **ADR 0014 (D-9 보류)** | RAG 데이터 정제 보류 결정 + 시나리오 B 트리거 명시 (ADR 0011 형식) | **최우선** |
| **D-8 (RAG 평가)** | relevance@k / answer quality / hallucination 메트릭 정착 | **격상** (D-9 → D-8) |
| **D-7 (Chunking 정책)** | chunk_size / overlap 튜닝 + 평가 (D-8 결과 기반) | D-8 후 |
| **D-5 (RAG 활용 차별화)** | ReAct agent에 RAG 도구 추가 (4 → 5 도구) | D-7 후 |
| D-6 / D-4 / P-1 / I-1 | (기존 순서 유지) | 후순위 |

---

## §7 검증 메타 (5 가드 + WORK_PATTERNS)

### §7.1 5 가드 적용

- **G1 본질 트리거**: 진단 중 "RAG 호출 0건 + Qdrant 컬렉션 0건" 발견 시 즉시 분기 3 강제 ✓
- **G2 Reversibility**: Type 1 (산출 1 파일 / git 작업 0) ✓
- **G3 Done Definition**: §1-§5 모두 채움 + 분기 3 결정 + 면접 답변 ✓
- **G4 Round Cap**: 1 라운드 완료 ✓
- **G5 First Principle**: "정착된 카드 ≠ 본질 적합 카드" 직격 증명 ✓

### §7.2 WORK_PATTERNS 누적 문제 매칭

| 문제 | 본 진단 매칭 |
|---|---|
| 문제 4 (응답 schema 키 가설) | RAG 응답 키 (`answer` / `sources`) 실측 (chat.py:194-207) |
| 문제 6 (호출 위치 가설) | RAG 호출 5 위치 모두 grep 실측 (chat.py + rag.py + main.py) |
| 문제 13 (외부 SDK 응답 구조) | Qdrant `/collections` API 실측 — 0건 확인 |
| 문제 19 (sync 누락) | T-6 머지됐지만 default `chromadb` 미전환 — sync 누락 패턴 |

---

## §갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-06 | 초기 작성 — 분기 3 확정 + ADR 0014 (D-9 보류) + D-8 우선순위 격상 권고 |

**한 문장**: D-9 진입 본질 진단 결과 정제 대상 부재 + RAG 사용처 약함 — D-9 보류 ADR + D-8 (평가 메트릭) 우선순위 격상이 시나리오 A 본질에 적합한 시니어 결정.
