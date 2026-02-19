# ADR-007: FastAPI Sync 엔드포인트 선택

## 상태: Accepted

---

## 맥락 (Context)

portfolio-service의 모든 API 엔드포인트(`/api/optimize`, `/api/backtest`, `/api/risk`, `/api/experiment/*`)가 `async def`로 선언되어 있었지만, 내부에 `await`가 단 하나도 없었다. yfinance(네트워크 I/O), scipy(CPU-bound), MLflow(파일 I/O)가 모두 synchronous blocking 라이브러리였다.

**Docker Compose 통합 테스트에서 발견된 문제**:
- `/api/optimize` 호출 시 무한 대기 → 타임아웃
- `docker exec`로 컨테이너 내부에서 직접 Python 실행하면 정상 동작
- API 엔드포인트를 통해서만 hang 발생
- 원인: `async def` + blocking I/O → 이벤트 루프 블로킹 + `BaseHTTPMiddleware`의 body stream 충돌

---

## 고려한 선택지

### 옵션 A: async def + asyncio.to_thread()

```python
@router.post("/optimize")
async def optimize(request: OptimizeRequest):
    result = await asyncio.to_thread(
        get_returns_and_covariance_resilient,
        tickers=request.tickers, period=request.period
    )
```

- **장점**: 기존 `async def` 시그니처 유지, 명시적으로 blocking 코드를 threadpool로 위임
- **단점**: 모든 blocking 호출마다 `to_thread()` 래핑 필요 → 코드 노이즈, 래핑 누락 시 여전히 블로킹, 미들웨어 body 충돌 문제는 별도 해결 필요

### 옵션 B: def (sync) — FastAPI 자동 threadpool 실행

```python
@router.post("/optimize")
def optimize(request: OptimizeRequest):
    result = get_returns_and_covariance_resilient(...)
```

- **장점**: FastAPI가 `def`를 감지하면 자동으로 threadpool에서 실행 → 코드 변경 최소 (`async` 키워드만 제거), 모든 blocking I/O가 자동으로 threadpool에서 실행
- **단점**: 함수 내에서 `await` 사용 불가, threadpool 크기 기본값(40)에 의존

### 옵션 C: async def + httpx/aiohttp로 전환

```python
@router.post("/optimize")
async def optimize(request: OptimizeRequest):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://yahoo.finance/...")
```

- **장점**: 진정한 async — 이벤트 루프 블로킹 제로
- **단점**: yfinance를 httpx로 대체해야 함 → Yahoo Finance API를 직접 구현, scipy/MLflow는 async 버전이 없음 → 결국 일부는 `to_thread()` 필요, 대규모 리팩토링

---

## 결정 (Decision)

**옵션 B: def (sync)** 선택.

```python
# Before: async def — 이벤트 루프에서 직접 실행 → blocking
@router.post("/optimize")
async def optimize_portfolio(request: OptimizeRequest):
    data = get_returns_and_covariance_resilient(...)  # 30초간 이벤트 루프 블로킹
    result = optimize_min_variance(mu, cov)           # CPU-bound
    return OptimizeResponse(...)

# After: def — FastAPI가 threadpool에서 자동 실행
@router.post("/optimize")
def optimize_portfolio(request: OptimizeRequest):
    data = get_returns_and_covariance_resilient(...)  # threadpool에서 실행
    result = optimize_min_variance(mu, cov)           # threadpool에서 실행
    return OptimizeResponse(...)
```

추가로 `RequestLoggingMiddleware`에서 `await request.body()` 호출을 제거:

```python
# Before: body stream 소비 → def 엔드포인트와 deadlock
body_bytes = await request.body()
request_body = json.loads(body_bytes.decode("utf-8"))
logger.info("request_started", body=request_body, ...)

# After: body 로깅 제거
logger.info("request_started", method=request.method, path=request.url.path, ...)
```

**선택 이유**:
- 코드 변경 최소: `async def` → `def`로 8개 엔드포인트에서 `async` 키워드만 제거
- 자동 threadpool: FastAPI가 `def` 함수를 감지하면 `anyio.to_thread.run_sync()`로 자동 래핑 → 개발자가 래핑을 잊을 위험 없음
- 미들웨어 호환: `def` 엔드포인트는 threadpool에서 실행되므로 `BaseHTTPMiddleware`의 body stream 관리와 충돌하지 않음 (body 로깅 제거 시)
- yfinance, scipy, MLflow 모두 sync 라이브러리 → async로 전환하는 것은 비용 대비 이득 없음

---

## 결과 (Consequences)

**장점**:
- 타임아웃 해소: 무한 대기 → 정상 응답 (5~15초)
- 동시 처리: threadpool 기본 40 워커 → 동시 40개 요청까지 병렬 처리
- 이벤트 루프 보호: health check, WebSocket 등 async 작업이 블로킹되지 않음
- 코드 변경 최소: 8줄 수정 (각 엔드포인트에서 `async` 제거)

**트레이드오프**:
- threadpool 크기 제한: 기본 40 → 동시 40개 이상의 최적화 요청이 오면 큐잉
- `await` 사용 불가: 향후 async DB 드라이버 도입 시 다시 `async def`로 전환 필요
- body 로깅 제거: 요청 body 디버깅이 필요하면 엔드포인트 내부에서 로깅해야 함

---

## 재선택한다면?

같은 선택. FastAPI 공식 문서에서도 "blocking I/O가 있으면 `def`를 사용하라"고 권장한다. yfinance를 async HTTP 클라이언트로 대체하는 것은 비용 대비 이득이 없고, scipy/MLflow는 async 버전이 존재하지 않는다.

향후 고부하 환경에서는 Uvicorn 워커 수(`--workers 4`) + threadpool 크기 조정(`ANYIO_BACKEND_OPTIONS`)으로 스케일링하는 것이 합리적이다.
