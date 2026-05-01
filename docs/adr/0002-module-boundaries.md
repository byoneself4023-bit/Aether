# ADR 0002 — Module Boundaries: routers / services / agents

- **상태**: Accepted — `agents/` 활성 (T-1a + H-2 머지 2026-05-01)
- **일자**: 2026-04-28
- **관련 작업**: H-1 (본 ADR 작성), H-2 (agents/ 신설), T-1 (Tool Use 패턴)

---

## 컨텍스트

llm-service는 FastAPI 권장 레이아웃(`routers/services/schemas/middleware`)을 따르고 있으나, 두 가지 문제가 있다:

1. **`agents/` 디렉토리 부재** (`docs/agent-capability-audit/02_agent_implementation.md:§1`). 라우터 함수가 `services/llm.py`의 도메인 함수와 `portfolio_client.py`의 외부 호출을 직접 순차 호출하는 절차적 함수 체인 형태. LangChain/LangGraph/AutoGen 0건 (`Grep` 결과).
2. **레이어 경계가 코드로 강제되지 않음**. routers가 schemas를 생성하지 않고 services 내부 모듈을 직접 import하거나, services가 middleware를 import하는 회귀가 발생할 수 있다.

H-2 카드는 `app/agents/` 디렉토리를 신설하고 BaseAgent 추상화를 도입한다. 본 ADR은 그 도입의 사전 결정을 문서화한다.

---

## 결정

**현재 레이어 (확정)**:

```text
app/
├── main.py             # FastAPI 진입점, 라이프사이클, 미들웨어 등록
├── config.py           # Pydantic Settings
├── routers/            # HTTP 엔드포인트만. 도메인 로직 금지.
├── services/           # 도메인 로직, 외부 호출, LLM/RAG.
├── schemas/            # Pydantic 모델. 모든 레이어가 import 가능.
├── middleware/         # main.py가 등록만. services에서 import 금지.
└── data/               # knowledge_base 정적 자산.
```

import 방향: `routers → services → 외부` (단방향). schemas는 자유. middleware는 고립.

근거: `llm-service/app/main.py:8-13, 64-66`, 01:§3 (depth 3 트리).

**T-1a + H-2 도입 후 (활성, 2026-05-01)**:

```text
app/
├── agents/                  # 활성
│   ├── __init__.py          # public API: BaseAgent, get_tool_registry, ToolRegistry
│   ├── base.py              # BaseAgent 추상 (run() 1 메서드, YAGNI)
│   ├── tools.py             # ToolRegistry + get_tool_registry() lazy init
│   └── portfolio_tools.py   # 4 도메인 함수 @tool 래퍼
└── services/                # 도구화된 함수 노출 (services가 agents를 import 금지)
```

- `BaseAgent` 1줄 책임: `async run(user_input, context) -> dict` (CLAUDE.md §6).
- routers는 agents를 호출 가능 (T-1b 진입 시). agents는 services를 도구로 호출. services는 agents를 모른다 (의존 역전).
- T-1a 시점에는 routers가 agents를 직접 호출하지 않음 (chat.py 0 변경) — T-1b ReAct 통합에서 활성화.

---

## 결과

**얻는 것**:

- 새 도메인 분석 추가 시 `agents/` 1 파일 + `services/` 0 파일 변경으로 끝나는 구조.
- LLM의 도구 선택을 코드 분기 대신 BaseAgent의 tool 등록으로 표현 (T-1 카드).
- 단위 테스트 단위가 명확 — agents는 services를 mock 가능, services는 외부를 mock 가능.

**감수하는 것**:

- 레이어 위반은 코드로 강제되지 않는다 (Python에는 module-level visibility가 없다). 컨벤션에 의존. H-7 PR 게이트에서 `import-linter` 같은 정적 검사 도입을 검토.
- T-1a + H-2 머지로 §결정 두 번째 블록이 활성. T-1b가 chat.py:331-349 절차적 호출을 ReAct로 통합 예정.

---

## 영향

- 신규 PR이 routers에서 외부(httpx, google-generativeai)를 직접 호출하면 본 ADR 위반.
- services에서 middleware/agents를 import하면 본 ADR 위반.
- T-1a + H-2 머지로 본 ADR §결정 두 번째 블록 "예정 → 활성" 갱신 완료 (2026-05-01).
- T-1b 머지로 `routers → agents` 의존 활성 (chat.py가 ReActAgent 호출). LangGraph 채택 사유는 ADR 0005, ReAct 패턴 채택 사유는 ADR 0006 참조.
