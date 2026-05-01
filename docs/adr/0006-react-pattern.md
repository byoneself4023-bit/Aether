# ADR 0006 — ReAct 패턴 채택 (chat.py 절차적 4 호출 → ReAct 1 호출)

- **상태**: Accepted
- **일자**: 2026-05-01
- **관련 작업**: T-1b (LangGraph ReAct 통합)
- **선행 ADR**: 0005 (LangGraph 채택), 0002 (모듈 경계 — agents 활성)

---

## 컨텍스트

T-1a 머지 후 `app/agents/` 인프라는 정착됐지만 `chat.py:331-356`은 여전히 4 도메인 함수를 절차적으로 순차 호출 중:

```python
portfolio_analysis = analyze_portfolio(...)
risk_analysis     = explain_risk(...)
backtest_analysis = summarize_backtest(...)
recommendation    = get_recommendation(...)
```

문제:

1. **호출 순서·조합이 코드에 hardcoded**. 사용자가 "수익률만 알려줘"를 요청해도 4 호출 모두 발생 — 비용·지연 낭비.
2. **새 도메인 분석 추가 = 라우터 분기 추가**. routers/chat.py에 if/else 누적.
3. **모델이 도구 선택의 주체가 아님**. LLM은 단순 응답 생성기 — Tool Use 시그널 약함.

---

## 결정

**`chat.py:331-356`을 ReAct 1 호출로 통합한다.**

- `app/agents/react_agent.py::ReActAgent` 가 `langgraph.prebuilt.create_react_agent`로 LLM + 4 @tool을 묶음
- 모델이 도구 호출 순서·조합을 자율 판단
- 응답 호환 어댑터 `_extract_tool_results`가 ToolMessage 흐름 → AnalysisResponse 4 필드로 매핑 → 호출자(frontend) 회귀 0
- **fallback**: `USE_REACT_AGENT=false` env로 기존 절차적 호출 즉시 복원 (코드 변경 없음)

---

## 대안 비교

| 패턴 | 장점 | 단점 | 결정 |
|---|---|---|---|
| **ReAct (LangGraph create_react_agent)** | 모델이 도구 호출 자율 판단 / 새 도구 추가 = 라우터 변경 0 / 공고 매칭 (Tool Use·Agent 자율성·프롬프트 엔지니어링 3중) / T-3 Multi-Agent 진입 시 Subgraph 자연 확장 | 토큰 폭증 가능 (도구 호출 + 결과 합산) / 응답 시간 직렬화 / ToolMessage 직렬화 형식 의존 | **채택** |
| 단순 Function Calling (모델이 도구 호출 1 회만) | 토큰 절감 / 응답 시간 짧음 | 4 도구를 모두 호출해야 하는 본 케이스에선 효과 0 / Loop가 필요할 땐 또 분기 추가 | 미채택 |
| Plan-and-Execute (LLM이 계획 → 별도 executor) | 흐름 명시성 / 디버깅 용이 | 추상 추가 / 본 케이스(고정 4 도구) 오버엔지니어링 / T-3 Multi-Agent와 중복 추상 | 미채택 |
| 절차적 호출 유지 (현재) | 단순. 토큰·시간 예측 가능 | 위 컨텍스트 §문제 1·2·3 미해결 / 공고 매칭 약함 | 본 PR로 폐기 (fallback만 보존) |

---

## 본질 — 모델을 도구 호출의 주체로

T-1b는 단순 코드 통합이 아니다. **LLM의 역할을 "응답 생성기"에서 "도구 선택자 + 응답 종합자"로 격상**시키는 선언이다.

- 절차적: routers가 LLM을 호출 → LLM이 텍스트 반환 → routers가 다음 함수 결정
- ReAct: routers가 ReActAgent 호출 → ReActAgent가 LLM + 도구를 그래프로 묶음 → LLM이 도구 선택 + 호출 + 결과 합산

이 변화는 T-2 (MCP 서버) 진입 시 결정적이다. MCP는 외부 클라이언트(Claude Desktop 등)가 본 서비스의 도구를 호출하는 프로토콜 — ReActAgent가 이미 도구를 graph로 묶어뒀기 때문에 MCP 어댑터는 도구 목록만 노출하면 끝.

---

## 응답 형식 호환 (회귀 0 보장)

ReAct 결과 (`react_result["messages"]`)에서 4 ToolMessage를 추출 → AnalysisResponse 4 필드에 매핑:

```python
_TOOL_NAME_TO_FIELD = {
    "analyze_portfolio_tool":  "portfolio_analysis",
    "explain_risk_tool":       "risk_analysis",
    "summarize_backtest_tool": "backtest_analysis",
    "get_recommendation_tool": "recommendation",
}
```

`summary` (한 줄 요약, 메트릭 기반) + `portfolio_data` (PortfolioData) 는 LLM과 무관 — 기존 코드에서 그대로 생성. 호출자(frontend) 입장에선 응답 형식 변경 0.

---

## 운영 안전망

`USE_REACT_AGENT=false` 환경변수로 즉시 절차적 호출 복원. 코드 변경 0, 재배포 0. ReAct가 토큰 폭증·응답 지연·기타 문제를 일으키면 운영자가 env만 토글하면 끝.

테스트도 동일 패턴 — `tests/conftest.py`의 autouse `_disable_react_agent`가 기본 fallback 모드 강제. ReAct 검증은 `@pytest.mark.use_react_agent` 마커로 opt-in. 이 패턴은 H-10의 `_bypass_jwt`와 자기 일관 (사용자 결정 1).

---

## 영향

- 새 도메인 분석 추가: `app/agents/portfolio_tools.py`에 @tool 함수 + `tool_registry` 등록만으로 ReActAgent가 자동 활용. routers 변경 0.
- T-2 (MCP 서버) 진입 시 ReActAgent의 4 도구가 그대로 MCP tool로 재활용.
- T-3 (Multi-Agent) 진입 시 Supervisor가 ReActAgent를 Sub-Agent로 호출.
- 토큰 사용량 모니터링 — `token_tracker.py`로 ReAct 평균 토큰 추적 (운영 KPI).
- AGENTS.md §1 호출 체인 + §10 Agent Architecture가 본 ADR의 운영 인덱스.

---

## YAGNI — 본 카드에서 미도입

- ReAct response_format (Pydantic 강제 출력) — 본 케이스는 도구 결과 추출이 충분
- Custom Graph (create_react_agent 대신 직접 StateGraph) — prebuilt로 충분
- Conditional Edges (도구 의존성 명시) — 프롬프트로 충분 (`recommendations는 backtest 참고`)
- Memory / Checkpointer — T-3 Multi-Agent 진입 시 도입

신규 LLM 도구가 5종 이상으로 증가하거나 도구 의존성이 복잡해지면 Custom Graph로 마이그레이션 검토.
