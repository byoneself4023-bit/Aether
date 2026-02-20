# Docker Compose 통합 테스트 결과

## 개요

| 항목 | 내용 |
|------|------|
| 목표 | Docker Compose로 6개 컨테이너 기동 후 E2E 사용자 흐름 테스트 |
| 환경 | Docker 28.3.3, Docker Compose v2.39.2, macOS (darwin 24.6.0) |
| 서비스 | postgres, redis, auth-service, portfolio-service, llm-service, frontend |
| 결과 | **10/10 시나리오 통과**, 8개 이슈 발견 및 수정 |

---

## 서비스 구성

### 컨테이너 구성표

| 컨테이너 | 이미지 | 포트 (호스트:컨테이너) | 의존성 | Health Check |
|----------|--------|----------------------|--------|-------------|
| aether-postgres | postgres:16-alpine | 5433:5432 | - | `pg_isready` |
| aether-redis | redis:7-alpine | 6380:6379 | - | `redis-cli ping` |
| aether-auth | Spring Boot 3.2.12 (custom) | 8003:8003 | postgres, redis | `/actuator/health` |
| aether-portfolio | FastAPI (custom) | 8001:8001 | - | `/health` |
| aether-llm | FastAPI (custom) | 8002:8002 | portfolio-service | `/health` |
| aether-frontend | Next.js 16 (custom) | 3000:3000 | auth, portfolio, llm | `wget localhost:3000` |

### 네트워크

- **aether-network** (bridge): 모든 컨테이너가 동일 네트워크에 연결
- 서비스 간 통신은 컨테이너 이름을 hostname으로 사용
  - `http://postgres:5432` (auth → DB)
  - `http://redis:6379` (auth → Redis)
  - `http://portfolio-service:8001` (llm → portfolio)

### 환경변수 흐름

```
.env (호스트)
  ├── GEMINI_API_KEY → GOOGLE_API_KEY (llm-service)
  ├── POSTGRES_USER/PASSWORD → SPRING_DATASOURCE_* (auth-service)
  ├── JWT_SECRET → jwt.secret (auth-service)
  └── CORS_ORIGINS → cors.allowed-origins (auth-service)
```

---

## 테스트 시나리오 & 결과

### A. 인증 흐름 (Auth-Service)

#### A1. 회원가입 ✅

```bash
curl -s -X POST http://localhost:8003/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@aether.com","password":"TestPass1@","name":"테스터"}'
```

**응답**: `201 Created`
```json
{"success": true, "data": {"id": 1, "email": "test@aether.com", "name": "테스터"}}
```

---

#### A2. 로그인 ✅

```bash
curl -s -X POST http://localhost:8003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@aether.com","password":"TestPass1@"}'
```

**응답**: `200 OK` — accessToken + refreshToken 발급
```json
{"success": true, "data": {"accessToken": "eyJhbG...", "refreshToken": "eyJhbG..."}}
```

---

#### A3. 내 정보 조회 ✅

```bash
curl -s http://localhost:8003/api/auth/me \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**응답**: `200 OK`
```json
{"success": true, "data": {"id": 1, "email": "test@aether.com", "name": "테스터", "role": "USER"}}
```

---

#### A4. 토큰 갱신 ✅

```bash
curl -s -X POST http://localhost:8003/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken": "${REFRESH_TOKEN}"}'
```

**응답**: `200 OK` — 새 accessToken + refreshToken 쌍 발급

---

#### A5. 로그아웃 ✅

```bash
curl -s -X POST http://localhost:8003/api/auth/logout \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

**응답**: `200 OK` — access token 블랙리스트 등록, refresh token 삭제

---

### B. 포트폴리오 흐름 (Portfolio-Service)

#### B1. 포트폴리오 최적화 ✅

```bash
curl -s -X POST http://localhost:8001/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"tickers":["AAPL","MSFT","GOOGL","AMZN"],"strategy":"max_sharpe","period":"1y","rf":0.04}'
```

**응답**: `200 OK` — 최적 비중 + 드리프트 경고 포함
```json
{
  "weights": {"AAPL": 0.0, "MSFT": 0.0, "GOOGL": 1.0, "AMZN": 0.0},
  "metrics": {"expected_return": 0.552838, "volatility": 0.310527, "sharpe_ratio": 1.6515},
  "drift_warning": {"has_drift": true, "severity": "critical", "drift_type": "combined"}
}
```

