# ADR 0008 — MCP 서버 채택 (T-2 Spike 결과)

**상태**: **Unblocked** (선행 카드 H-X 머지 — fastapi 0.119.1 / starlette 0.48.0 / anyio 4.13.0 등 mcp 호환 베이스라인 확보. T-2 본격 PR 즉시 재진입 가능)
**일자**: 2026-05-04 (Draft) / 2026-05-05 (Blocked 전환) / 2026-05-05 (Unblocked 전환)
**관련 카드**: `docs/agent-capability-audit/phase3/04_T-2_mcp_server.md`

---

## 컨텍스트

T-2 본격 PR(portfolio-service의 4 도메인 함수 MCP stdio 노출, 60~80h 추정)
진입 전 1.5h cap의 Spike로 **위험 선노출**. llm-service `tool_registry`(T-1a 자산)
의 `analyze_portfolio_tool` 1개를 stdio MCP 서버로 노출하는 PoC를 작성하고,
in-process MCP client로 list_tools / call_tool roundtrip을 검증.

레이어 분리:

- **Spike (이번)**: `llm-service/poc/`에서 LangChain `StructuredTool.args_schema.model_json_schema()` → MCP `Tool.inputSchema` 변환 패턴 검증.
- **본격 PR (다음)**: 카드 §4대로 `portfolio-service/app/mcp_server.py` 신규 + 4 도구 + L-7 X-Request-ID 연동.

## Spike 결과

### 1. SDK

- 패키지: `mcp` 1.27.0 (Anthropic, MIT) — 카드 §6 명세 `>=0.9.0` 충족, 1.x 안정.
- 부수 의존성: `httpx-sse 0.4.3`, `python-multipart 0.0.27`, `sse-starlette 3.4.1`, `pyjwt 2.12.1`.
- 영향: PyJWT가 2.9.0 → 2.12.1로 업그레이드됨. 본격 PR에서는 portfolio-service venv에 격리되므로 영향 없음. Spike venv는 종료 후 복원.
- 안정성 판정: **안정** (1.x 정식, breaking change 위험 낮음).

### 2. Transport

- **stdio 채택**. 사유: Claude Desktop 표준 호환, subprocess launch 모델로 보안/권한 분리 명확.
- `mcp.server.stdio.stdio_server()` async context manager — `(read, write)` AsyncFile 튜플 반환.
- `mcp.client.stdio.stdio_client(StdioServerParameters)` — `command/args/cwd/env` 4 필드로 server 기동.

### 3. Tool inputSchema 변환

- **1:1 매핑 OK, 어댑터 0줄**.
- LangChain `StructuredTool.args_schema.model_json_schema()` 반환 dict 키: `{description, properties, required, title, type}` — 표준 JSON Schema.
- MCP `Tool.inputSchema`는 dict 자유형 — 그대로 대입 가능 (`Tool(name=t.name, description=t.description, inputSchema=t.args_schema.model_json_schema())`).
- 필드 명세: `Tool` 9 필드 — `name, title, description, inputSchema, outputSchema, icons, annotations, meta, execution`. PoC는 3 필드만 사용, 본격 PR에서 outputSchema 활용 검토.

### 4. 외부 호출 검증 (in-SDK stdio client)

Claude Desktop 설정은 secret 외부 파일 작성이라 CLAUDE.md §4 위험 항목.
대안으로 `mcp.client.stdio.stdio_client` + `ClientSession`으로 PoC 서버를 subprocess로 띄워 자동 검증.

| 호출 | 결과 | latency |
|---|---|---|
| `initialize` | OK | — |
| `list_tools` | 1 tools, inputSchema 5 키 정상 | **6.1ms** |
| `call_tool` (dummy 인풋) | `isError=True`, 비즈니스 검증 실패 (`metrics.expected_return` 누락) | **25.6ms** |

→ Protocol/transport/inputSchema 모두 정상. call_tool isError는 도구 비즈니스 검증 미통과 (PoC 인풋 dummy)이지 MCP layer 실패 아님.

