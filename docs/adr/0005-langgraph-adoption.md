# ADR 0005 — LangGraph 채택 (Agent Framework)

- **상태**: Accepted
- **일자**: 2026-05-01
- **관련 작업**: T-1a (LangGraph 인프라), H-2 (모듈 경계), T-1b (ReAct 통합 예정)

---

## 컨텍스트

`llm-service`는 한 사용자 요청에 LLM을 4번 호출한다 (`chat.py:331-349`):

1. `analyze_portfolio` — 포트폴리오 분석
2. `explain_risk` — 리스크 설명
3. `summarize_backtest` — 백테스트 요약
4. `get_recommendation` — 개선 제안

각 호출은 절차적으로 순차 실행되며, **LLM이 어떤 도구를 호출할지 코드 분기로 결정**한다. 이는 다음 한계가 있다:

1. **새 도메인 분석 추가 = 코드 분기 추가**: routers/chat.py에 if/else가 누적된다.
2. **사용자 의도와 도구 호출 매핑이 코드에 hardcoded**: "수익률만 알려줘" 같은 부분 요청에도 4 호출 모두 발생.
3. **LLM 호출 수가 고정**: 비용·지연 최적화 여지 0.

T-1 카드는 이를 **ReAct 패턴 (LLM이 도구 선택)**으로 대체한다. 본 ADR은 그 프레임워크 결정을 문서화한다.

---

## 결정

**LangGraph (>= 0.2)를 채택한다.**

- 프레임워크: LangGraph 1.1.10 (측정 시점)
- 통합: `langchain-google-genai` 4.2.2 (Gemini provider) + `langchain-core` 1.3.2 (`@tool` 데코레이터)
- 진입 단계:
  - **T-1a (본 카드)**: 인프라만 — `app/agents/` 모듈 + `BaseAgent` 추상 + `ToolRegistry` + 4 함수 @tool 래핑. **chat.py 0 변경**.
  - **T-1b (다음 카드)**: ReAct 통합 — `chat.py:331-349` 절차적 4 호출 → ReAct 1 호출.
  - **T-3 (Big Bet)**: Multi-Agent — Supervisor 패턴, Subgraph 추상 도입.

---

## 대안 비교

| 프레임워크 | 장점 | 단점 | 결정 |
|---|---|---|---|
| **LangGraph** | LangChain 생태계와 자연 통합 / 명시적 Graph 추상으로 흐름 추적 용이 / Multi-Agent (Supervisor·Subgraph) 1급 지원 / `langchain-google-genai`로 Gemini 직접 통합 | 의존성 무거움 (18 패키지 신규) / 1.x 버전이 비교적 최근 (호환성 변동 위험) | **채택** |
| LangChain Agents (legacy AgentExecutor) | 단순. 학습 곡선 낮음 | 1.0+에서 deprecated. ReAct는 가능하나 Multi-Agent·상태 관리 빈약. T-3 진입 시 마이그레이션 부담 | 미채택 |
| CrewAI | Multi-Agent 시각화 우수 / Role-based 추상 직관적 | LangChain 생태계와 분리 / Gemini 통합 추가 작업 / 한국 커뮤니티·공고 매칭 약함 | 미채택 |
| AutoGen | Microsoft 산업 채택 / Multi-Agent 강력 | OpenAI 우선 / Gemini 어댑터 미성숙 / 본 프로젝트 BFF 패턴과 결합 부자연 | 미채택 |
| 자체 구현 (no framework) | 의존성 0 / 완전 제어 | ReAct 루프 / tool calling 직접 구현 비용 / Multi-Agent 진입 시 재작업 / 공고 매칭 시그널 약함 | 미채택 |

---

## 본질 — LangGraph가 가져올 변화

T-1a는 단순 의존성 추가가 아니다. **에이전트 흐름을 코드 분기에서 그래프로 옮긴다**는 선언이다.

- 현재: `chat.py`가 4 함수를 `await`로 순차 호출. 흐름은 코드 라인 순서.
- T-1b 후: ReAct Agent가 도구 4종 중 필요한 것만 호출. 흐름은 LLM 추론 + Graph edge.
- T-3 후: Supervisor가 도메인별 Sub-Agent에게 위임. 흐름은 Multi-Agent 조율.

이 변화는 routers가 LLM 추론을 코드로 흉내 내는 패턴 → routers가 에이전트에 위임하는 패턴으로 이동한다 (의존 역전).

---

## YAGNI 원칙 (T-1a 적용)

T-1a에서는 **T-1b ReAct 진입에 필요한 것만** 만든다:

- ✓ `BaseAgent` 추상 — `run()` 1 메서드
- ✓ `ToolRegistry` — `register/get/list_all` 3 메서드
- ✓ 4 함수 @tool 래퍼 — 1:1 대응

**미도입 (T-3 Multi-Agent 진입 시)**:
- Supervisor / Subgraph 추상
- Conditional Edges 헬퍼
- Memory / Checkpointer

---

## 자기 일관성 — prompt_registry 패턴 미러

`tool_registry`는 `prompt_registry` (H-4)와 **인터페이스 + 인스턴스화 패턴까지 동일**:

```python
# prompt_registry (H-4):
_registry: PromptRegistry | None = None
def get_registry() -> PromptRegistry: ...

# tool_registry (T-1a):
_tool_registry: ToolRegistry | None = None
def get_tool_registry() -> ToolRegistry: ...
```

두 registry 모두 lazy init + `_register_default_*()` 부수효과 + 테스트 reset 가능. 학습 비용 절감.

---

## 영향

- 신규 LLM 도구 추가 시 `agents/portfolio_tools.py` 또는 신규 `agents/<domain>_tools.py`에 @tool 함수 정의 + `_register_default_tools()`에 등록.
- routers가 services의 도메인 함수를 직접 호출하는 패턴은 T-1b 머지 시점에 ReAct 호출로 대체.
- T-3 Big Bet 시점에 Supervisor + Subgraph 도입 — 본 ADR 갱신 의무.
- AGENTS.md §10 "Agent Architecture" 섹션이 본 ADR의 운영 인덱스.