---

#### B2. 백테스트 ✅

```bash
curl -s -X POST http://localhost:8001/api/backtest \
  -H "Content-Type: application/json" \
  -d '{"tickers":["AAPL","MSFT","GOOGL","AMZN"],"strategy":"max_sharpe","period":"3y","train_window":252,"rebalance_every":63}'
```

**응답**: `200 OK` — walk-forward 백테스트 결과
```json
{
  "metrics": {
    "total_return": 0.186152, "annual_return": 0.090416,
    "annual_volatility": 0.258604, "sharpe_ratio": 0.2723,
    "max_drawdown": 0.328639, "win_rate": 0.5372
  },
  "rebalance_count": 8,
  "portfolio_values": [{"date": "2024-02-23", "value": 0.998257}, ...]
}
```

---

#### B3. 리스크 분석 ✅

```bash
curl -s -X POST http://localhost:8001/api/risk \
  -H "Content-Type: application/json" \
  -d '{"tickers":["AAPL","MSFT","GOOGL"],"weights":{"AAPL":0.4,"MSFT":0.3,"GOOGL":0.3},"period":"1y","confidence":0.95,"n_simulations":10000}'
```

**응답**: `200 OK` — VaR, CVaR, Monte Carlo 리스크 분석
```json
{
  "parametric_var": {"value": 0.022573, "confidence": 0.95, "method": "parametric"},
  "monte_carlo_var": {"value": 0.022892, "confidence": 0.95, "method": "monte_carlo"},
  "cvar": 0.029257,
  "risk_summary": {"volatility": 0.226361, "max_loss_1d": 0.043241}
}
```

---

### C. LLM 흐름 (LLM-Service)

#### C1. RAG 채팅 ✅

```bash
curl -s -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"분산투자의 장점을 알려줘","session_id":"test-session"}'
```

**응답**: `200 OK` — RAG 기반 한국어 상세 응답 + 참고 소스
```json
{
  "response": "분산투자는 포트폴리오 이론의 핵심 개념으로...",
  "sources": ["Modern Portfolio Theory...", "Risk Management..."]
}
```

---

### D. 프론트엔드

#### D1. 페이지 로드 ✅

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

**응답**: `200` — Next.js 서버사이드 렌더링 정상

---

### 결과 요약

| # | 테스트 | 엔드포인트 | 결과 |
|---|--------|-----------|------|
| A1 | 회원가입 | POST /api/auth/signup | ✅ Pass |
| A2 | 로그인 | POST /api/auth/login | ✅ Pass |
| A3 | 내 정보 | GET /api/auth/me | ✅ Pass |
| A4 | 토큰 갱신 | POST /api/auth/refresh | ✅ Pass |
| A5 | 로그아웃 | POST /api/auth/logout | ✅ Pass |
| B1 | 포트폴리오 최적화 | POST /api/optimize | ✅ Pass |
| B2 | 백테스트 | POST /api/backtest | ✅ Pass |
| B3 | 리스크 분석 | POST /api/risk | ✅ Pass |
| C1 | RAG 채팅 | POST /chat | ✅ Pass |
| D1 | 프론트엔드 | GET / | ✅ Pass |

---

## 발견된 이슈 & 수정 (8개)

### 이슈 1: ENV 변수명 불일치

**증상**: llm-service에서 Google API 인증 실패, `GOOGLE_API_KEY` 환경변수가 빈 문자열

**원인**: docker-compose.yml에서 `GEMINI_API_KEY=${GEMINI_API_KEY}`로 전달했지만, llm-service의 `config.py`는 pydantic 필드명 `google_api_key`에 의해 `GOOGLE_API_KEY` 환경변수를 기대

```yaml
# Before
- GEMINI_API_KEY=${GEMINI_API_KEY}

# After
- GOOGLE_API_KEY=${GEMINI_API_KEY}
```

**교훈**: 환경변수 네이밍 컨벤션을 서비스 간 통일해야 한다. pydantic-settings는 필드명을 대문자로 변환하므로, docker-compose에서 전달하는 변수명과 일치하는지 반드시 확인.

---

### 이슈 2: 포트 충돌

