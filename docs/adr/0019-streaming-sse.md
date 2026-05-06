# ADR 0019 — Streaming SSE 본격 정착 (D-6)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: D-6 (우대 요건 4 직격)
- **결정 근거**: ADR 0005 (LangGraph) + 0006 (ReAct) + 0018 (5 도구 통합) + ADR 0011 형식 + 점진 전환 본능 (D-5 패턴 일관성)

---

## 컨텍스트

D-5 ReAct 5 도구 자율 판단 평균 12.8초 → 사용자가 응답 전체를 대기. token stream 본격 정착으로 UX 진화. **우대 요건 4번 (Streaming 응답 처리 — SSE / WebSocket) 직격 매칭**.

신규 endpoint `/api/chat/stream` 분리 본능 — 기존 `/api/chat` 0 변경 (frontend 영향 0).

---

## 결정 (4 분기 본격 추적)

### 분기 1: SSE vs WebSocket — **SSE 채택**

| 옵션 | 본격 |
|---|---|
| **SSE** ✓ | 단방향 (서버 → 클라이언트) / HTTP/1.1 chunked / 본격 적합 (LLM token stream) |
| WebSocket | 양방향 / 본격 의무 X (사용자 입력은 1회) — 시나리오 B 트리거 |

### 분기 2: astream vs astream_events — **astream_events 채택**

| 옵션 | 본격 |
|---|---|
| `astream` | state stream — token 단위 X |
| **`astream_events`** ✓ | LangGraph 0.2+ — `on_chat_model_stream` / `on_tool_start` / `on_tool_end` 캡처 |

### 분기 3: LangGraph 통합 vs LLM 직접 — **통합 채택**

| 옵션 | 본격 |
|---|---|
| **A: LangGraph 통합** ✓ | ReAct 5 도구 자율 판단 본격 stream |
| B: LLM 직접 | ReAct 우회 / 기능 축소 |

### 분기 4: RAG fallback 본격 처리 — **옵션 A 채택**

| 옵션 | 본격 |
|---|---|
| **A: 티커 < 2 시 RAG fallback** ✓ | 기존 /api/chat 패턴 일관성 |
| B: ReAct 단일 흐름 | 본격 단순화 / 일관성 손실 |

---

## Decision

1. 신규 endpoint `POST /api/chat/stream` (`StreamingResponse(media_type="text/event-stream")`)
2. 기존 endpoint `/api/chat` 0 변경 (회귀 0 의무)
3. `react_agent.py:run_stream` async generator 메서드 신규 — `astream_events` v2 활용
4. `streaming.py` 신규 — sse_event / sse_done / format_token_event / format_tool_event / format_error_event
5. JWT 검증 + sanitize_user_input + 티커 < 2 RAG fallback (기존 패턴 일관성)
6. SSE format: `[event: <name>\n]data: <json>\n\n` + 종료 시그널 `event: done`

---

## E2E 결과 (실 측정 / curl -N)

| 시나리오 | 입력 | events | tokens | tool_events | done | 소요 시간 |
|---|---|---|---|---|---|---|
| 1. 티커 X (RAG fallback) | "샤프 비율이란?" | 2 | 1 | 0 | 1 | **4.62s** |
| 2. 티커 O (ReAct 5 도구) | "AAPL, MSFT 분석해줘" | 9 | 6 | 2 | 1 | 20.05s |
| 3. 조합 (5 도구 자율) | "VaR + AAPL/MSFT 분석" | 8 | 5 | 2 | 1 | 12.80s |

**핵심 검증**:
- ✓ SSE format 본격 동작 (`data: {json}\n\n`)
- ✓ `on_tool_start` / `on_tool_end` event 캡처 (시나리오 2 / 3)
- ✓ `event: done` 종료 시그널
- ✓ 시나리오 1 (티커 X) RAG fallback 일관성 보장
- ✓ 첫 응답 도달 (E2E 1 = 4.62s) 5초 이내 본격 도달 의무 충족

---

## 영향

### 시그널 강화 (+)

- **우대 요건 4 직격 매칭** (SSE)
- **양면 정책 9 ADR 정립**: 0011-**0019** = 시니어 시그널 누적
- UX 진화: 첫 응답 도달 시간 4.62s (티커 X) — 기존 동기 응답 대비 본격 진화
- ReAct 5 도구 본격 stream 통합 (D-5 학습 활용)
- 분기 결정 4건 본격 추적 = 면접 답변 자료 ("왜 SSE? 왜 astream_events? 왜 통합? 왜 fallback A?")
- 점진 전환 본능 일관성 (D-5 신규 endpoint 분리 패턴 본격 재사용)

### 트레이드오프 (−)

- WebSocket 미적용 (양방향 의무 X — 시나리오 B 트리거)
- Frontend SSE 통합 별도 카드 분리 (현재 backend 본격만)
- token 단위 yield network overhead (HTTP/1.1 chunked로 완화)

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| WebSocket 양방향 stream | 실시간 대화 본격 시점 |
| Frontend SSE 통합 (`/dashboard/chat`) | 시나리오 B 진입 / Frontend 본격 |
| Stream 중간 취소 (사용자 abort) | 사용자 영역 의무 |
| Stream 응답 cache (Redis 본격) | 동일 질문 반복 영역 발생 |
| Token rate limiting | 비용 추적 본격 시점 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **D-4** | D-6 머지 후 | 코드 Audit / 종합 정리 |
| **P-1** | D-4 후 | PRINCIPLES 8/9/10 |
| **I-1** | P-1 후 | 면접 답변 시뮬레이션 |
| **F-N (Frontend SSE)** | 시나리오 B 진입 | /dashboard/chat SSE 통합 |
| **F-N (WebSocket)** | 양방향 의무 발생 | 실시간 대화 본격 |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (4 분기 결정 본격 추적 + 3 E2E PASS + 양면 정책 9 ADR 정립). 우대 요건 4 직격 매칭. |
