# ADR 0018 — ReAct agent에 RAG 도구 통합 (D-5)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: D-5 (AI Agent 자율 판단 본능 진화)
- **결정 근거**: ADR 0005 (LangGraph) + 0006 (ReAct) + ADR 0011 형식 + ADR 0010 (T-3 보류) 일관성

---

## 컨텍스트

ReAct agent 4 도구 (analyze / risk / backtest / recommendation) 자율 호출 / RAG 미통합. `/api/chat`에서 티커 X / O 영역 분리 (티커 < 2 → RAG fallback / 티커 ≥ 2 → ReAct).

D-5는 5번째 도구 (`search_knowledge_base`) 추가 — 사용자 의도 영역 분리 X / ReAct 자율 판단 본능 진화.

---

## 결정

### 1. search_knowledge_base 도구 추가 (`rag_tools.py` 신규)

도메인 분리 본능 — `portfolio_tools.py` (수치 분석 4) ↔ `rag_tools.py` (지식 검색 1).

```python
@tool
def search_knowledge_base(question: str) -> dict[str, Any]:
    """투자 도메인 지식 검색 (포트폴리오 이론 / 리스크 관리 / 투자 전략 / 섹터 분석)."""
    result = query_with_llm(question=question, k=3, include_sources=True)
    return {"answer": ..., "sources": ...}
```

### 2. tool_registry 5 도구 등록 (`tools.py:_register_default_tools`)

기존 4 + `search_knowledge_base` = 5.

### 3. react_agent `_TOOL_NAME_TO_FIELD` 매핑 갱신

신규 매핑: `"search_knowledge_base": "knowledge_sources"` (기존 4 매핑 무수정).

### 4. AnalysisResponse `knowledge_sources` Optional 필드 추가

```python
class AnalysisResponse(BaseModel):
    ...
    knowledge_sources: dict | None = Field(default=None, ...)  # D-5
```

기존 6 필드 무수정 + Optional 1 필드 추가 = 응답 호환성 보장.

### 5. ReAct system prompt v1.1 등록

5 도구 영역 + 판단 규칙 명시. v1.0 보존 (회귀 시 즉시 롤백 가능). `react_agent.py`가 v1.1 호출 default.

### 6. chat.py fallback 환경변수 토글

```python
rag_fallback_direct = os.getenv("RAG_FALLBACK_DIRECT", "true").lower() == "true"
```

- default `true`: 기존 fallback 흐름 보존 (안전 점진 전환)
- `false`: 티커 < 2 영역도 ReAct 5 도구 자율 판단

---

## 영향

### 시그널 강화 (+)

- **사용자 의도 자율 판단 본능 정착**: 영역 분리 X → AI Agent 본질 직격
- **양면 정책 8 ADR 정립**: 0011 / 0012 / 0013 / 0014 / 0015 / 0016 / 0017 / **0018**
- **티커 X / O 흐름 통일** (`RAG_FALLBACK_DIRECT=false` 시점)
- **조합 질문 가능**: ReAct가 RAG + 분석 도구 조합 호출 (예: "VaR 정의 + 포트폴리오 분석" → search_knowledge_base + analyze)
- **점진 전환 본능**: default true → 안전 보존, env 토글로 신 흐름 활성화

### 트레이드오프 (−)

- LLM 입력 token ~50-100 증가 (도구 description 1개)
- 5 도구 자율 판단 회귀 가능성 ↑ (잘못된 도구 선택 — system prompt + 3 E2E 검증으로 완화)

---

## E2E 결과 (실 측정)

| 시나리오 | 입력 | 결과 |
|---|---|---|
| 1. 티커 X (default fallback) | "샤프 비율이란?" | HTTP 200 / answer 704 chars / **3 sources** |
| 2. 티커 O | "AAPL, MSFT, GOOGL 분석해줘" | HTTP 200 / answer 826 chars / portfolio_data 3 weights |
| 3. 조합 (티커 O + 도메인) | "VaR이 뭐고 AAPL, MSFT 포트폴리오 분석해줘" | HTTP 200 (12.8s) / answer 798 chars / portfolio_data 2 weights |

**3 시나리오 모두 PASS** — ChatResponse 응답 구조 보존 (frontend 영향 0).

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| Hybrid Search (BM25 + Vector) | 우대 요건 / 시나리오 B 진입 |
| 도구 6+ 확장 (Multi-Agent 본격) | T-3 보류 일관성 (ADR 0010) — Multi-Agent 영역 |
| 도구 호출 비용 추적 (Token Tracker 본격) | 시나리오 B 진입 |
| 도구 실패 자동 재시도 | 안정성 본격 시점 |
| `RAG_FALLBACK_DIRECT=false` default 전환 | 5 도구 자율 판단 회귀 0 검증 후 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **D-6** | D-5 머지 후 | Streaming 차별화 |
| **D-4** | D-6 후 | 코드 Audit / 종합 정리 |
| **F-N (Hybrid Search)** | 시나리오 B 진입 | BM25 + Vector |
| **F-N (도구 6+)** | T-3 트리거 | Multi-Agent (ADR 0010 일관성) |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (5 도구 자율 판단 + 양면 정책 8 ADR 정립 + ReAct system prompt v1.1 + chat.py fallback 환경변수 토글). 3 E2E 시나리오 PASS. |
