# Aether Top 10 진화 회고 (EVOLUTION.md)

> Top 10 카드 진행 결과 회고. 면접 / 이력서용 한 줄 답변 + 카드별 Before/After + 시스템 진화 흐름. 메모리 #20 (Top 10 종료 시 정리 약속) 충족.
>
> **위치**: `docs/agent-capability-audit/EVOLUTION.md`
> **작성 시점**: 2026-05-05 (Top 10 9.5/10 + T-3 보류 결정)
> **참조**: `docs/agent-capability-audit/SCENARIO.md` (시나리오 A) + `docs/agent-capability-audit/TECH_DECISIONS.md` (기술 결정 근거) + `docs/agent-capability-audit/PRINCIPLES.md` (시니어 판단 패턴) + `docs/adr/` (10건)

---

## §1. 시스템 진화 흐름 (수치 비교)

| 측면 | Before (2026-04-28) | After (2026-05-05, Top 10 종료) | 증분 |
|---|---|---|---|
| 백엔드 API 라우터 수 | 1 (chat) | 32 (chat / rag / portfolio / risk / backtest / drift / ...) | +31 |
| 테스트 합산 | ~50 | 494 (llm 287 + portfolio 219 + auth 70 — T-6 기준) — 머지 후 555 예상 | +444 |
| ADR 수 | 1 (0001 microservice-split) | 10 (0001-0010, 0009 PR #14 미머지, 0010 본 PR) | +9 |
| 안전장치 (가드 / 검증 / 게이트) | 0 | 14건 (5 가드 + PR 게이트 4 + WORK_PATTERNS A-G 7) | +14 |
| 등록 프롬프트 수 | 0 | 8 (v1.0) — registry 단일 진입점 | +8 |
| 자기 일관성 패턴 (WORK_PATTERNS) | 0 | 5종 + F-패턴 (검증+분기+머지) | +6 |
| 시니어 판단 패턴 (PRINCIPLES) | 0 | 7개 (5번까지 v4 + 6번/7번 v5) | +7 |

→ **시스템이 *"카드 누적"* X *"진화 트리"* 로 자라남.** 매 카드가 다음 카드의 안전장치를 박는 구조 (e.g., H-7 PR 게이트 → T-1b 회귀 자동 감지 → T-2 MCP Spike 가드).

---

## §2. Top 10 카드 회고 (Before / After / 안전장치 / 패턴 / 한 줄)

### 1. H-4 — Prompt registry 확장

| 항목 | 내용 |
|---|---|
| Before | 코드 상수 f-string으로 LLM 프롬프트 박힘. 새 프롬프트 = 코드 변경 |
| After | `prompt_registry.get(name, version)` 단일 진입점. 8 프롬프트 v1.0 등록 |
| 안전장치 | 환경변수 `PROMPT_VERSION_<NAME>` 런타임 선택 (rollback) |
| 자기 일관성 패턴 | 패턴 1 (Lazy Init Singleton — `get_registry()`) |
| 채용 어필 한 줄 | *"프롬프트 자체를 자산으로 박음 — 코드 변경 없이 버전 전환 + A/B 테스트 가능"* |

### 2. H-1 — 지배 숫자 정리

| 항목 | 내용 |
|---|---|
| Before | AGENTS.md §7 지배 숫자가 카드별로 다른 위치에 흩어짐 |
| After | §7 단일 표 + 변경 시 본 § + 인용 위치 동시 갱신 의무 박음 |
| 안전장치 | CLAUDE.md §2 "AGENTS.md 갱신 자체 검증" — 카드별 갱신 의무 |
| 자기 일관성 패턴 | 패턴 4 (옵션 비교 + 명시 결정) |
| 채용 어필 한 줄 | *"지배 숫자 한 곳에 박음 + 카드별 갱신 자동 검증 = 문서가 코드만큼 신뢰 가능한 자산"* |

### 3. H-7 — PR 게이트 도입

| 항목 | 내용 |
|---|---|
| Before | 회귀 검증 = 사람 의무, 매 PR 5-10분 |
| After | black / ruff / mypy / pytest cov 81% + tsc / eslint / vitest / build / markdownlint = 8종 자동 |
| 안전장치 | 1차 비차단 (기존 코드 보호) + 점진 강화 (H-7c/d/L-3 후속) |
| 자기 일관성 패턴 | 패턴 5 (옵션 B 2단 분해 — 도입 + 강화 분리) |
| 채용 어필 한 줄 | *"PR 게이트 8종 자동화로 회귀 사람 의무 → 0 — 시니어가 코드 리뷰에 본질 사고 집중 가능"* |

### 4. H-6 — google-genai SDK 마이그레이션

| 항목 | 내용 |
|---|---|
| Before | `google-generativeai` (legacy, FutureWarning 누적) |
| After | `google-genai` 1.74 (신 SDK) — 응답 어댑터 한 줄 + timeout sec→ms 변환 |
| 안전장치 | 마이그레이션 PoC + 응답 구조 직접 inspect |
| 자기 일관성 패턴 | 패턴 3 (응답 호환 어댑터 — `result.embeddings[0].values`) |
| 채용 어필 한 줄 | *"외부 SDK 마이그레이션 시 단위 변환 + 응답 구조 어댑터로 호출자 0 변경 — 운영 안전성 시그널"* |

### 5. H-10 + L-7 — X-Request-ID 분산 트레이싱

| 항목 | 내용 |
|---|---|
| Before | 요청 추적 불가 — 로그가 어느 호출에 속하는지 모름 |
| After | `X-Request-ID` ContextVar + httpx event_hooks로 자동 forward (llm → portfolio) |
| 안전장치 | `RequestLoggingMiddleware`가 ContextVar set + 모든 logger 자동 박음 |
| 자기 일관성 패턴 | 패턴 1 (Lazy Init — ContextVar 모듈 레벨) |
| 채용 어필 한 줄 | *"분산 트레이싱 X-Request-ID 박아 모든 서비스 로그를 한 흐름으로 추적 가능"* |

### 6. T-1a + H-2 — LangGraph 인프라

| 항목 | 내용 |
|---|---|
| Before | `chat.py` 절차적 4 호출 (analyze + risk + backtest + recommend) |
| After | `app/agents/` 신설 — `BaseAgent` 추상 + `ToolRegistry` + 4 도메인 도구 `@tool` 래핑 |
| 안전장치 | 인프라만 도입 (chat.py 미수정) — T-1b가 통합 시점 |
| 자기 일관성 패턴 | 패턴 5 (2단 분해 — 인프라 + 통합 분리) + ADR 0002 |
| 채용 어필 한 줄 | *"인프라 + 동작 변경 분리해서 회귀 위험 영역 분리 — T-1b 실패해도 T-1a 보호"* |

### 7. T-1b — ReAct 통합

| 항목 | 내용 |
|---|---|
| Before | chat.py 절차적 4 호출, 사람이 순서 박음 |
| After | `ReActAgent.run()` 1 호출, 모델이 4 도구 자율 판단. `USE_REACT_AGENT=false` env로 절차적 fallback |
| 안전장치 | env 토글 + 무한 루프 max_iterations=10 + ReAct 단위/통합 테스트 +12 |
| 자기 일관성 패턴 | 패턴 5 (환경변수 토글) + ADR 0006 |
| 채용 어필 한 줄 | *"의존성 있는 도구 분기에서 ReAct 자율 판단 + 무한 루프 차단 + 절차적 fallback 보존 = 운영 안전성"* |

### 8. H-1c — AGENTS.md §7 지배 숫자 표 정리

| 항목 | 내용 |
|---|---|
| Before | §7 지배 숫자 표에 중복 행 (테스트 합산 / SDK 버전 등) |
| After | 중복 행 제거 + 단일 출처 박음 |
| 안전장치 | 매 PR에 §7 갱신 자체 검증 |
| 자기 일관성 패턴 | 패턴 4 (옵션 비교 + 명시 결정) |
| 채용 어필 한 줄 | *"문서 정합성 자동 검증 — 새 개발자가 §7만 보고 시스템 상태 파악 가능"* |

### 9. T-2 — MCP 서버 (portfolio-service)

| 항목 | 내용 |
|---|---|
| Before | Aether 4 도구는 내부 호출만 — 외부 LLM 통합 X |
| After | `portfolio-service/app/mcp_server.py` stdio 서버, 4 도구(analyze_portfolio / compute_risk / run_backtest / get_recommendation) 외부 LLM 노출 |
| 안전장치 | in-SDK stdio_client 통합 테스트 4건 + `_serialize()` 8 분기 어댑터 (dataclass / numpy / pandas / Enum / Pydantic → JSON) |
| 자기 일관성 패턴 | 패턴 1 (Lazy Init `_TOOLS` dict) + 패턴 3 (응답 호환 어댑터) + ADR 0008 |
| 채용 어필 한 줄 | *"국내 도메인 MCP 서버 거의 0건 차별화 — Anthropic 표준 채택 + Claude Desktop / Cursor 즉시 호환 + LangChain args_schema 1:1 매핑"* |

### 10. T-6 — Qdrant 어댑터 마이그레이션

| 항목 | 내용 |
|---|---|
| Before | ChromaDB 1.5.0 직접 호출 (in-process volume, 멀티 인스턴스 동기화 X) |
| After | `vector_store.py` 어댑터 (ChromaDBStore + QdrantStore) + `VECTOR_STORE` env 토글 (default chromadb) |
| 안전장치 | 호출자(rag.py) 0 변경 + 마이그레이션 스크립트 (top-k 동등성 검증) + Qdrant in-memory 통합 테스트 17건 |
| 자기 일관성 패턴 | 패턴 1 (Lazy Init Singleton) + 패턴 3 (score → distance 변환) + 패턴 5 (env 토글) + ADR 0009 |
| 채용 어필 한 줄 | *"운영급 벡터 DB 마이그레이션 패턴 — 어댑터 + env 토글로 호출자 0 변경 + 운영 사고 시 즉시 롤백"* |

### (보류) 11. T-3 — Multi-Agent (LangGraph supervisor + worker)

| 항목 | 내용 |
|---|---|
| 결정 | **보류** — ADR 0010 인용 |
| 사유 | 시나리오 A(기술 데모) 본질 X / 차별화 임팩트 약함 (LangGraph 사례 多) / 단일 ReAct로 시나리오 A 충분 |
| 트리거 | 시나리오 B 진입 / Houseman Phase 7-12 진화 진입 시 |
| 학습 처리 | 적용 시점 통합 (별도 학습 repo X) — Houseman 진화 시점에 학습 + 구현 동시 |
| 자기 일관성 패턴 | **PRINCIPLES 패턴 6** (박지 않은 결정 = 명시한 결정만큼 강한 시그널) |
| 채용 어필 한 줄 | *"기술 도입은 누구나 가능 — 시니어 차이는 박지 않은 결정 + 진입 트리거 명시. T-3은 시나리오 A 본질 X라 보류 + Houseman Phase 7-12 학습 적용 통합 시점에 도입 명시"* |

---

## §3. 면접 답변 한 줄 (10 카드 + T-3 보류)

| 질문 | 답변 |
|---|---|
| *"Aether에서 가장 자랑스러운 카드는?"* | T-2 MCP 서버 — 국내 도메인 거의 0건 차별화 + Anthropic 표준 + LangChain 1:1 매핑 + 어댑터 0줄 |
| *"운영 진입 시점 마이그레이션 어떻게?"* | T-6 Qdrant 어댑터 + VECTOR_STORE env 토글로 호출자 0 변경 + 즉시 롤백 |
| *"AI 에이전트 도구 자율 분기?"* | T-1b ReAct max_iterations=10 + USE_REACT_AGENT=false 절차적 fallback 보존 |
| *"분산 트레이싱?"* | H-10 + L-7 X-Request-ID ContextVar + httpx event_hooks 자동 forward |
| *"외부 SDK 마이그레이션 안전?"* | H-6 google-genai 응답 어댑터 + timeout sec→ms 단위 변환 + 호출자 0 변경 |
| *"PR 게이트?"* | H-7 black/ruff/mypy/pytest cov 81% + tsc/eslint/vitest/build/markdownlint 8종 자동 |
| *"왜 Multi-Agent 안 했어요?"* | T-3 보류 결정 ADR 0010 — 시나리오 A 본질 X + Houseman Phase 7-12 학습 적용 통합 시점에 도입 |
| *"문서 정합성?"* | H-1 + H-1c AGENTS §7 단일 출처 + 카드별 갱신 자체 검증 |
| *"프롬프트 자산화?"* | H-4 prompt_registry.get(name, version) 단일 진입점 + 8 프롬프트 v1.0 등록 |
| *"인프라 + 동작 변경 분리?"* | T-1a + T-1b 2단 분해 — 회귀 위험 영역 분리 |

---

## §4. Top 10 9.5/10 + T-3 보류 = 시나리오 일관성 시그널

**Top 10 결과**: 9건 본격 머지 + 1건(T-3) 보류 결정 = **9.5/10**.

**일반 시각**: *"10/10 못 채웠으니 부족함"*
**시니어 시각**: *"보류 결정 + 진입 트리거 + 학습 적용 통합 = 결정 근거 추적 시스템 정착"*

면접 답변 시그널:
> *"Top 10에서 T-3 Multi-Agent는 보류 결정으로 ADR에 박았어요. 시나리오 A(기술 데모) 본질에 과한 복잡도라서요. 차별화 임팩트도 T-2 MCP / T-6 Qdrant 대비 약했고, LangGraph supervisor 사례가 많아서 차별화 시그널이 약했거든요. Houseman 프로젝트 Phase 7-12 진화 진입 시점에 학습 + 적용 통합으로 도입할 예정입니다. 별도 학습 repo는 안 만들었는데, 이유는 적용 시점에 다시 작성해야 해서 재사용 가치가 약하기 때문이에요. 박지 않은 결정 + 진입 트리거 명시 = 결정 근거 추적 시스템 자체가 시니어 시그널이라 봅니다."*

---

## §5. 메모리 #20 충족 — Top 10 종료 시 정리 약속

본 EVOLUTION.md 작성 = 메모리 #20의 *"Top 10 종료 시 정리"* 약속 충족.

다음 단계:
- **T-2b** (Claude Desktop config 가이드) — 외부 사용자 진입 시
- **H-1d** (`llm_max_tokens` 영구 해결) — 운영 단계 진입 시
- **WF-1** (사용자 워크플로우 통합) — 실서비스 진입 시
- **T-3a/T-3b** (Multi-Agent 진입) — 시나리오 B 진입 / Houseman Phase 7-12 진화 시점

→ Top 10 종료. EVOLUTION.md = 면접 / 이력서 자료 1차 완성.

---

## §6. 진화 회고 5 측면 (시니어 시그널 분류)

| 측면 | 카드 | 안전장치 | 시니어 패턴 | 비개발자 한 줄 |
|---|---|---|---|---|
| **자산화** | H-4 prompt_registry / H-1+H-1c AGENTS §7 | 단일 진입점 / 카드별 갱신 검증 | 패턴 1 (Lazy Init) | *"프롬프트 + 문서 = 코드만큼 신뢰 가능한 자산"* |
| **회귀 차단** | H-7 PR 게이트 8종 / T-1a+T-1b 2단 분해 | 자동 검증 / 영역 분리 | 패턴 5 (2단 분해) | *"PR 머지 시 사람이 검증할 일을 0으로"* |
| **마이그레이션** | H-6 SDK / T-6 Qdrant | 응답 어댑터 / env 토글 | 패턴 3 (응답 호환) | *"외부 변경에 호출자 0 변경 + 즉시 롤백"* |
| **차별화** | T-2 MCP / T-6 Qdrant | 측정 5건 사전 검증 / 어댑터 | 패턴 4 (옵션 비교) | *"국내 0건 사례 + 운영급 마이그레이션 패턴"* |
| **결정 근거 추적** | T-3 보류 결정 (본 PR) | ADR 0010 + EVOLUTION + PRINCIPLES 6번 | 패턴 6 (박지 않은 결정) | *"박지 않은 결정도 시그널 — 진입 트리거 + 학습 적용 통합 명시"* |

---

## §7. 다음 갱신 예정

- T-3a/T-3b 진입 시 — 본 EVOLUTION.md에 "보류 → 진입 결정" 회고 추가
- Houseman Phase 7-12 학습 + 적용 통합 결과 회고 (메모리 #18)
- 시나리오 B 진입 결정 시 — 시나리오 A → B 전환 회고

---

## 갱신 이력

| 일자 | 갱신 내용 | 갱신 사유 |
|---|---|---|
| 2026-05-05 (v1 / 본 문서) | 최초 작성 — Top 10 9건 회고 + T-3 보류 + 면접 답변 + 진화 5 측면 | 메모리 #20 충족 (Top 10 종료 시 정리 약속) + ADR 0010 인용 |
