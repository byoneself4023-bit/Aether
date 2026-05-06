# ADR 0004 — 도메인 라우터 JWT 검증 + X-Request-ID 분산 트레이싱

- **상태**: Accepted
- **일자**: 2026-05-01
- **관련 작업**: H-10 + L-7 (`docs/agent-capability-audit/phase3/08_H-10_L-7_jwt_and_request_id.md`)

---

## 컨텍스트

Phase 1 As-Is 감사는 두 결함을 적시했다:

1. **01:§1** — `llm-service` / `portfolio-service` 도메인 라우터에 JWT 검증 코드가 0건. LLM 비용·연산 엔드포인트가 사실상 공개 노출 (인증 우회 가능).
2. **04:§3** — 두 서비스는 자체 미들웨어로 X-Request-ID를 *발급*은 하지만 `llm-service` → `portfolio-service` 호출 시 forward되지 않음. 한 사용자 요청을 두 서비스 로그에서 일렬 추적 불가.

T-2 (MCP 서버) 진입 전 호출자 인증 베이스 + 분산 트레이싱이 정착돼야 한다.

---

## 결정

### 1. JWT 검증: HS512 공유 비밀키 (단일 알고리즘)

`auth-service`가 `Keys.hmacShaKeyFor(jwtProperties.getSecret())` (`JwtTokenProvider.java:41-43`)로 토큰을 발급한다. jjwt 라이브러리는 비밀키 길이가 64 bytes 이상일 때 자동으로 **HS512**를 선택하며, 본 프로젝트의 `JWT_SECRET`은 이 임계값을 충족해 실측 발급 토큰 헤더가 `{"alg":"HS512"}`로 확정된다 (F-1 검증 결과 인용).

python 서비스(llm/portfolio)는 동일 비밀키 + `pyjwt.decode(..., algorithms=["HS512"])`로 검증한다 (`*/middleware/auth.py`).

- 비밀키는 환경변수 `JWT_SECRET`로 주입. `docker-compose.yml`에서 세 서비스(auth/llm/portfolio)가 동일 값 공유.
- FastAPI dependency: `app/middleware/auth.py::verify_jwt` — Authorization 헤더가 없거나 디코드 실패 시 401.
- **검증 측 일관성 의무**: 발급 알고리즘 변경 시 검증 측 `algorithms=[...]` 동시 갱신. 단일 알고리즘 명시 (호환 모드 X — 보안 약화 방지).

### 2. 적용 단위: 라우터 시그니처에 1줄 추가

```python
async def endpoint(
    request: SomeRequest,
    user: dict = Depends(verify_jwt),
) -> SomeResponse: ...
```

미들웨어가 아닌 dependency를 택한 이유:

- **선택적 면제**: 헬스체크/Prometheus scrape는 토큰을 전달하지 못한다. dependency는 라우터별 opt-in이라 자연스럽게 면제 가능.
- **payload 주입**: 향후 `user["sub"]`로 호출자 식별 (T-2 MCP 호출자 식별 베이스).

### 3. X-Request-ID forward: httpx event_hooks

```python
async def _forward_headers(request: httpx.Request) -> None:
    if rid := request_id_var.get(""):
        request.headers["X-Request-ID"] = rid[:64]
    if token := auth_token_var.get(""):
        request.headers["Authorization"] = f"Bearer {token}"

httpx.AsyncClient(..., event_hooks={"request": [_forward_headers]})
```

미들웨어가 ContextVar로 RID를 발급하고, `verify_jwt`가 디코드한 토큰을 별도 ContextVar(`auth_token_var`)에 set한다. httpx 호출 시 hook이 두 ContextVar를 읽어 헤더로 forward.

### 4. 토큰 로그 마스킹

`logging.py`의 포매터가 출력 직전 regex (`Bearer\s+[A-Za-z0-9._\-]+` → `Bearer ***`)로 마스킹한다. JSON dump 전체에 적용해 `extra` 필드까지 커버.

### 5. 기존 테스트 무수정 통과

`tests/conftest.py`의 autouse `_bypass_jwt` fixture가 기본적으로 `app.dependency_overrides[verify_jwt]`로 stub을 등록한다. 실제 검증 로직을 테스트하려면 `@pytest.mark.no_jwt_bypass` 마커로 opt-out.

---

## 본질 — 인증을 미들웨어가 아닌 자산으로

H-10은 단순 보안 패치가 아니다. **호출자 정보를 모든 도메인 라우터가 1급(first-class) 인자로 받는다는 선언**이다.

