# AUDIT_REPORT — Aether 시니어 관점 전체 진단 (AUDIT-1)

> **본질**: I-1-REVIEW (PR #47 / c249657) 머지 후 Aether 4 서비스 (auth Spring Boot Java / portfolio + llm FastAPI Python / frontend Next.js TypeScript) 시니어 관점 전체 진단. 발견만 / 수정 X / 별도 디벨롭 카드 트리거. 8 카테고리 × 4 서비스 = 22 발견 항목 (Critical 3 / Major 11 / Minor 8) + Green 정상 영역 영역 영역.
> **카드**: AUDIT-1 (시니어 관점 전체 진단 / 보고서 카드 / ADR X)
> **작성일**: 2026-05-09
> **선행 카드**: I-1-REVIEW (PR #47 / c249657 / 면접 답변 자료 인용 정정 14건)
> **인용 자료** (5건): TEST_REPORT.md (TG-2d 시연 결과 / DBG-1+DBG-2 트리거) + INTERVIEW_SIMULATION.md §10 (자가 검증 패턴) + WORK_PATTERNS.md (18 누적 + 5 가드) + PRINCIPLES.md (10 패턴 / 양면 정책) + ADR/README.md (15 양면 정책 분류) + AGENTS.md §7 (지배 숫자)
>
> **검증 도구**: Claude Code 4 서비스 코드 직접 정독 + 3 Explore 병렬 진단 (Group A 보안+에러+동시성 / Group B 성능+관찰성+테스트 / Group C 일관성+코드 품질) + 본인 검증 (자가 검증 패턴 / 영역 의무) → 발견 항목 영역 본인 검증 후 정정. 추측 X / 실측 본문만.

---

## §0 본질 + 진단 범위 + 통계

### §0.1 진단 범위

| 항목 | 값 |
|---|---|
| 진단 시점 | 2026-05-09 (I-1-REVIEW 머지 후) |
| 검증 대상 | 4 서비스 (auth + portfolio + llm + frontend) + 3 인프라 (postgres + redis + qdrant) |
| 검증 카테고리 | 8 (보안 / 에러 / 동시성 / 성능 / 일관성 / 테스트 / 관찰성 / 코드 품질) |
| 검증 방식 | 4 서비스 코드 직접 정독 + 3 Explore 병렬 진단 + 본인 검증 (자가 검증 패턴) |
| 코드 변경 | 0 (발견 + 보고만 / 별도 디벨롭 카드 트리거) |

### §0.2 통계

| 우선순위 | 수 | 비율 | 시연 영향 |
|---|---|---|---|
| Critical | 3 | 14% | ✗ 차단 (DBG-1 / DBG-2 / FE-E2E) |
| Major | 11 | 50% | ⚠ 영향 (안정성 / 일관성 / 성능) |
| Minor | 8 | 36% | - 무관 (코드 품질 / 리팩토링) |
| **합계** | **22** | **100%** | - |

### §0.3 검증 영역 영역 영역 (자가 검증 패턴)

3 Explore agent 영역 영역 영역 영역 영역 영역 영역 영역 영역 — 본인 검증 영역 정정:

| Agent 발견 | 본인 검증 결과 | 정정 |
|---|---|---|
| (Group A) `.env` 영역 키 노출 Critical | ✗ 거짓 — `.gitignore` 영역 `.env` 영역 영역 / `git ls-files` 영역 `.env.example`만 영역 영역 | 본 보고서 영역 X |
| (Group C) portfolio + llm 마이그레이션 영역 Critical | ✗ 거짓 — portfolio + llm 영역 DB 영역 영역 영역 영역 (grep `create_engine` = 0건 / docker-compose 영역 auth-service만 DATABASE_URL) | 본 보고서 영역 X |
| (Group A) auth signup race condition Critical | ⚠ Major — User entity 영역 `@Column(unique=true)` ✓ + V1 SQL `UNIQUE` ✓ → DB constraint 영역 영역 영역 / 단 catch 영역 영역 영역 영역 500 영역 (DUPLICATE_EMAIL 영역 영역 X) | Major 영역 영역 정착 |

**시그널**: 본 자가 검증 = 면접 답변 영역 "어떻게 검증?" 질문 영역 = AUDIT_REPORT §0.3 영역 영역 (PRINCIPLES 패턴 10 / G1 본질 트리거 / I-1-REVIEW §10 일관성).

---

## §1 발견 항목 종합 (요약 표)

| # | 카테고리 | 우선순위 | 본문 (요약) | 시연 영향 | 디벨롭 카드 |
|---|---|---|---|---|---|
| 1 | 테스트 | Critical | Frontend E2E 테스트 부재 (5건 단순 "load" 테스트만 / API mock / 상호작용 / 로직 검증 X) | ✗ | DEV-FE-1 |
| 2 | 성능 | Critical | yfinance transient rate limit 영역 fallback 영역 (DBG-1 / TG-2d 발견 영역) | ✗ | DBG-1 (영역 영역) |
| 3 | 보안 | Critical | 이메일 형식 검증 영역 (Spring `@Email` 영역 영역 영역 / RFC 5322 영역 / DBG-2 / TG-2d 발견) | ✗ | DBG-2 (영역 영역) |
| 4 | 동시성 | Major | auth signup TOCTOU 영역 (DB unique constraint 영역 영역 / catch 영역 영역 영역 500 영역 영역 영역) | ⚠ | DEV-AUTH-1 |
| 5 | 코드 품질 | Major | JWT 검증 로직 DRY 위반 (llm + portfolio 98% 중복) | ⚠ | DEV-DRY-1 |
| 6 | 코드 품질 | Major | 함수 내 import 11+ 건 (CLAUDE.md §3 / memory 영역 위반) | ⚠ | DEV-IMPORT-1 |
| 7 | 에러 핸들링 | Major | 사용자 메시지 영역 예외 본문 노출 (chat / optimize / risk / backtest 영역 5+ 건) | ⚠ | DEV-ERR-1 |
| 8 | 코드 품질 | Major | 함수 복잡도 (chat() 73 LOC / optimize_portfolio() 120+ LOC) | ⚠ | DEV-COMPLEX-1 |
| 9 | 관찰성 | Major | portfolio-service health check 영역 (단순 "healthy" / DB+yfinance 영역 영역) | ⚠ | DEV-OBS-1 |
| 10 | 보안 | Major | auth-service CORS `allowedHeaders=*` (CorsConfig.java:26) | ⚠ | DEV-SEC-1 |
| 11 | 일관성 | Major | 에러 코드 체계 영역 (llm + portfolio HTTPException 영역 임시 문자열만 / auth ErrorCode enum 영역) | ⚠ | DEV-API-1 |
| 12 | 일관성 | Major | 로그 포맷 혼재 (llm-service unstructured f-string vs portfolio + auth structured) | ⚠ | DEV-LOG-1 |
| 13 | 에러 핸들링 | Major | `except Exception: pass` silent failure (portfolio data.py:328 / llm rag.py:198 / main.py:84/91) | ⚠ | DEV-ERR-2 |
| 14 | 테스트 | Major | yfinance / Gemini mock fixture 표준화 영역 (portfolio + llm tests / 실제 API 호출 가능성) | ⚠ | DEV-TEST-1 |
| 15 | 보안 | Minor | CSP 정책 세분화 영역 (`script-src` / `style-src` 명시 영역) | - | DEV-SEC-2 |
| 16 | 동시성 | Minor | Redis `set()` + `expire()` 영역 atomic 영역 영역 (`setex()` 영역 영역) | - | DEV-CONC-1 |
| 17 | 성능 | Minor | portfolio-service 동기 라우터 (`def` / yfinance.download 영역 thread pool 점유) | - | DEV-PERF-1 |
| 18 | 일관성 | Minor | health / RAG init endpoint 영역 `response_model` 영역 (FastAPI 영역) | - | DEV-API-2 |
| 19 | 관찰성 | Minor | frontend health check 결과 영역 X (UI feedback 영역 영역) | - | DEV-OBS-2 |
| 20 | 보안 | Minor | Frontend `NEXT_PUBLIC_*` 영역 endpoint 경로 노출 (의도적 / 영역 영역) | - | DEV-SEC-3 |
| 21 | 관찰성 | Minor | Prometheus `/metrics` 영역 영역 영역 영역 (portfolio metrics.py 영역 영역 영역 영역 영역 영역) | - | DEV-OBS-3 |
| 22 | 성능 | Minor | yfinance 캐시 미스 시 retry / exponential backoff 영역 (현 단순 호출) | - | DEV-PERF-2 |

**Green (정상 영역)**:

- JWT HS512 + Redis blacklist (auth-service / F-1a / ADR 0004 v2)
- httpx AsyncClient context manager (llm-service portfolio_client.py:43-50)
- portfolio-service + llm-service structured 로그 (JSON 포맷 + X-Request-ID forward)
- ADR 0013 페이지 분리 (frontend optimize 42 LOC / backtest 39 LOC)
- ADR 0019 SSE (chat.py:332-372 + react_agent.py:52-76)
- TODO/FIXME/HACK 주석 0건 (Clean Code 준수)
- TypeScript 타입 안전 (`: any` 0건)
- Python 타입 힌트 99% (CLAUDE.md §3 준수)
- Markowitz / walk-forward / Auto Research 영역 영역 영역 (TG-2d 시연 ✓)
- auth User entity `@Column(unique=true)` + V1 SQL `UNIQUE` (DB constraint 영역)

---

## §2 카테고리별 상세

### §2.1 보안 (Security)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 1 | DBG-2 / `auth-service/.../request/SignUpRequest.java` | Spring `@Email` annotation 영역 영역 검증만 (`@` 영역 영역 검증) | RFC 5322 영역 영역 영역 X — `foo@bar` 영역 정상 signup (TG-2d Edge-1 / id=19 영역) / TLD 영역 영역 영역 X | 시연 ✗ (Edge-1 영역 영역) + 면접 시그널 (DBG-2 인용) | Critical | DBG-2 (영역 영역 / Apache Commons Email Validator 또는 Hibernate `@Pattern` 강화) |
| 2 | `auth-service/.../config/CorsConfig.java:26` | `setAllowedHeaders(List.of("*"))` | 임의 헤더 주입 가능 — `X-Original-URL` / `X-Forwarded-For` 스푸핑 영역 영역 / D-2 (ADR 0012) 영역 영역 영역 = `[Authorization, Content-Type, X-Request-ID]` 영역 영역 | 운영 영역 영역 ⚠ | Major | DEV-SEC-1 (allowedHeaders 화이트리스트 영역 영역) |
| 3 | `llm-service/app/main.py + portfolio-service/app/main.py` | CSP `default-src 'self'` (HTTP 헤더) | `script-src` / `style-src` 명시 영역 영역 — 인라인 스크립트 / 스타일 차단 명확화 영역 | - | Minor | DEV-SEC-2 (CSP 정책 세분화) |
| 4 | `frontend/.env` | `NEXT_PUBLIC_AUTH_URL` 등 endpoint 노출 | 의도적 (브라우저 영역 호출) — 단 endpoint 경로 영역 = 정찰 영역 영역 영역 X | - | Minor | DEV-SEC-3 (영역 영역 endpoint 영역 영역 영역) |

**Green**:

- JWT HS512 + 64 bytes secret (`JwtTokenProvider.java:39-44`) ✓
- Redis blacklist (`JwtTokenProvider.java:116-130`) ✓
- `.env` git 영역 영역 (`.gitignore` 영역 영역) ✓
- `dangerouslySetInnerHTML` 0건 (frontend XSS 영역 영역) ✓
- SQL injection — JPA + Pydantic 영역 영역 영역 영역 ✓
- D-2 운영급 (ADR 0012 / CORS 명시 / API 키 검증 이중 / X-Request-ID forward) ✓

---

### §2.2 에러 핸들링 (Error Handling)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 5 | `llm-service/app/routers/chat.py:218-224, 248-253` | `except Exception as e: return ChatResponse(answer=f"...오류가 발생했습니다: {e}")` | 사용자 메시지 영역 예외 본문 영역 노출 — 스택 트레이스 / 구현 세부사항 영역 영역 영역 | ⚠ 정보 유출 | Major | DEV-ERR-1 (예외 본문 영역 영역 영역 영역 / `logger.error(exc_info=True)` 영역 분리) |
| 6 | `portfolio-service/app/routers/{optimize,risk,backtest}.py` | `except Exception as e: raise HTTPException(detail=f"Internal error: {str(e)}")` 5+ 건 | 동일 패턴 — 내부 에러 영역 client 영역 노출 / FastAPI exception_handler 영역 영역 | ⚠ | Major | DEV-ERR-1 |
| 7 | `portfolio-service/app/services/data.py:328` | `except Exception: pass` (silent catch) | 데이터 수집 실패 영역 영역 영역 영역 영역 영역 무시 — 디버깅 영역 영역 영역 / 근본 원인 영역 영역 영역 | ⚠ | Major | DEV-ERR-2 (silent failure 영역 / `logger.warning(exc_info=True)` 추가) |
| 8 | `llm-service/app/routers/rag.py:198-199 + main.py:84, 91` | 동일 silent catch 패턴 | 의존성 초기화 / 문서 조회 실패 영역 영역 영역 영역 영역 영역 영역 | ⚠ | Major | DEV-ERR-2 |
| 9 | `llm-service/app/services/portfolio_client.py:88` | `except Exception: error_detail = response.text` | 백엔드 5xx 응답 본문 영역 영역 영역 영역 영역 영역 — 정보 유출 가능 | ⚠ | Major | DEV-ERR-1 (응답 정규화) |

**Green**:

- `auth-service/.../GlobalExceptionHandler.java` ✓ — RuntimeException 영역 로그만 / `INTERNAL_SERVER_ERROR` 영역 영역 / 스택 트레이스 영역 영역 X
- `llm-service/app/services/llm_provider.py:144-148` ✓ — LLMError 영역 영역 / 비재시도 영역 재전파
- ErrorCode enum (`auth-service/.../ErrorCode.java`) ✓ — A001 / C002 / U002 등 9 영역 영역

---

### §2.3 동시성 (Concurrency)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 10 | `auth-service/.../AuthService.java:28-49 signUp()` | `@Transactional` + `existsByEmail` (line 31) → `save` (line 45) | TOCTOU race 영역 가능 — 단 User entity 영역 `@Column(unique=true)` ✓ + V1 SQL `UNIQUE` ✓ → DB constraint 영역 영역 영역 / **catch 영역 영역 영역 영역 500 영역 (DUPLICATE_EMAIL 영역 영역 X)** | ⚠ 사용자 경험 (500 vs 409) | Major | DEV-AUTH-1 (`DataIntegrityViolationException` catch + `DUPLICATE_EMAIL` 영역 영역 / 또는 try-catch unique constraint 영역) |
| 11 | `auth-service/.../JwtTokenProvider.java:74-90` | Redis `set()` + `expire()` (refresh token) | 단일 Redis 영역 영역 영역 영역 / `setex()` 영역 SET + EXPIRE atomic 영역 영역 영역 영역 | - | Minor | DEV-CONC-1 (`opsForValue().set(key, val, ttl, MILLISECONDS)` 또는 `setex` 영역 atomic 영역 영역) |

**Green**:

- llm-service async 라우터 (chat.py:174-330) ✓
- httpx AsyncClient context manager ✓
- Spring `@Transactional` 명시 ✓
- portfolio-service async 라우터 영역 (영역 영역 영역) — 영역 영역 §2.4 성능 영역 영역

---

### §2.4 성능 (Performance)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 12 | DBG-1 / `portfolio-service/app/services/data_provider.py:76-113` | `yfinance.download()` 동기 호출 + `threads=True` | TG-2c 영역 transient rate limit 영역 영역 영역 → TG-2d 영역 영역 영역 (transient 영역) — fallback / retry / cache miss 영역 영역 영역 영역 / FastAPI 영역 thread pool 점유 | ✗ 시연 (TG-2c 영역 영역 / TG-2d ✓ / 영역 transient) | Critical | DBG-1 (영역 영역 / `asyncio.to_thread` + exponential backoff retry + fallback data source) |
| 13 | `portfolio-service/app/routers/*.py` | 동기 라우터 (`def`) | I/O 바운드 작업 (yfinance.download / SQL) 영역 thread pool 점유 / 고부하 영역 throughput 저하 | ⚠ | Minor | DEV-PERF-1 (`async def` 영역 영역 / I/O 영역 `asyncio.to_thread`) |
| 14 | `portfolio-service/app/services/cache.py:1-386` | LRU + Redis fallback (CACHE_MAXSIZE=1000) | ✓ 캐시 영역 영역 영역 — 단 캐시 미스 영역 즉시 yfinance 호출 / retry 영역 | - | Minor | DEV-PERF-2 (캐시 미스 시 exponential backoff) |

**Green**:

- httpx AsyncClient (`portfolio_client.py:43-50`) ✓
- llm-service async 라우터 ✓
- auth-service `users(email)` 인덱스 (V1 SQL) ✓
- frontend 영역 N+1 영역 영역 (영역 영역 fetch / SWR 영역 영역) ✓
- llm_provider.py LRU 캐시 ✓
- LLM 호출 timeout 60s ✓

---

### §2.5 일관성 (Consistency)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 15 | `llm-service/app/routers/{health,rag}.py` | 일부 endpoint `response_model` 영역 영역 (raw dict return) | 응답 타입 영역 영역 영역 — Pydantic 영역 영역 영역 / OpenAPI 영역 영역 영역 영역 | - | Minor | DEV-API-2 (`response_model=...` 추가) |
| 16 | `llm-service + portfolio-service` HTTPException | `HTTPException(status_code=503, detail="Portfolio service is unavailable")` 영역 임시 문자열만 | 에러 코드 체계 X — auth-service 영역 ErrorCode enum 영역 / FastAPI 영역 영역 영역 영역 영역 | ⚠ 일관성 / API 클라이언트 영역 영역 영역 | Major | DEV-API-1 (FastAPI ErrorCode enum 영역 / 응답 형식 영역 영역) |
| 17 | `llm-service/app/routers/chat.py` 영역 | unstructured `logger.info(f"Chat request: ...")` | portfolio-service / auth-service 영역 structured 로그 (JSON) — llm-service 영역 영역 영역 / 영역 영역 영역 | ⚠ 분산 트레이싱 영역 영역 | Major | DEV-LOG-1 (llm-service 영역 structured 로그 영역 통일) |

**Green**:

- 네이밍 컨벤션 ✓ — Python snake_case / Java camelCase / TS camelCase + PascalCase
- ADR 준수 — ADR 0001 (단방향 호출 / 영역 영역 영역 호출 X) / ADR 0012 (CORS 영역) / ADR 0013 (페이지 분리) / ADR 0019 (SSE) ✓
- portfolio-service `response_model` 영역 ✓ (`@router.post("/optimize", response_model=OptimizeResponse)`)
- auth-service `ApiResponse<T>` 구조 영역 ✓
- frontend TypeScript 타입 정의 영역 ✓

---

### §2.6 테스트 커버리지 (Test Coverage)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 18 | `frontend/src/__tests__/` (5건) | Vitest "module load" 테스트만 (Dashboard / Chat / Backtest / Optimize / Header) | 실제 컴포넌트 렌더링 / 사용자 상호작용 / API mock 테스트 영역 — TG-2c 자동 시연 영역 영역 영역 영역 | ✗ 시연 영역 ⚠ + 면접 시그널 약함 | Critical | DEV-FE-1 (Vitest + MSW Mock Service Worker 또는 Playwright E2E 추가) |
| 19 | `portfolio-service/tests/` (12건) + `llm-service/tests/` (28건) | mock 사용 (645 + 88 LOC) | yfinance / Gemini / Qdrant mock fixture 표준화 영역 — 실제 API 호출 가능성 / pytest-vcr 영역 영역 | ⚠ 테스트 신뢰성 | Major | DEV-TEST-1 (mock fixture 표준화 / pytest-vcr 또는 responses) |
| 20 | `auth-service/.../test/` (8건) | AuthControllerTest / AuthServiceTest / JwtTokenProviderTest | edge case 영역 영역 영역 — 이메일 형식 (DBG-2) / 빈 비밀번호 / 영역 입력 / 영역 영역 | - (DBG-2 영역 영역) | Minor | DEV-TEST-2 (DBG-2 머지 후 edge case 테스트 영역) |

**테스트 합계**: 53 파일 (llm 28 / portfolio 12 / auth 8 / frontend 5) — AGENTS.md §7 영역 635 영역 (개별 테스트 함수 카운트 영역 영역).

**Green**:

- llm-service coverage 86% ✓ (PR 게이트 차단 / `--cov-fail-under=81`)
- AsyncMock / unittest.mock.patch 영역 영역 사용 ✓
- portfolio-service coverage 측정 영역 (PR 게이트 비차단)

---

### §2.7 관찰성 (Observability)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 21 | `portfolio-service/app/main.py:43-52` | `/health` 단순 `{"status": "healthy"}` | 의존성 검증 영역 영역 — DB / yfinance / 영역 영역 영역 / llm-service 영역 영역 (`api_key:ok / vectorstore:ok / portfolio_service:ok`) | ⚠ 장애 감지 지연 | Major | DEV-OBS-1 (llm-service 영역 강화) |
| 22 | `frontend/src/lib/api/{portfolio,llm}.ts` | health endpoint 호출 + 결과 영역 영역 X | UI feedback 영역 영역 — 실패 영역 fallback / banner 영역 | - | Minor | DEV-OBS-2 (connectivity banner 추가) |
| 23 | `portfolio-service/app/metrics.py:1-100` | Prometheus 메트릭 영역 영역 (Counter / Histogram / Gauge) | `/metrics` endpoint 영역 영역 영역 영역 영역 — 영역 영역 X / 영역 영역 영역 | - | Minor | DEV-OBS-3 (`/metrics` route 추가) |

**Green**:

- llm-service + portfolio-service structured 로그 (JSON 포맷) ✓
- X-Request-ID forward (httpx event_hooks / portfolio_client.py:17-22) ✓
- llm-service `/health` (api_key + vectorstore + portfolio_service 검증) ✓
- auth-service `/health` (DB + Redis ping) ✓
- Bearer 토큰 마스킹 ✓

---

### §2.8 코드 품질 (Code Quality)

| # | 위치 | 현재 상태 | 문제 | 영향 | 우선순위 | 디벨롭 |
|---|---|---|---|---|---|---|
| 24 | `llm-service/app/middleware/auth.py:14-42` ↔ `portfolio-service/app/middleware/auth.py:14-42` | `verify_jwt()` 98% 중복 (jwt.decode + ExpiredSignatureError + InvalidTokenError) | DRY 위반 — JWT 검증 로직 변경 시 2 곳 동시 수정 의무 / 위험 | ⚠ 유지보수 비용 ↑ | Major | DEV-DRY-1 (공유 패키지 추출 / 영역 PyPI / Git submodule) |
| 25 | 함수 내 import 11+ 건 — `chat.py:199 import os` / `tools.py:47, 53 from ...` / `main.py:72, 73, 135` / `prompt_registry.py:137, 144, 150` / `prompts.py:373` / `rag.py:444` / `optimize.py:89` | 함수 내 import (CLAUDE.md §3 / memory: "Python imports at top of file (early-fail)" 위반) | import 영역 모듈 로드 시점 영역 영역 영역 X — 영역 영역 호출 영역 영역 영역 영역 / circular import 영역 영역 영역 영역 | ⚠ early-fail 위반 | Major | DEV-IMPORT-1 (모든 함수 내 import 영역 파일 상단 영역) |
| 26 | `llm-service/app/routers/chat.py:174-246 chat()` (73 LOC) | 다중 분기 (RAG fallback / ReAct / portfolio analysis) + 3단계 중첩 | 함수 복잡도 ↑ — 테스트 어려움 / 유지보수 비용 ↑ | ⚠ | Major | DEV-COMPLEX-1 (`rag_fallback_path` / `react_agent_path` / `portfolio_analysis_path` 분해) |
| 27 | `portfolio-service/app/routers/optimize.py optimize_portfolio()` (120+ LOC) | 데이터 수집 → 최적화 → 진단 정보 변환 (3단계) | 동일 — 함수 분해 권장 | ⚠ | Major | DEV-COMPLEX-1 |

**Green**:

- TODO / FIXME / HACK 주석 0건 (Clean Code 준수) ✓
- TypeScript `: any` 0건 ✓
- Python 타입 힌트 99% (CLAUDE.md §3 준수) ✓
- `print()` 사용 X (logger 영역 사용) ✓
- circular import / bare imports 영역 영역 영역 ✓
- frontend 페이지 LOC ≤ 200 (D-3 / ADR 0013 준수 / optimize 42 / backtest 39 / chat 167) ✓
- portfolio-service async client 영역 ✓

---

## §3 우선순위별 종합

### §3.1 Critical (3건) — 즉시 디벨롭 의무

| # | 본문 | 디벨롭 | 시연 영향 | 카드 |
|---|---|---|---|---|
| 2 | yfinance transient rate limit fallback 영역 (DBG-1 / TG-2d 발견) | yfinance fallback / retry / cache | ✗ 영역 영역 영역 차단 | DBG-1 |
| 3 | 이메일 형식 검증 영역 (DBG-2 / Spring `@Email` 영역 영역 / RFC 5322 영역 영역 / TG-2d Edge-1) | Apache Commons Email Validator 또는 `@Pattern` 강화 | ✗ Edge case 영역 차단 | DBG-2 |
| 1 | Frontend E2E 테스트 부재 (Vitest "module load" 영역 / API mock + 상호작용 + 로직 영역) | Vitest + MSW 또는 Playwright E2E | ⚠ 자동 시연 영역 영역 / 면접 시그널 영역 | DEV-FE-1 |

**시연 차단**: 2건 (DBG-1 / DBG-2) — TG-2d 영역 발견 영역 / 본 카드 영역 영역 영역 = 발견만 / 별도 카드 영역 영역.

### §3.2 Major (11건) — 시나리오 B 진입 전 디벨롭

| 카테고리 | 항목 | 카드 |
|---|---|---|
| 동시성 | auth signup TOCTOU catch 영역 영역 | DEV-AUTH-1 |
| 코드 품질 | JWT verify_jwt DRY 위반 | DEV-DRY-1 |
| 코드 품질 | 함수 내 import 11+ 건 | DEV-IMPORT-1 |
| 에러 핸들링 | 사용자 메시지 영역 예외 본문 노출 (5+ 건) | DEV-ERR-1 |
| 에러 핸들링 | silent failure (`except: pass`) | DEV-ERR-2 |
| 코드 품질 | 함수 복잡도 (chat / optimize) | DEV-COMPLEX-1 |
| 관찰성 | portfolio-service health check 영역 | DEV-OBS-1 |
| 보안 | CORS allowedHeaders=* | DEV-SEC-1 |
| 일관성 | 에러 코드 체계 영역 (FastAPI) | DEV-API-1 |
| 일관성 | 로그 포맷 혼재 (llm-service unstructured) | DEV-LOG-1 |
| 테스트 | yfinance / Gemini mock 표준화 | DEV-TEST-1 |

### §3.3 Minor (8건) — Houseman 진입 시점 디벨롭

| 카테고리 | 항목 | 카드 |
|---|---|---|
| 보안 | CSP 영역 세분화 | DEV-SEC-2 |
| 보안 | NEXT_PUBLIC endpoint 노출 | DEV-SEC-3 |
| 동시성 | Redis SET + EXPIRE atomic | DEV-CONC-1 |
| 성능 | portfolio-service 동기 라우터 | DEV-PERF-1 |
| 성능 | 캐시 미스 retry / backoff | DEV-PERF-2 |
| 일관성 | response_model 영역 | DEV-API-2 |
| 관찰성 | frontend health UI feedback | DEV-OBS-2 |
| 관찰성 | Prometheus `/metrics` 영역 | DEV-OBS-3 |
| 테스트 | auth edge case 영역 (DBG-2 영역 영역) | DEV-TEST-2 |

---

## §4 디벨롭 카드 트리거 종합

### §4.1 카드 진입 순서 (Critical → Major → Minor)

**Phase 1 (즉시 / 시나리오 A 영역 영역 / 1주)**:

1. **DBG-1** (yfinance transient fallback / retry) — TG-2c 영역 영역 영역 영역 / 시연 영역
2. **DBG-2** (이메일 형식 검증 강화) — TG-2d Edge-1 발견 / Spring `@Email` → `@Pattern` 또는 Commons Validator
3. **DEV-FE-1** (Frontend E2E 테스트) — Vitest + MSW 또는 Playwright

**Phase 2 (시나리오 B 진입 전 / 2-4주)**:
4. **DEV-AUTH-1** (signup TOCTOU catch / `DataIntegrityViolationException` → `DUPLICATE_EMAIL`)
5. **DEV-DRY-1** (JWT 공유 패키지 추출 / `aether_shared_auth`)
6. **DEV-IMPORT-1** (함수 내 import 11+ 건 정리 / 파일 상단 이동)
7. **DEV-ERR-1** (사용자 메시지 영역 예외 본문 영역 영역 / `logger.error(exc_info=True)` 분리)
8. **DEV-ERR-2** (silent failure 영역 / `logger.warning(exc_info=True)` 추가)
9. **DEV-COMPLEX-1** (chat / optimize 함수 분해)
10. **DEV-OBS-1** (portfolio-service health 강화 / DB + yfinance 검증)
11. **DEV-SEC-1** (CORS allowedHeaders 화이트리스트)
12. **DEV-API-1** (FastAPI ErrorCode enum / 응답 형식 영역)
13. **DEV-LOG-1** (llm-service structured 로그 영역 통일)
14. **DEV-TEST-1** (yfinance / Gemini mock fixture 표준화)

**Phase 3 (Houseman 진입 시점 / Aether 종료 후)**:
15-22. Minor 8건 — 시나리오 B 진입 영역 영역 + 코드 품질 영역 영역 영역 영역 영역 영역 영역.

### §4.2 카드 영역 한 책임 (CLAUDE.md §6)

각 디벨롭 카드 영역 = **한 책임** 영역 — 카드 분할 의무. 한 카드 영역 시간 ≥ 30분 = 카드 분해 검토 / ≥ 1시간 = 분해 의무.

---

## §5 면접 답변 시그널

### §5.1 "발견된 문제는?"

> "AUDIT_REPORT.md (AUDIT-1 / 본 카드) 영역 시니어 관점 전체 진단 정착 — 22 발견 항목 (Critical 3 / Major 11 / Minor 8) + Green 정상 영역 영역. Critical 3건 = DBG-1 yfinance transient fallback 영역 / DBG-2 이메일 형식 검증 영역 / Frontend E2E 테스트 부재. 본 모든 발견 영역 = 별도 디벨롭 카드 (DEV-XXX-N) 영역 분리 — 한 카드 1책임 (CLAUDE.md §6) 일관성."

**시그널**: 자가 진단 + 우선순위 + 결정 추적 + 카드 분리.

### §5.2 "왜 안 고쳤어요?"

> "양면 정책 (PRINCIPLES 패턴 6) — 본 카드 영역 영역 = 발견만 / 수정 X / 디벨롭 카드 영역 분리 (CLAUDE.md §6 한 카드 1책임). DBG-1 (yfinance) 영역 = TG-2d 영역 영역 영역 영역 ✓ → transient 영역 영역 영역 영역 → DBG-1 영역 영역 = 영역 fallback 영역 (별도 카드 영역). DBG-2 (이메일) 영역 = 영역 영역 영역 영역 영역 영역. Critical 3 → 디벨롭 영역 영역 / Major 11 → 시나리오 B 진입 전 / Minor 8 → Houseman 진입 시점 영역 영역."

**시그널**: 의도적 결정 + 양면 정책 + 시나리오 분리 + 한 카드 1책임.

### §5.3 "Critical은 어떻게?"

> "Critical 3건 = 시연 차단 영역. DBG-1 (yfinance) 영역 = 즉시 영역 영역 / DBG-2 (email) 영역 = 즉시 영역 영역 영역 / Frontend E2E 영역 = 시연 자동화 영역 영역 영역. 본 영역 영역 영역 = AUDIT_REPORT.md §3.1 영역 명시 + 디벨롭 카드 ID 부여 (DBG-1 / DBG-2 / DEV-FE-1) — 영역 추적 영역 영역."

**시그널**: 명확한 다음 진입 + 카드 ID 추적.

### §5.4 "transient vs 영구?"

> "DBG-1 (yfinance) 영역 사례 — TG-2c 영역 X / TG-2d 영역 ✓ / 코드 변경 X → transient (외부 API rate limit). 본 영역 시그널 영역 활용 — 영역 영역 영역 영역 영역 = transient (영역 영역 영역 영역 영역 fallback) / 영역 영역 = 영구 (즉시 정정 영역). 양면 정책 영역 = transient 영역 영역 영역 영역 영역 영역 영역 / 영구 영역 영역 영역 영역 영역 영역."

**시그널**: TG-2d 발견 영역 인용 + 본질 판단 + 시니어 시그널.

### §5.5 "양면 정책 영역?"

> "AUDIT-1 본 카드 영역 = 발견 영역 영역 / 수정 X = 보류 결정 영역 영역. 단 발견 영역 영역 영역 영역 영역 영역 (Green 정상 영역 영역 영역 영역 영역) — 즉 의도적 결정 영역 추적 + 영역 영역 영역 영역 영역 분리. PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 직접 사례."

**시그널**: 양면 정책 + Green 영역 + 패턴 6 일관성.

---

## §6 다음 진입 카드

### §6.1 즉시 진입 (Critical / Phase 1)

1. **DBG-1** — yfinance transient rate limit fallback (`portfolio-service/app/services/data_provider.py`)
2. **DBG-2** — 이메일 형식 검증 강화 (`auth-service/.../SignUpRequest.java`)
3. **DEV-FE-1** — Frontend E2E 테스트 (Vitest + MSW 또는 Playwright)

### §6.2 단기 진입 (Major / Phase 2)

4-14. DEV-AUTH-1 / DEV-DRY-1 / DEV-IMPORT-1 / DEV-ERR-1 / DEV-ERR-2 / DEV-COMPLEX-1 / DEV-OBS-1 / DEV-SEC-1 / DEV-API-1 / DEV-LOG-1 / DEV-TEST-1

### §6.3 중장기 진입 (Minor / Phase 3 / Houseman 시점)

15-22. Minor 8건 — DEV-SEC-2 / DEV-SEC-3 / DEV-CONC-1 / DEV-PERF-1 / DEV-PERF-2 / DEV-API-2 / DEV-OBS-2 / DEV-OBS-3 / DEV-TEST-2

### §6.4 Aether 종료 카드

본 카드 (AUDIT-1) 머지 + 디벨롭 카드 영역 영역 머지 후 → **Aether 종료 카드** (시나리오 A 종료 / Top 10 9.5/10 / META_REVIEW §9 일관성) → **Houseman 진입** (별도 repo / Phase 7-12 / Subagents / Soul.md / HOUSEMAN_APPLICATION.md 작성).

---

## §7 한 문장

AUDIT-1 = 시니어 관점 전체 진단 (22 발견 / Critical 3 + Major 11 + Minor 8) + Green 영역 영역 영역 + 디벨롭 카드 22 ID 부여 (DBG-1 / DBG-2 / DEV-XXX-N) + 자가 검증 패턴 (3 Explore 영역 본인 검증 정정 영역) + 양면 정책 일관성 (발견만 / 수정 X / 별도 카드 영역) — 면접 답변 영역 자료 (시그널 ↑↑) / Aether 종료 자료 영역 / 디벨롭 카드 트리거 영역.