**증상**: `docker compose up` 실패 — `bind: address already in use`

**원인**: 로컬 Postgres(5432), Redis(6379)가 이미 실행 중이어서 동일 포트 바인딩 불가

```yaml
# Before
ports:
  - "5432:5432"  # Postgres
  - "6379:6379"  # Redis

# After
ports:
  - "5433:5432"  # Postgres (로컬과 분리)
  - "6380:6379"  # Redis (로컬과 분리)
```

**교훈**: 호스트 포트 매핑은 로컬 개발 환경을 고려해야 한다. 컨테이너 간 통신은 내부 포트(5432, 6379)를 그대로 사용하므로, 호스트 포트만 변경하면 서비스 간 통신에 영향 없음.

---

### 이슈 3: prometheus_client 모듈 누락

**증상**: portfolio-service 컨테이너 기동 실패
```
ModuleNotFoundError: No module named 'prometheus_client'
```

**원인**: `app/metrics.py`에서 `prometheus_client`를 import하지만 `requirements.txt`에 미등록

```diff
# portfolio-service/requirements.txt
+ prometheus-client==0.19.0
```

**교훈**: 코드에서 import하는 모든 패키지는 requirements.txt에 반드시 명시해야 한다. `pip freeze`로 의존성을 관리하거나, CI에서 clean install 테스트를 실행하면 사전에 잡을 수 있다.

---

### 이슈 4: yfinance 429 Too Many Requests

**증상**: Yahoo Finance API 호출 시 429 에러 반환
```
YFRateLimitError: Too Many Requests. Rate limited. Try after a while.
```

**원인**: yfinance 0.2.33이 최신 Yahoo Finance API의 rate limiting 대응 로직(재시도, 쿠키 관리)이 부족

```diff
# portfolio-service/requirements.txt
- yfinance==0.2.33
+ yfinance>=0.2.40
```

실제 설치 버전: `yfinance 1.2.0` (최신 안정 버전으로 해석됨)

**교훈**: 외부 API에 의존하는 라이브러리는 주기적으로 업데이트가 필요하다. 특히 yfinance처럼 비공식 API를 사용하는 라이브러리는 제공자 측 변경에 빠르게 대응해야 한다.

---

### 이슈 5: yfinance 1.x API Breaking Change

**증상**: 가격 데이터 처리 시 타입 에러
```
ValueError: too many values to unpack
```

**원인**: yfinance 1.x에서 `yf.download()`의 반환 형식이 변경됨
- **0.2.x**: 단일 티커 → `data["Close"]`가 `pd.Series` 반환
- **1.x**: 단일 티커도 MultiIndex columns → `data["Close"]`가 `pd.DataFrame` 반환

```python
# Before (yfinance 0.2.x 가정)
prices = data["Close"]
if isinstance(prices, pd.Series):
    prices = prices.to_frame(tickers[0])

# After (yfinance 1.x 호환)
prices = data["Close"]
if isinstance(prices, pd.Series):
    prices = prices.to_frame(tickers[0])
# fetch_single_ticker_prices에서도:
close = data["Close"]
if isinstance(close, pd.DataFrame):
    return close.iloc[:, 0]
return close
```

**교훈**: 메이저 버전 업그레이드 시 반환 타입 변경을 반드시 확인해야 한다. `isinstance` 방어 코드를 추가하면 하위/상위 호환성을 모두 지원할 수 있다.

---

### 이슈 6: Google 임베딩 모델 Deprecation

**증상**: LLM 채팅 시 임베딩 생성 404 에러
```
404 Not Found: models/embedding-001 is not found
```

**원인**: `models/embedding-001`이 Google API에서 폐기(deprecated)됨. `models/text-embedding-004`도 동일하게 404.

```python
# Before
embedding_model: str = "models/embedding-001"

# After
embedding_model: str = "models/gemini-embedding-001"
```

사용 가능한 모델은 `genai.list_models()`로 확인:
```
models/gemini-embedding-001  ← 현재 활성
```

**교훈**: 외부 AI 모델 API는 deprecation 주기가 빠르다. 모델명을 환경변수로 외부화하고, health check에서 모델 접근 가능 여부를 확인하면 장애를 조기에 감지할 수 있다.

---

### 이슈 7: ChromaDB 벡터 차원 불일치