- 미들웨어 방식이라면 라우터가 호출자를 모른다 → MCP 서버에서 누가 도구를 호출했는지 추적 불가.
- dependency 방식이라면 `user: dict`가 라우터 시그니처에 명시되고, 향후 권한 검사·감사 로그·rate-limit 키로 전부 활용 가능.

이 선택은 T-2(MCP)·T-1(LangGraph)에서 호출자별 도구 ACL과 trace에 그대로 재사용된다.

---

## 면제 7건 (라우터별 위치)

| 서비스 | 메서드 | 경로 | 위치 | 면제 사유 |
|---|---|---|---|---|
| llm | GET | `/health` | `app/main.py:69` | Jenkins/docker healthcheck |
| llm | GET | `/` | `app/main.py:107` | root info |
| llm | GET | `/api/chat/health` | `app/routers/chat.py:451` | chat 모듈 헬스 |
| llm | GET | `/api/metrics/tokens` | `app/routers/metrics.py:13` | Prometheus scrape |
| portfolio | GET | `/health` | `app/main.py:44` | Jenkins/docker healthcheck |
| portfolio | GET | `/` | `app/main.py:56` | root info |
| portfolio | GET | `/metrics` | `app/routers/metrics.py:11` | Prometheus scrape |

`/health` `/metrics` 보호 시 `docker-compose.yml` healthcheck + `prometheus.yml` scrape 설정 변경이 필요하다 — 본 카드 범위(외부 인프라 손대지 않음) 밖이라 면제.

---

## 향후 검토 사항 (별도 카드)

### H-10b — RS256 + JWKS 마이그레이션

HS512는 비밀키가 모든 서비스에 평문으로 분산된다. 환경변수 leak 시 토큰 위조 가능. RS256으로 마이그레이션하면:

- `auth-service`만 RSA 사설키 보유 (서명).
- `llm-service` / `portfolio-service`는 공개키만 보관 (검증).
- `auth-service`에 JWKS 엔드포인트(`/.well-known/jwks.json`) + `kid` 헤더로 키 회전 지원.

마이그레이션 비용:

- `auth-service` JWKS 컨트롤러 + Spring Security 재설정 (2~3 파일 신규).
- `llm-service` / `portfolio-service`는 `pyjwt`의 `JWKClient` + `algorithms=["RS256"]`로 변경 (verify_jwt 1 함수 수정).
- 기존 발급 토큰 호환을 위한 마이그레이션 윈도우 (RS256 + HS512 dual-verify) 단계 필요.

본 카드(H-10/L-7) 책임은 "verify_jwt 정착"이지 "auth-service 알고리즘 변경"이 아니므로 분리 (CLAUDE.md §6 1카드 1책임). H-10b는 보안 취약 분석 강도가 올라갈 때 우선순위 격상.

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-01 | v1 | 초기 Accepted (H-10 + L-7 카드 산출) — HS256 명시 |
| 2026-05-06 | v2 | F-1 (PR #20) 검증에서 auth-service 실측 발급 알고리즘이 **HS512**임을 확인 (jjwt 자동 선택). portfolio/llm 검증 측 `algorithms=["HS256"]` 누락 동기화로 도메인 라우터 3개 (optimize/backtest/chat) 401 차단. F-1a 카드에서 양 측 HS512 통일 + "검증 측 일관성 의무" 명시 추가. |

### L-7b — 분산 trace ID 표준 (W3C Trace Context)

현재는 단순 X-Request-ID. OpenTelemetry / W3C `traceparent` 헤더로 확장 시 분산 trace 시스템(Tempo/Jaeger)과 직접 연동 가능. T-1 / Phase 4 관측성 카드에서 다룬다.

---

## 영향

- 신규 도메인 라우터 추가 시 `Depends(verify_jwt)`가 시그니처에 포함돼야 한다 (PR 리뷰에서 검증).
- llm → portfolio 외 서비스 간 httpx 호출이 추가되면 동일한 event_hooks를 등록해야 한다.
- 토큰을 로그에 직접 출력하는 신규 코드는 ADR 위반 (마스킹 자동 처리되지만 의도 자체를 회피).
- T-2 (MCP) 카드는 본 ADR이 보장한 `user: dict` 시그니처를 전제로 호출자별 도구 ACL을 설계.
- AGENTS.md §9 "인증 · 분산 트레이싱"이 본 ADR의 운영 인덱스.
