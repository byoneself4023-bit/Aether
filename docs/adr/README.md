# ADR 인덱스 (CL-1 / 양면 정책 14 ADR)

> **본질**: ADR 23건 카테고리별 인덱스. Top 10 카드 (0001-0010) + D 시리즈 (0011-0020) + 메타 / V / CL 시리즈 (0021-0024). 양면 정책 = 정착 결정 vs 보류 결정 vs 메타 / 정리 결정.
> **카드**: CL-1 (자료 인덱스 / ADR 0024)
> **갱신일**: 2026-05-07

---

## §1 ADR 23건 카테고리별 인덱스

### Top 10 카드 (ADR 0001-0010)

Aether 시작 단계 / Top 10 카드 영역. Phase 1-2 사전 분석 + 카드 본문 영역.

| # | ADR | 카드 | 본질 |
|---|-----|------|------|
| 1 | [0001](0001-microservice-split.md) | H-1 | Microservice Split (4 서비스 분리 / Top 10) |
| 2 | [0002](0002-module-boundaries.md) | H-1c | Module Boundaries (routers → services → 외부) |
| 3 | [0003](0003-prompt-registry-policy.md) | H-4 | Prompt Registry (단일 진입점 / 코드 상수 f-string 금지) |
| 4 | [0004](0004-auth-and-tracing.md) | H-10 + L-7 | Auth + Tracing (HS512 통일 — F-1a 시점 v2) |
| 5 | [0005](0005-langgraph-adoption.md) | T-1a | LangGraph 도입 |
| 6 | [0006](0006-react-pattern.md) | T-1b | ReAct 패턴 (LangChain ChatGoogleGenerativeAI) |
| 7 | [0007](0007-genai-sdk-migration.md) | H-6 | google-genai 1.74 마이그레이션 |
| 8 | [0008](0008-mcp-server-adoption.md) | T-2 | MCP Server (4종 stdio transport) |
| 9 | [0009](0009-qdrant-migration.md) | T-6 | Qdrant 마이그레이션 (vector_store 어댑터) |
| 10 | [0010](0010-t3-multi-agent-deferred.md) | C-1 | T-3 Multi-Agent 보류 (양면 정책 시작) |

### D 시리즈 + T-6b (ADR 0011-0020)

D-1 ~ D-9 카드 영역 + T-6b Qdrant default. 시나리오 A 본질 결정 + 운영급 + RAG 영역.

| # | ADR | 카드 | 본질 |
|---|-----|------|------|
| 11 | [0011](0011-functional-trim-deferred-features.md) | D-1 | 본질 X 4건 보류 (MLflow / drift / weight / RAG 정제) |
| 12 | [0012](0012-production-grade-decisions.md) | D-2 | 운영급 (CORS 명시 / API 키 검증 / cache LRU) |
| 13 | [0013](0013-frontend-page-decomposition.md) | D-3 | Frontend 페이지 분리 (200 LOC 임계) |
| 14 | [0014](0014-rag-data-cleaning-deferred.md) | D-9 | RAG 정제 보류 (분기 3 / 정적 4 md / 정형) |
| 15 | [0015](0015-rag-evaluation-metrics.md) | D-8 | RAG 평가 자체 4 메트릭 (ragas 미도입) |
| 16 | [0016](0016-qdrant-default-migration.md) | T-6b | Qdrant default + chromadb fallback (_EMBED_DIM 768→3072 정정) |
| 17 | [0017](0017-rag-chunking-policy.md) | D-7 | RAG Chunking grid search (9 조합 / chunk_size=500 / overlap=300) |
| 18 | [0018](0018-react-agent-rag-tool-integration.md) | D-5 | ReAct + RAG 통합 (5번째 도구 search_knowledge_base) |
| 19 | [0019](0019-streaming-sse.md) | D-6 | Streaming SSE (POST /api/chat/stream 신규 endpoint) |
| 20 | [0020](0020-d4-audit-cleanup-decisions.md) | D-4 | Audit 종합 (14 카드 / 18 누적 문제 17 해소) |

### 메타 / V / CL 시리즈 (ADR 0021-0024)

P-1 시점 메타 정착 + V 시리즈 검증 + CL-1 자료 정리.

| # | ADR | 카드 | 본질 |
|---|-----|------|------|
| 21 | [0021](0021-meta-patterns-and-karpathy-mapping.md) | P-1 | 메타 패턴 (PRINCIPLES 8/9/10) + KARPATHY 매핑 (76→87점) |
| 22 | [0022](0022-cumulative-asset-verification.md) | V-1 | 누적 자료 검증 (의문 7건 / 부족 5 + 부분 충분 2) |
| 23 | [0023](0023-karpathy-mapping-rewrite.md) | V-1b | KARPATHY_MAPPING §1 재작성 (영상 9 ↔ Aether) + LECTURE 단어 위생 |
| 24 | [0024](0024-asset-cleanup.md) | CL-1 | 자료 인덱스 정착 (본 ADR / docs README 3건 + pre-existing 14건 분류) |