**증상**: 임베딩 저장 시 차원 에러
```
ValueError: Embedding dimension 3072 does not match collection dimensionality 768
```

**원인**: 기존 ChromaDB 데이터가 `embedding-001` (768차원)으로 생성되었는데, 새 모델 `gemini-embedding-001`은 3072차원 벡터를 생성

```bash
# 기존 벡터스토어 삭제 (Docker volume)
docker volume rm aether_llm_chroma_data
docker compose restart llm-service
```

**교훈**: 임베딩 모델을 변경하면 벡터스토어 마이그레이션이 필요하다. 프로덕션에서는 모델 변경 시 기존 데이터를 새 모델로 재임베딩하는 마이그레이션 스크립트를 준비해야 한다.

---

### 이슈 8: API 타임아웃 (핵심 — 가장 어려웠던 이슈)

**증상**: `/api/optimize` 호출 시 무한 대기 → 타임아웃 (30초 후 400 반환)

**원인 분석 과정**:

1. **yfinance가 Docker 안에서 안 되나?**
   ```bash
   docker exec aether-portfolio python3 -c "import yfinance; print(yfinance.download('AAPL', period='5d'))"
   ```
   → 정상 동작. yfinance 문제 아님.

2. **최적화 로직이 hang?**
   ```bash
   docker exec aether-portfolio python3 -c "
   from app.services.data import get_returns_and_covariance_resilient
   result = get_returns_and_covariance_resilient(['AAPL','MSFT'], period='1y')
   print(result.successful_tickers)
   "
   ```
   → 정상 동작. 로직 문제 아님.

3. **async def 안에서 blocking I/O?**
   - 모든 라우터 엔드포인트가 `async def`로 선언
   - 내부에 `await`가 단 하나도 없음
   - yfinance, scipy, MLflow 모두 synchronous blocking I/O
   - `async def` + blocking I/O = 이벤트 루프 블로킹
   → 부분적으로 맞지만, 이것만으로는 "첫 요청도 실패"하는 현상을 설명 못함

4. **최종 원인: `BaseHTTPMiddleware` + `await request.body()` + `def` 엔드포인트의 조합**
   - `RequestLoggingMiddleware`(BaseHTTPMiddleware)에서 `await request.body()`로 요청 body를 읽음
   - `async def` → `def`로 변경하면 FastAPI가 threadpool에서 엔드포인트를 실행
   - BaseHTTPMiddleware의 `call_next`가 `def` 엔드포인트와 통신할 때 request stream이 이미 소비되어 있으면 **deadlock 발생**
   - 이벤트 루프에서 body stream이 해제되기를 기다리는 동안, threadpool의 엔드포인트도 body를 읽으려 대기 → 상호 교착

**수정**:

```python
# 1. async def → def (FastAPI가 자동으로 threadpool에서 실행)

# Before (4개 라우터, 8개 엔드포인트)
@router.post("/optimize")
async def optimize_portfolio(request: OptimizeRequest):
    # blocking yfinance, scipy 호출... await 없음
    data_result = get_returns_and_covariance_resilient(...)

# After
@router.post("/optimize")
def optimize_portfolio(request: OptimizeRequest):
    # threadpool에서 실행되므로 이벤트 루프 블로킹 없음
    data_result = get_returns_and_covariance_resilient(...)
```

```python
# 2. 미들웨어에서 body 로깅 제거 (stream 충돌 방지)

# Before
request_body = None
if request.method in ["POST", "PUT", "PATCH"]:
    body_bytes = await request.body()
    if body_bytes:
        request_body = json.loads(body_bytes.decode("utf-8"))

logger.info("request_started", body=request_body, ...)

# After
logger.info("request_started", ...)  # body 로깅 없이
```

**수정된 파일** (8개 엔드포인트):
- `optimize.py`: `optimize_portfolio` (1개)
- `backtest.py`: `run_backtest` (1개)
- `risk.py`: `analyze_risk` (1개)
- `experiment.py`: 5개 (`run_optimize_experiment`, `compare_methods`, `run_backtest_exp`, `get_results`, `get_best`)
- `middleware/logging.py`: body 로깅 제거

**교훈**: FastAPI에서 `async def` vs `def` 선택은 **성능이 아니라 정확성의 문제**다.

