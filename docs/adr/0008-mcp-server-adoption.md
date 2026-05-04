# ADR 0008 — MCP 서버 채택 (T-2 Spike 결과)

**상태**: **Accepted** (T-2 본격 PR 머지 — `portfolio-service/app/mcp_server.py` 신규, 4 도구 stdio 노출, 4 통합 테스트 통과, 215 회귀 0)
**일자**: 2026-05-04 (Draft) / 2026-05-05 (Blocked) / 2026-05-05 (Unblocked) / 2026-05-05 (Accepted)
**관련 카드**: `docs/agent-capability-audit/phase3/04_T-2_mcp_server.md`
**결정 근거 (면접 답변 일관성)**: `docs/agent-capability-audit/TECH_DECISIONS.md` §5 MCP (라인 198-230)

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

## T-2 본격 PR 머지 결과 (2026-05-05) — Accepted 전환

### 4 도구 매핑 표 (실측, MCP `Server("aether-portfolio")` 등록)

| MCP Tool name | InputSchema (Pydantic) | 호출 대상 (서비스 레이어) | 반환 dataclass |
|---|---|---|---|
| `analyze_portfolio` | `AnalyzePortfolioInput` (mu / cov / rf) | `app/services/optimizer.py:optimize_max_sharpe(mu, cov, rf)` | `PortfolioMetrics` |
| `compute_risk` | `ComputeRiskInput` (weights / mu / cov / n_simulations) | `app/services/risk.py:risk_summary(weights, mu, cov, ...)` | `RiskSummary` |
| `run_backtest` | `RunBacktestInput` (returns / asset_names / dates / strategy) | `app/services/backtest.py:walk_forward_backtest(df, strategy)` | `BacktestResult` (`pd.Series`/`pd.DataFrame` 포함) |
| `get_recommendation` | `GetRecommendationInput` (recent_returns / historical_returns / asset_names) | `app/services/drift_detector.py:analyze_drift(recent, hist, asset_names)` | `CombinedDriftAnalysis` (Enum 포함) |

### 측정 4단계 결과 (WORK_PATTERNS 문제 18 본격 적용)

1. **dry-run**: `pip install --dry-run 'mcp>=1.0,<2.0'` → 충돌 0건 ✓
2. **6차원 의존성 매트릭스**: anyio / starlette / httpx / pyjwt / uvicorn / pydantic 호환 ✓
3. **on_startup grep**: 0건 → lifespan 마이그레이션 skip
4. **BaseHTTPMiddleware**: 1건 (RequestLoggingMiddleware) — 215 회귀 0 검증 ✓

### 추가 발견 (2차 적용 — T-2 본격 PR에서 해소)

`mcp 1.27.0`이 `sse-starlette>=3.4.1` 요구 → starlette 1.0.0 트랜지티브 업그레이드 → fastapi 0.119.1과 충돌. 해소: `sse-starlette==3.0.3` 핀(pip resolver 자동 선택 버전, starlette 0.48 호환). 베이스라인 변경 X.

### L-7 X-Request-ID 통합 (옵션 A 채택)

```python
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    request_id = arguments.pop("_request_id", None) or str(uuid.uuid4())[:8]
    token = request_id_ctx.set(request_id)
    try:
        ...
    finally:
        request_id_ctx.reset(token)
```

`_request_id`는 inputSchema에 노출 X (외부 LLM은 모름, 자동 생성). 기존 `RequestLoggingMiddleware`의 `request_id_ctx`와 자기 일관성 유지.

### `_serialize()` 어댑터 (응답 호환 패턴 3)

dataclass / numpy ndarray / numpy scalar / pandas Timestamp / pandas Series / pandas DataFrame / Enum / Pydantic / dict / list/tuple 8 분기 recursion. 4 도구 모두 호환.

### entrypoint 패턴

```bash
PYTHONPATH=/path/to/portfolio-service python -m app.mcp_server
```

Claude Desktop config 예시는 후속 카드 T-2b에서 README 가이드 추가.

### 통합 테스트 결과 (in-SDK stdio_client, Spike 패턴 정착)

| 테스트 | 결과 |
|---|---|
| `test_list_tools_returns_4` | ✓ 4 도구 list 검증 |
| `test_call_compute_risk_success` | ✓ numpy → JSON dict roundtrip (var_95 / cvar_95 / expected_return 검증) |
| `test_call_unknown_tool_returns_error` | ✓ ValueError → MCP isError=True |
| `test_call_invalid_schema_returns_error` | ✓ Pydantic ValidationError → MCP isError=True |

`pytest tests/test_mcp_server.py -v`: **4 passed**. 기존 215 회귀 0.

## 후속 카드 트리거 (Accepted 후)

1. ~~**선행 카드 H-X**~~ — 완료 (PR #10).
2. ~~**T-2 본격 PR**~~ — **완료 (이번 PR)**. 4 도구 stdio 노출 + 통합 테스트 + ADR Accepted.
3. **T-2b** (선택, 후속) — Claude Desktop / Cursor config README 가이드 추가.
4. **T-2c** (보류) — MCP HTTP/SSE transport 추가 (TECH_DECISIONS §5 미래 마이그레이션 트리거: 원격 호출 / 다중 클라이언트 동시 접속 시).
5. **ADR 0002 (모듈 경계) 갱신** — MCP가 새 외부 인터페이스로 portfolio-service에 추가됨. 별도 정리 카드 또는 다음 큰 변경 시점.

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