---

## §2 양면 정책 14 ADR (정착 vs 보류 vs 메타)

### 정착 결정 (7건) — 시나리오 A 본질 적합 + 운영급

| ADR | 카드 | 정착 본문 |
|-----|------|----------|
| 0012 | D-2 | CORS 명시 정책 + API 키 이중 안전장치 + cache LRU |
| 0013 | D-3 | Frontend 페이지 분리 (200 LOC 임계) |
| 0015 | D-8 | RAG 평가 자체 4 메트릭 (relevance@k / precision@k / latency / cost) |
| 0016 | T-6b | Qdrant default + chromadb fallback + _EMBED_DIM 정정 |
| 0017 | D-7 | RAG Chunking 정책 (chunk_size=500 / overlap=300) |
| 0018 | D-5 | ReAct + RAG 통합 (5 도구 자율 판단) |
| 0019 | D-6 | Streaming SSE (POST /api/chat/stream) |

### 보류 결정 (3건) — 시나리오 B 트리거

| ADR | 카드 | 보류 본문 / 트리거 |
|-----|------|--------------------|
| 0010 | C-1 | T-3 Multi-Agent 보류 (Houseman Phase 7-12 도메인 검증) |
| 0011 | D-1 | 본질 X 4건 (MLflow / drift / weight / RAG 정제) — 시나리오 B 진입 |
| 0014 | D-9 | RAG 정제 보류 (정적 4 md / 이미 정형) — 시나리오 B + 동적 데이터 |

### 메타 / 검증 결정 (3건) — 본질 추적

| ADR | 카드 | 메타 본문 |
|-----|------|----------|
| 0020 | D-4 | Audit 종합 (14 카드 결과 / 18 누적 문제 정리) |
| 0021 | P-1 | 메타 패턴 (귀납) + 카파시 영역 (연역) 통합 |
| 0022 | V-1 | 누적 자료 검증 (의문 7건 / V-1b 트리거) |
| 0023 | V-1b | KARPATHY §1 재작성 + LECTURE 단어 위생 (양면 정책 13 ADR) |

### 정리 결정 (1건) — 자료 인덱스

| ADR | 카드 | 정리 본문 |
|-----|------|----------|
| 0024 | CL-1 | 자료 인덱스 정착 (docs README 3건 + pre-existing 14건 분류) |

---

## §3 ADR 형식

ADR 0011 / 0014 / 0020 / 0021 / 0022 / 0023 형식 일관성 (양면 정책 ADR 패턴):

```
# ADR NNNN — [제목] ([카드ID])

- **상태**: Accepted / Proposed / Deferred
- **일자**: YYYY-MM-DD
- **관련 카드**: [카드ID]
- **결정 근거**: [출처 명시]

## 컨텍스트
[본질 상황 2-3 문단]

## 결정 (N 분기 추적)
### 분기 1: [영역] — **A/B/C 채택**
[옵션 본문 + 선택 사유]
... (N 분기)

## Decision
[결정 산출물 본문 / 변경 대상 자료 명시]

## 영향
### 시그널 강화 (+)
- [본질 가치]
### 트레이드오프 (−)
- [한계 / 비용]

## 미적용 영역 (시나리오 B 트리거)
| 영역 | 트리거 |
|---|---|

## 후속 카드
| 카드 | 트리거 | 본질 |
|---|---|---|

## ADR 의존성
| ADR | 인용 위치 |

## 갱신 이력
| 일자 | 버전 | 변경 |
```

---

## §4 ADR 갱신 정책

1. **결정 변경 시 v2 / v3** — 0004 (F-1a 시점 v2 / HS512 통일) 패턴. git log 추적 + 본문에 v2 명시.
2. **ADR 추가 시** — 본 README + docs/README.md + AGENTS.md §7 동시 갱신 의무.
3. **양면 정책 영역 변경 시** — §2 분류 갱신 의무. 정착 → 보류 / 보류 → 정착 영역 변경 = ADR v2 의무.
4. **카드 ID 영역** — 본 README §1 카테고리 영역 갱신. 카드 추가 = ADR 추가 + 본 README 갱신.

---

## §5 ADR 본질 진입 흐름

| 본질 | 진입 ADR |
|------|----------|
| 양면 정책 (정착 vs 보류) 시작 | 0010 (T-3 보류) |
| 시나리오 A 본질 결정 | 0011 / 0014 (보류) + 0015 / 0019 (정착) |
| 메타 패턴 + 카파시 영역 | 0021 |
| 누적 자료 검증 영역 | 0022 / 0023 |
| 자료 인덱스 정착 영역 | 0024 (본 카드) |

---

> **한 문장**: ADR 23건 (0001-0023) + 0024 신규 = 양면 정책 14 ADR. 정착 7 + 보류 3 + 메타 4 + 정리 1. 본 인덱스 = 6개월 후 본인 답 가능 정착 (PRINCIPLES 원칙 5 / 결정 근거 추적).