| 상황 | 올바른 선택 |
|------|-----------|
| `await` 호출이 있는 경우 (httpx, DB async 드라이버) | `async def` |
| blocking I/O가 있는 경우 (yfinance, requests, 파일 I/O) | `def` |
| CPU-bound 계산만 있는 경우 (numpy, scipy) | `def` |

또한 Starlette의 `BaseHTTPMiddleware`에서 `await request.body()`를 호출하면 request stream을 소비하므로, `def` 엔드포인트와 함께 사용할 때 deadlock이 발생할 수 있다.

---

## 수정된 파일 목록

| 파일 | 관련 이슈 | 변경 내용 |
|------|-----------|----------|
| `docker-compose.yml` | #1, #2 | ENV 변수명 수정, 호스트 포트 변경 |
| `portfolio-service/requirements.txt` | #3, #4 | prometheus-client 추가, yfinance 업그레이드 |
| `portfolio-service/app/services/data_provider.py` | #5 | yfinance 1.x 호환 (instanceof 체크) |
| `portfolio-service/app/routers/optimize.py` | #8 | `async def` → `def` |
| `portfolio-service/app/routers/backtest.py` | #8 | `async def` → `def` |
| `portfolio-service/app/routers/risk.py` | #8 | `async def` → `def` |
| `portfolio-service/app/routers/experiment.py` | #8 | `async def` → `def` (5개 엔드포인트) |
| `portfolio-service/app/middleware/logging.py` | #8 | body 로깅 제거 |
| `llm-service/app/config.py` | #6 | 임베딩 모델명 변경 |

---

## 최종 서비스 상태

```
aether-postgres    ✅ Healthy  (5433:5432)
aether-redis       ✅ Healthy  (6380:6379)
aether-auth        ✅ Healthy  (8003:8003)
aether-portfolio   ✅ Healthy  (8001:8001)
aether-llm         ✅ Healthy  (8002:8002)
aether-frontend    ✅ Running  (3000:3000)
```

6개 컨테이너 전부 정상 기동, 10/10 테스트 통과.

---

## 단위 테스트 vs 통합 테스트

### 8개 이슈 중 단위 테스트로 잡을 수 있었던 것: 0개

| 이슈 | 단위 테스트로 발견 가능? | 이유 |
|------|----------------------|------|
| #1 ENV 변수명 불일치 | ❌ | 단위 테스트는 `.env`를 읽지 않고 mock 값 사용 |
| #2 포트 충돌 | ❌ | 네트워크 레벨 문제, 코드와 무관 |
| #3 모듈 누락 | ❌ | 단위 테스트 환경에는 이미 설치되어 있을 수 있음 |
| #4 yfinance 429 | ❌ | 외부 API rate limiting, mock으로 테스트 시 발견 불가 |
| #5 yfinance API 변경 | ❌ | mock 데이터는 고정 형식, 실제 반환값 변경 감지 불가 |
| #6 임베딩 모델 폐기 | ❌ | mock API는 항상 성공 |
| #7 ChromaDB 차원 불일치 | ❌ | 테스트용 vectorstore는 매번 새로 생성 |
| #8 async/middleware 충돌 | ❌ | 단위 테스트의 TestClient는 미들웨어를 다르게 처리 |

### 통합 테스트의 가치

- **환경변수 불일치**: 서비스 간 환경변수 전달은 코드 리뷰만으로 잡기 어렵다
- **포트 충돌**: 실제 배포 환경에서만 발생하는 인프라 이슈
- **외부 API 변경**: 실제 API 호출 없이는 감지 불가능한 breaking change
- **런타임 호환성**: 라이브러리 메이저 버전 업의 실제 영향
- **미들웨어 충돌**: 프레임워크 내부 동작(이벤트 루프, stream 관리)이 엔드포인트 구현 방식과 상호작용하는 미묘한 문제
- **데이터 볼륨 호환성**: 이전 데이터와 새 모델 간의 차원 불일치

**결론**: 단위 테스트는 "코드가 맞는지" 확인하고, 통합 테스트는 "시스템이 동작하는지" 확인한다. 이 프로젝트에서 발견된 8개 이슈는 모두 **서비스 간 경계**에서 발생한 것으로, 통합 테스트 없이는 프로덕션 배포 후에야 발견되었을 문제들이다.