### 5. 본격 PR 진입 판정

- [x] SDK 안정 (1.27.0 정식)
- [x] tool_registry args_schema → inputSchema **1:1 매핑** (어댑터 0줄)
- [x] in-SDK client 호출 성공 (initialize / list / call 모두 도달)
- [x] 1.5h cap 준수
- [x] PoC commit 0 (Spike 본질)

→ **본격 PR 진입 OK**.

## 본격 PR 진입 결정

T-2 본격 PR(`docs/agent-capability-audit/phase3/04_T-2_mcp_server.md` §4)
그대로 진입 가능. portfolio-service의 4 도메인 함수에 Spike에서 검증된
변환 패턴 적용:

```python
Tool(
    name=fn.__name__,
    description=fn.__doc__,
    inputSchema=PydanticModel.model_json_schema(),  # 또는 LangChain StructuredTool.args_schema.model_json_schema()
)
```

서버 구조 4 줄 책임:

1. `Server("aether-portfolio")` 생성 + `@server.list_tools()` / `@server.call_tool()` 데코레이터 2개.
2. `stdio_server()` async context — `server.run(read, write, init_options)`.
3. call_tool 핸들러: dispatch dict (`name → callable`) + `json.dumps(result)` → `TextContent`.
4. L-7 X-Request-ID는 MCP `meta` 또는 별도 logging context로 주입.

## 본격 PR 진입 시도 결과 (2026-05-05) — Blocked

T-2 본격 PR을 위해 portfolio-service venv에 `mcp>=1.0,<2.0` 설치 시도 → **fastapi 0.104.1과 의존성 충돌**.

### 충돌 매트릭스 (실측)

`pip install 'mcp>=1.0,<2.0'`이 강제 업그레이드한 패키지:

| 패키지 | 기존 (portfolio-service) | mcp 1.27.0 요구 | fastapi 0.104.1 요구 | 결과 |
|---|---|---|---|---|
| `anyio` | 3.7.1 | `>=4.5` | `>=3.7.1,<4.0.0` | **충돌** |
| `starlette` | 0.27.0 | sse-starlette `>=0.49.1` 경유 | `>=0.27.0,<0.28.0` | **충돌** |
| `pydantic` | 2.5.3 | `>=2.11.0,<3.0.0` | `>=1.7.4,<3.0.0` (호환 OK) | mcp만 영향 |
| `pyjwt` | 2.9.0 | `>=2.10.1` | (제약 X) | mcp만 영향 |
| `httpx` | 0.25.2 | `>=0.27.1` | (제약 X) | mcp만 영향 |
| `uvicorn` | 0.24.0 | `>=0.31.1` | (제약 X) | mcp만 영향 |

설치 후 `from app.main import app` 실측: `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'` — fastapi 0.104.1이 강제 업그레이드된 starlette 1.0.0과 비호환.

### 회복

`pip install --force-reinstall -r requirements.txt`로 fastapi 0.104.1 + anyio 3.7.1 + starlette 0.27.0 복원, mcp/sse-starlette/jsonschema 등 잔여 패키지 uninstall, `pytest tests/test_optimizer.py tests/test_risk.py` 42 passed 검증 완료. venv는 머지 전 상태로 복귀.

### 차단 결정

- 가드 G2 (Reversibility — 신규 모듈만, 기존 코드 0 변경) 위반 위험: fastapi 업그레이드는 routers/main.py 동작 영향 가능 (예: lifespan / on_startup / Depends 시그니처).
- 가드 G1 (3h cap) — 초과 전 자동 트리거.
- CLAUDE.md §6 (1카드 1책임) — fastapi 업그레이드는 별도 카드 책임.

→ **본격 PR 보류**. ADR만 Blocked로 갱신.

## 충돌 해소 매트릭스 (H-X 머지 결과, 2026-05-05)

선행 카드 H-X로 portfolio-service 베이스라인 일괄 업그레이드. T-2 본격 PR이 추가 트리거하는 transitive upgrade를 H-X에 흡수하여 T-2는 `mcp>=1.0,<2.0` 1줄 추가만으로 진행 가능.

