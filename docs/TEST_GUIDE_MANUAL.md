# TEST_GUIDE_MANUAL — Aether 일상 + 면접 시점 시연 가이드 (TG-MANUAL)

> **본질**: Phase 1 종료 (DBG-1 + DBG-2 + DEV-FE-1 정착) 후 일상 시점 + 면접 시점 분리 시연 가이드. AUDIT-1 결과 통합 (Critical 3 정착 / Major 11 보류 / Minor 8 보류) + DB 관리 (DBeaver + docker) + 면접 직전 cleanup 흐름. 자료 카드 / ADR X (TG-1 / DIFF-1 / I-1 / I-1-REVIEW / AUDIT-1 패턴 일관성).
> **카드**: TG-MANUAL (TEST_GUIDE_MANUAL.md / 자료 카드 / ADR X)
> **작성일**: 2026-05-10
> **선행 카드**: DEV-FE-1 (PR #51 / 8a6ec01) — Phase 1 종료
> **인용 자료** (8건): TEST_REPORT.md TG-2d (시연 결과) + DIFFERENTIATION.md (직무별 차별화) + INTERVIEW_SIMULATION.md §10 (자가 검증) + AUDIT_REPORT.md (22 발견 / Critical 3 정착) + ADR 0026 (DBG-1) + ADR 0027 (DBG-2) + ADR 0028 (DEV-FE-1) + AGENTS.md §7

---

## §0 본질 + 시점 분리

### §0.1 시점 분리 흐름

| 시점 | 흐름 본질 | 시간 | 주요 §  |
|---|---|---|---|
| 일상 시점 | 환경 시작 → 5 기능 정상 시연 → DB 관리 → 환경 종료 | 영역 영역 / ~15-20분 | §1 |
| 면접 시점 | 환경 cleanup → 시연 user 정착 → 5 기능 사전 검증 → 5분 시연 | 영역 영역 / ~30분 | §2 |

본 자료 영역 본질 — 시점 영역 영역 영역 / 영역 / 의무 영역 영역 영역 영역 영역 영역. 일상 영역 = 빠른 검증 / 면접 영역 = cleanup + 정확성 우선.

### §0.2 Phase 1 정착 후 안정성

본 시점 = Phase 1 (DBG-1 + DBG-2 + DEV-FE-1) 정착 영역 영역. **시연 안정성 ↑↑**:

- **DBG-1 정착** (ADR 0026): yfinance transient rate limit fallback (retry 3회 + Fixture Provider) → optimize / backtest 시연 영역 외부 API 차단 영역 영역 영역 영역
- **DBG-2 정착** (ADR 0027): 이메일 형식 검증 강화 (`@Email` + `@Pattern` / RFC 5322 / TLD ≥ 2자) → signup 영역 데이터 무결성 ↑
- **DEV-FE-1 정착** (ADR 0028): Frontend E2E 테스트 (MSW + Vitest + RTL / 21 신규 E2E) → 시연 영역 frontend 깨짐 회귀 자동 검증

### §0.3 환경 영역 (실측 / docker-compose.yml + .env)

| 영역 | 값 |
|---|---|
| postgres | localhost:**5433** (`5433:5432`) |
| POSTGRES_DB | `aether_auth` |
| POSTGRES_USER | `aether` |
| POSTGRES_PASSWORD | `.env` 영역 정착 (git X) |
| redis | localhost:6380 |
| qdrant | localhost:6333-6334 |
| auth-service | localhost:8003 (Spring Boot) |
| portfolio-service | localhost:8001 (FastAPI) |
| llm-service | localhost:8002 (FastAPI) |
| frontend | localhost:3000 (Next.js) |
| Flyway migration | `auth-service/src/main/resources/db/migration/V1__init.sql` |

---

## §1 일상 시점 (~15-20분)

### §1.1 환경 시작 (3분)

```bash
# 1. Docker Desktop GUI 시작 (Mac: Applications / Win: 시스템 트레이)
# 2. docker compose up -d (백그라운드 영역)
cd /Users/kuka/Aether
docker compose up -d

# 3. 30초 대기 후 healthy 검증
sleep 30
docker compose ps
# 7 서비스 = postgres + redis + qdrant + auth + portfolio + llm + frontend
# 모두 "healthy" 영역 확인
```

**API health 4 endpoint**:

```bash
curl http://localhost:8003/health  # auth (Spring Boot)
curl http://localhost:8001/health  # portfolio (FastAPI)
curl http://localhost:8002/health  # llm (api_key + vectorstore + portfolio_service)
curl http://localhost:3000          # frontend (HTTP 200)
```

**frontend 영역 개발** (선택 / hot reload 영역):

```bash
cd frontend
npm run dev   # localhost:3000 / Next.js 개발 모드
```

### §1.2 5 기능 정상 시연 (10분)

#### §1.2.1 signup + login (DBG-2 정착 후)

```bash
# 신규 user (DBG-2 후 = TLD 의무)
TS=$(date +%s)
curl -X POST http://localhost:8003/api/auth/signup \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"daily${TS}@aether.local\",\"password\":\"Daily123!\",\"name\":\"Daily\"}"
# → 201 Created / id + email + role=USER

# login → accessToken
curl -X POST http://localhost:8003/api/auth/login \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"daily${TS}@aether.local\",\"password\":\"Daily123!\"}"
# → 200 OK / accessToken + refreshToken (HS512 / 30분 + 7일)

# 영역 영역 영역 (DBG-2 회귀): foo@bar 영역 → C002 (TLD 영역 영역)
curl -X POST http://localhost:8003/api/auth/signup \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"foo${TS}@bar\",\"password\":\"Daily123!\",\"name\":\"X\"}"
# → 400 / error.code = C002 (DBG-2 정착 후)
```

#### §1.2.2 optimize (Sharpe 1.5971 / DBG-1 fallback)

```bash
TOKEN=...  # login accessToken
curl -X POST http://localhost:8001/api/optimize \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tickers":["AAPL","MSFT","GOOGL"],"strategy":"max_sharpe","period":"3y"}'
# → metrics.sharpe_ratio = 1.5971 (TG-2d 일치) / weights GOOGL 89.47% + AAPL 10.53%
# DBG-1 정착 후 = yfinance transient 차단 시 FixtureProvider 자동 전환
```

#### §1.2.3 backtest (누적 155.74% / 8 메트릭)

```bash
curl -X POST http://localhost:8001/api/backtest \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tickers":["AAPL","MSFT","GOOGL"],"strategy":"max_sharpe","start_date":"2022-01-01","end_date":"2024-12-31","rebalance_every":63}'
# → metrics.total_return = 1.5574 / sharpe = 0.9051 / mdd = 0.3034 / rebalance_count = 16
```

#### §1.2.4 RAG chat (질문 + sources)

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message":"샤프 비율이 무엇인가요?"}'
# → answer + sources (📚 영역 표기) / 26 chunks / 3072차원 / Qdrant
```

#### §1.2.5 MCP (Claude Desktop / 사용자 수동)

- Claude Desktop 영역 stdio 4 도구 등록 (analyze_portfolio / compute_risk / run_backtest / get_recommendation)
- 자동 시연 X / 사용자 수동 검증 영역
- 시연 시 = 사용자 영역 직접 확인 의무

### §1.3 일상 DB 관리 (DBeaver SQL Editor)

#### §1.3.1 연결 정보

- Host: `localhost`
- Port: `5433` (호스트 영역 / 컨테이너 5432)
- Database: `aether_auth`
- User: `aether`
- Password: `.env` POSTGRES_PASSWORD 영역
- Driver: PostgreSQL 16

#### §1.3.2 정석 — Cmd+] (Mac) / Ctrl+] (Win/Linux)

```sql
-- 조회
SELECT id, email, name, role, enabled, created_at FROM users ORDER BY id;

-- 수정 (이름)
UPDATE users SET name = 'New Name' WHERE id = 2;

-- 다중 삭제
DELETE FROM users WHERE id IN (5, 6, 7);

-- 전체 삭제 + sequence 리셋 (id 1 영역 영역)
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
```

#### §1.3.3 INSERT 영역

- **추천**: signup endpoint 영역 호출 (bcrypt 해시 자동 / 영역 영역 검증 적용)
- **직접 SQL X**: bcrypt 해시 영역 영역 의무 / 영역 검증 영역 영역 X

### §1.4 frontend 테스트 (DEV-FE-1 정착 후)

```bash
cd frontend
npm test
# → 26 passed (10 files / 5 unit + 21 E2E)
# 기능 변경 영역 영역 회귀 검증 의무
```

**테스트 영역**:

- 5 unit (Dashboard / Chat / Backtest / Optimize / Header) — module load
- 21 E2E (auth-flow 6 + optimize 4 + backtest 4 + chat 4 + error 3) — MSW + RTL

### §1.5 환경 종료

```bash
# 빠른 정지 (volume 보존 / 영역 영역 영역 데이터 유지)
docker compose stop

# volume 보존 종료 (컨테이너 삭제 / 데이터 유지)
docker compose down

# 영역 영역 (volume 영역 영역 / 데이터 손실 / 면접 cleanup 영역)
# docker compose down -v
```

---

## §2 면접 시점 (~30분)

### §2.1 면접 직전 30분 흐름

| Step | 시간 | 본문 | 명령 |
|---|---|---|---|
| 1 | 3분 | 환경 시작 | `docker compose up -d` + sleep 30 |
| 2 | 5분 | DB cleanup (id=1 시작 영역) | `docker compose down -v` + 재시작 |
| 3 | 1분 | 시연 user 정착 | `curl signup` + id=1 검증 |
| 4 | 15분 | 5 기능 사전 검증 | curl 영역 5건 |
| 5 | 5분 | 면접 시연 5분 리허설 | 분 1-5 흐름 |

### §2.2 면접 직전 DB cleanup (정석)

```bash
# 1. volume 전체 삭제 (id=1 시작 영역 영역)
docker compose down -v

# 2. 재시작 (Flyway migration 자동 / V1__init.sql 영역)
docker compose up -d

# 3. 30초 대기 + 7/7 healthy 검증
sleep 30
docker compose ps
# 모두 healthy 확인 의무

# 4. 시연 user 정착
TS=$(date +%s)
curl -X POST http://localhost:8003/api/auth/signup \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"demo${TS}@aether.local\",\"password\":\"DemoPass123!\",\"name\":\"Demo\"}"
# → 201 / id = 1

# 5. id=1 검증
docker compose exec postgres psql -U aether -d aether_auth \
  -c "SELECT id, email FROM users;"
# → id=1 영역 시연 user 영역 영역
```

### §2.3 면접 시연 5분 흐름 (TG-2d 결과 + Phase 1 정착 후)

| 분 | 시연 | 답변 포인트 |
|---|---|---|
| 1 | signup + login + /dashboard + logout | F-1a / ADR 0004 v2 / HS512 + Redis blacklist + DBG-2 (이메일 검증 강화 / ADR 0027) |
| 2 | optimize (AAPL+MSFT+GOOGL → Sharpe 1.5971) | T-1 / cvxopt Markowitz / **DBG-1 transient 발견 + fallback 정착 / ADR 0026** |
| 3 | backtest (누적 155.74% / Sharpe 0.9051) | walk-forward / 분기 리밸런싱 (63일) / 8 메트릭 |
| 4 | RAG chat (질문 + 📚 sources) | D-5 / ADR 0018 / ReAct 5 도구 자율 판단 / 26 chunks / 3072차원 / Qdrant |
| 5 | 차별화 (AGENTS.md §7 / ADR README) | **양면 정책 18 ADR** / 카파시 매핑 8 본능 76→87 / WORK_PATTERNS / **AUDIT-1 자가 검증 패턴** |

### §2.4 면접 시점 시그널 흐름

#### "DB 관리 어떻게?"

> "DBeaver (시각 / SQL Editor 정석 Cmd+]) + docker exec psql (CLI / 자동화 영역) 영역 양면 영역 영역. 면접 직전 cleanup 영역 = `docker compose down -v` 영역 volume 전체 삭제 + Flyway migration 자동 재실행 → id=1 영역 영역 영역 영역 시연 깨끗함 ↑."

#### "발견된 문제는?"

> "AUDIT_REPORT.md (AUDIT-1) — 22 발견 (Critical 3 / Major 11 / Minor 8). **Critical 3 정착 완료** (DBG-1 yfinance fallback / DBG-2 이메일 검증 / DEV-FE-1 Frontend E2E). Major 11 + Minor 8 = 양면 정책 보류 (시나리오 B 진입 시점 트리거 명시) — 영역 영역 PRINCIPLES 패턴 6 (미적용 결정 = 시그널) 일관성."

#### "왜 Major 11 안 고쳤어요?"

> "시나리오 A 본질 (사용자 0명 / 시연 영향 X) — Major 11 영역 시연 차단 영역 영역 영역 + 시나리오 B 진입 시점 (사용자 5+ 인터뷰 + PMF 10불) 영역 영역 트리거. 영역 의도 = 영역 의도적 결정 추적 + 영역 영역 영역 영역 영역 분리 (CLAUDE.md §6 한 카드 1책임)."

#### "transient vs 영구 어떻게 판단?"

> "DBG-1 사례 — TG-2c (PR #44) 영역 yfinance 차단 / TG-2d (PR #45) 영역 정상 / **코드 변경 X** → transient (외부 API rate limit). 즉 동일 시점 + 동일 코드 + 다른 결과 = transient 영역 영역. fallback 정착 (ADR 0026) 후 영구 X 영역 영역 → 영역 영역 정착 X."

#### "AI agent 검증 신뢰성?"

> "I-1-REVIEW (PR #47) — 면접 자료 14건 정정 (frontend SSE 미구현 발견 / HOUSEMAN 미존재 / D-3 LOC 정정). AUDIT-1 (PR #48) — 3 Explore agent 결과 본인 검증 영역 거짓 3건 정정 (.env 키 노출 거짓 / DB 마이그레이션 거짓 / signup race Critical→Major). DEV-FE-1 (PR #51) — plan 추측 → 실제 타입 정독 후 정정 (BacktestResult metrics nested). 즉 **자가 검증 패턴 정착** = G1 본질 트리거 + PRINCIPLES 패턴 10 일관성. AI agent 영역 100% 신뢰 X / 검증 의무."

---

## §3 DB 관리 (DBeaver + docker)

### §3.1 DBeaver 연결

1. New Database Connection → PostgreSQL
2. 연결 정보:
   - Host: `localhost`
   - Port: `5433`
   - Database: `aether_auth`
   - Username: `aether`
   - Password: `.env` 영역
3. Test Connection → Connected
4. users 테이블 더블클릭 → Data 탭

### §3.2 DBeaver SQL Editor (정석)

`Cmd+]` (Mac) / `Ctrl+]` (Win/Linux) 영역 SQL Editor 영역.

```sql
-- 조회
SELECT id, email, name, role, enabled, created_at FROM users ORDER BY id;

-- 영역 (이메일 영역 영역)
SELECT * FROM users WHERE email LIKE '%@aether.local';

-- 수정
UPDATE users SET name = 'Updated Name' WHERE id = 2;

-- 다중 삭제
DELETE FROM users WHERE id IN (5, 6, 7);

-- 전체 삭제 + sequence 리셋 (id=1 영역 영역)
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
```

**INSERT 영역**: signup endpoint 영역 호출 추천 (bcrypt 자동 + 검증 자동). 직접 SQL X.

### §3.3 docker 명령어 (백업 / 자동화)

```bash
# 조회
docker compose exec postgres psql -U aether -d aether_auth \
  -c "SELECT id, email, name FROM users ORDER BY id;"

# pager off (대량 결과 영역)
docker compose exec postgres psql -U aether -d aether_auth -P pager=off \
  -c "SELECT * FROM users;"

# 다중 삭제
docker compose exec postgres psql -U aether -d aether_auth \
  -c "DELETE FROM users WHERE id IN (5,6,7);"

# 전체 삭제 + sequence 리셋
docker compose exec postgres psql -U aether -d aether_auth \
  -c "TRUNCATE TABLE users RESTART IDENTITY CASCADE;"

# 백업 (pg_dump)
docker compose exec postgres pg_dump -U aether aether_auth > backup_$(date +%Y%m%d).sql
```

### §3.4 면접 직전 cleanup 정석

| 방법 | 시간 | 결과 | 추천 |
|---|---|---|---|
| `docker compose down -v` + 재시작 | ~30초 | volume 영역 / Flyway 자동 / id=1 시작 / 영역 영역 깨끗 | ✓ 면접 영역 |
| `TRUNCATE TABLE users RESTART IDENTITY CASCADE` | ~1초 | volume 보존 / 영역 영역 / 빠름 | 일상 영역 |

**면접 영역 추천** = `docker compose down -v` (영역 영역 깨끗함 / Flyway migration 자동 / 영역 영역 영역 영역).

---

## §4 Phase 1 정착 결과 활용

### §4.1 DBG-1 yfinance transient fallback (ADR 0026)

| 영역 | 본문 |
|---|---|
| 발견 | TG-2c (PR #44) 영역 yfinance 차단 / TG-2d (PR #45) 영역 정상 / 코드 변경 X |
| 본질 | transient yfinance rate limit (외부 API / 영구 X) |
| 정착 | `data_provider.py` 확장 (~140 LOC) — `RateLimitError` + `NetworkError` + `_classify_yfinance_error` (message 영역 분류) + `_retry_with_backoff` (3회 / 1s / 2s / 4s exponential) + `FixtureProvider` (252 영역 deterministic 1년 영역) + `CompositeProvider` (primary + fallback 자동 전환) |
| 검증 | 22 신규 테스트 / 회귀 0 (227 passed) |
| ADR | 0026 (양면 정책 16 ADR) |
| 면접 시그널 | "transient vs 영구 본질 판단" + "재발 회피 fallback" + "옵션 B 다른 provider 보류 = 시나리오 B 트리거" |

### §4.2 DBG-2 이메일 형식 검증 (ADR 0027)

| 영역 | 본문 |
|---|---|
| 발견 | TG-2c §2.1 Edge-1 (`foo@bar` id=17) + TG-2d §2.1 Edge-1 (`foo<ts>@bar` id=19) 정상 signup |
| 본질 | Spring `@Email` annotation = `@` 영역 영역 영역 / TLD 검증 X (RFC 5322 영역 영역 X) |
| 정착 | `SignUpRequest.java` `@Email` + `@Pattern("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")` 이중 검증 (TLD ≥ 2자 의무) |
| 검증 | 7 신규 테스트 (TLD 없음 / @ 없음 / 도메인 없음 / TLD 1자 / TG-2d Edge-1 회귀 / `+` / 다단 TLD) / 회귀 0 (BUILD SUCCESSFUL) |
| ADR | 0027 (양면 정책 17 ADR) |
| 기존 user | id=17 / id=19 보존 (마이그레이션 X / 시나리오 A 일관성) |
| 면접 시그널 | "디버그 발견 + 별도 카드 분리 결정" (한 카드 1책임) + "옵션 B 이메일 인증 보류 = 시나리오 B 진입 트리거" |

### §4.3 DEV-FE-1 Frontend E2E 테스트 (ADR 0028)

| 영역 | 본문 |
|---|---|
| 발견 | AUDIT-1 §1 Critical 1 — Frontend Vitest 5건 = "module load"만 / API mock + 비즈니스 로직 검증 0 |
| 정착 | MSW + Vitest + RTL / 21 신규 E2E (auth-flow 6 + optimize 4 + backtest 4 + chat 4 + error 3) / mock 응답 = TG-2d 시연 결과 일치 |
| 검증 | `npm test` 26 passed (10 files / 5 unit + 21 E2E) / `tsc --noEmit` 0 / 회귀 0 |
| ADR | 0028 (양면 정책 18 ADR) |
| 면접 시그널 | "시연 안정성 ↑↑" + "회귀 자동 검증" + "옵션 B Playwright 보류 = 시나리오 B 진입 시점 트리거 (CI/CD 자동화)" |

### §4.4 자가 검증 패턴 (시니어 시그널 ↑↑)

본 영역 = Aether 영역 영역 시그널 영역 영역. AI agent 결과 100% 신뢰 X / 본인 검증 영역 영역 정정 영역 정착:

| 카드 | 발견 | 정정 |
|---|---|---|
| I-1-REVIEW (PR #47) | 면접 자료 인용 14건 영역 영역 | frontend SSE 미구현 명시 / HOUSEMAN 작성 예정 표기 / D-3 LOC 영역 영역 → 후 / chat.py 라인 정정 등 |
| AUDIT-1 (PR #48) | 3 Explore agent 결과 거짓 3건 | `.env` 키 노출 거짓 / portfolio+llm DB 마이그레이션 거짓 / signup race Critical→Major (DB unique constraint 영역 영역) |
| DEV-FE-1 (PR #51) | plan 추측 → 실제 타입 영역 | `BacktestResult.metrics` nested / `OptimizationResult.metrics` nested / `rebalance_count` 영역 (n_rebalances X) |

**면접 답변 시그널** — "AI agent 결과 영역 영역 영역 100% 신뢰?" 영역 영역 영역 영역 영역 영역 영역 자가 검증 패턴 영역 영역 영역 영역. PRINCIPLES 패턴 10 (G1 본질 트리거) 일관성.

---

## §5 자가 점검 체크리스트

### §5.1 일상 시점 (10 항목)

- [ ] Docker Desktop GUI 시작 + `docker compose up -d`
- [ ] `docker compose ps` 영역 7/7 healthy 검증
- [ ] API health 4 endpoint 정상 응답 (auth / portfolio / llm / frontend)
- [ ] signup → 201 / login → 200 / accessToken 영역
- [ ] optimize → metrics.sharpe_ratio = 1.5971 영역
- [ ] backtest → metrics.total_return = 1.5574 + rebalance_count = 16
- [ ] chat → answer + sources 영역
- [ ] DBeaver 연결 (5433 / aether / aether_auth) + users 영역 조회
- [ ] frontend `npm test` → 26 passed
- [ ] 환경 종료 (`docker compose stop` 또는 `down`)

### §5.2 면접 직전 (15 항목)

- [ ] `docker compose down -v` (volume 전체 삭제)
- [ ] `docker compose up -d` 재시작
- [ ] 30초 대기 후 `docker compose ps` 7/7 healthy 검증
- [ ] API health 4 endpoint 정상
- [ ] 시연 user signup → 201 / id=1 검증 (`SELECT id FROM users`)
- [ ] login → accessToken 영역
- [ ] optimize 사전 검증 → Sharpe 1.5971
- [ ] backtest 사전 검증 → 누적 155.74%
- [ ] chat 사전 검증 → answer + sources
- [ ] MCP 사용자 수동 검증 (선택)
- [ ] DBeaver 연결 검증 (시연 영역 영역 사용)
- [ ] frontend `npm run dev` 시작 (`localhost:3000` 정상)
- [ ] AGENTS.md §7 + ADR README 차별화 영역 영역 (시연 5분 분 5)
- [ ] 면접 답변 시그널 영역 (AUDIT-1 22 발견 / 자가 검증 패턴 / Major 11 보류)
- [ ] 시연 5분 리허설 1회 (분 1-5 흐름)

### §5.3 면접 시연 5분 (5 항목)

- [ ] **분 1**: signup + login + `/dashboard` 진입 + logout (HS512 + Redis blacklist + DBG-2)
- [ ] **분 2**: optimize AAPL+MSFT+GOOGL → Sharpe 1.5971 (cvxopt + DBG-1 fallback)
- [ ] **분 3**: backtest 누적 155.74% / Sharpe 0.9051 / 16 리밸런싱 (walk-forward + 8 메트릭)
- [ ] **분 4**: chat "샤프 비율?" → answer + 📚 sources (ReAct 5 도구 + Qdrant + RAG)
- [ ] **분 5**: 차별화 (AGENTS.md §7 양면 정책 18 ADR / 카파시 매핑 / AUDIT-1 자가 검증)

---

## §6 다음 카드

| 옵션 | 본질 | 시점 |
|---|---|---|
| **Aether 종료 카드** (추천) | 시나리오 A 종료 결정 / 카드 누적 31+ 마감 / Houseman 진입 본질 / Top 10 9.5/10 일관성 | 본 시점 영역 |
| Phase 2 Major 11 카드 | DEV-AUTH-1 / DEV-DRY-1 / DEV-IMPORT-1 / DEV-ERR-1 / DEV-ERR-2 / DEV-COMPLEX-1 / DEV-OBS-1 / DEV-SEC-1 / DEV-API-1 / DEV-LOG-1 / DEV-TEST-1 | 시나리오 B 트리거 |
| Phase 3 Minor 8 카드 | DEV-SEC-2 / DEV-SEC-3 / DEV-CONC-1 / DEV-PERF-1 / DEV-PERF-2 / DEV-API-2 / DEV-OBS-2 / DEV-OBS-3 | Houseman 시점 |

**추천** = **Aether 종료 카드** → Houseman 진입 (시나리오 A 본질 정착 완료 / 별도 repo / Phase 7-12 / Subagents / Soul.md / HOUSEMAN_APPLICATION.md 작성).

---

## §7 한 문장

TG-MANUAL = 일상 + 면접 시점 분리 시연 가이드 (~450 LOC / 7 § / Phase 1 정착 후 안정성 ↑↑) — 환경 시작 + 5 기능 정상 시연 + DB 관리 (DBeaver + docker) + 면접 직전 cleanup 흐름 (`docker compose down -v` + Flyway 자동) + AUDIT-1 결과 활용 (Critical 3 정착 / Major 11 보류 / Minor 8 보류) + 자가 검증 패턴 시그널 (I-1-REVIEW 14건 + AUDIT-1 거짓 3건 + DEV-FE-1 plan 추측 정정) + 면접 답변 시그널 5건 — 시나리오 A 일관성 + 양면 정책 18 ADR / 다음 진입 = Aether 종료 카드.