| 패키지 | 이전 (충돌 시점) | H-X 후 | mcp 1.27 요구 | 상태 |
|---|---|---|---|---|
| `fastapi` | 0.104.1 | **0.119.1** | (제약 X, 호환 OK) | ✅ |
| `starlette` | 0.27.0 | **0.48.0** | sse-starlette 경유 0.49.1+ → 0.48.0 OK | ✅ |
| `anyio` | 3.7.1 | **4.13.0** | `>=4.5` | ✅ |
| `httpx` | 0.25.2 | **0.28.1** | `>=0.27.1` | ✅ |
| `pyjwt` | 2.9.0 | **2.12.1** | `>=2.10.1` | ✅ |
| `uvicorn` | 0.24.0 | **0.46.0** | `>=0.31.1` | ✅ |
| `pydantic` | 2.5.3 | **2.13.3** | `>=2.11.0` | ✅ |
| `pydantic-settings` | 2.1.0 | **2.14.0** | `>=2.5.2` | ✅ |

H-X 회귀 검증: `pytest tests/` **215 passed** (회귀 0). `from app.main import app` 정상.

### 측정 4단계 결과 (WORK_PATTERNS 문제 18 첫 적용)

1. **dry-run 매트릭스**: `pip install --dry-run 'fastapi>=0.115,<0.120' 'mcp>=1.0,<2.0'` → 다운그레이드/충돌 0건
2. **다차원 의존성**: anyio / starlette / httpx / pyjwt / uvicorn / pydantic 6 차원 모두 호환 확인
3. **on_startup grep**: 0 사용처 → lifespan 마이그레이션 skip
4. **BaseHTTPMiddleware**: 1 사용처 (RequestLoggingMiddleware) — starlette 0.27→0.48 점프 후 회귀 0 (`tests/test_logging.py` 5 케이스 pass)

## 후속 카드 트리거 (Unblocked 해소 경로)

1. ~~**선행 카드 H-X (필수)**~~ — **완료 (2026-05-05 머지)**. fastapi 0.119.1 / starlette 0.48.0 / anyio 4.13.0 / httpx 0.28.1 / pyjwt 2.12.1 / uvicorn 0.46.0 / pydantic 2.13.3 일괄 업그레이드. 215 테스트 회귀 0.
2. **T-2 본격 PR 재개 (즉시 가능)** — `04_T-2_mcp_server.md` §4 그대로 진입. `mcp>=1.0,<2.0` 1줄 추가, `portfolio-service/app/mcp_server.py` 신규, 4 도구 노출.
3. **선택 — H-X-llm (보류)** — llm-service는 본 카드 영향 없음 (mcp 미도입). 향후 llm-service에도 MCP 서버 도입 결정 시 동일 패턴 별도 카드.
4. **ADR 0002 (모듈 경계) 갱신** — T-2 본격 PR과 같은 PR (MCP 외부 인터페이스 추가 시점).

## 변경 사항

### Spike (commit 0 보존)
- `llm-service/poc/mcp_server_poc.py` (Spike 산출물)
- `llm-service/poc/mcp_client_check.py` (Spike 산출물)

### 본격 PR 시도 (이번 PR — Blocked 문서화만)
- `docs/adr/0008-mcp-server-adoption.md` (Draft → Blocked 전환, 충돌 매트릭스 추가)
- `docs/agent-capability-audit/WORK_PATTERNS.md` (의존성 베이스라인 사전 측정 누락 패턴 추가)
- `portfolio-service/requirements.txt` — **변경 없음** (mcp 미추가)
- `portfolio-service/app/mcp_server.py` — **미생성** (선행 카드 후 재개)
- `AGENTS.md` — **변경 없음** (도구 미노출이므로 §7 신규 행 미추가)

T-1a / T-1b / H-6 인프라 0 변경. llm-service/app/ 0 변경. portfolio-service/app/ 0 변경.
