# ADR 0028 — DEV-FE-1 Frontend E2E 테스트 (MSW + Vitest + RTL)

- **상태**: Accepted
- **일자**: 2026-05-10
- **관련 카드**: DEV-FE-1 (Frontend E2E / Phase 1 Critical 3 영역 영역)
- **결정 근거**: AUDIT_REPORT.md §1 (Critical 1) — Frontend Vitest 5건 = "module load"만 / API mock + 사용자 상호작용 + 비즈니스 로직 검증 0 / 시연 안정성 ↓↓

---

## 컨텍스트

AUDIT-1 (PR #48 / f42d8d6) 영역 발견 — Frontend E2E 테스트 영역 X / 5 unit 테스트 영역 = "module load + export default 영역" 검증만. 시연 시점 frontend 깨짐 위험 + 면접 시그널 약함 (테스트 커버리지 영역).

본 카드 (DEV-FE-1) = Phase 1 Critical 3번째 카드 (DBG-1 / DBG-2 영역 영역 정착) — Phase 1 종료 + Phase 2 Major 11 카드 진입 트리거.

---

## 결정 (양면 정책 / 5 분기 추적)

### 분기 1: 옵션 A (MSW + Vitest + RTL) vs 옵션 B (Playwright) — **A 채택**

**옵션 A (선택)** = MSW (Mock Service Worker / network level intercept) + Vitest (Next.js 호환) + React Testing Library + @testing-library/user-event — 영역 영역 영역 unit/integration 수준 / 빠른 실행 / CI 통합 영역.

**옵션 B (보류)** = Playwright (실제 Chromium / 헤드리스) — 무거움 / TG-2c puppeteer 시연 흐름과 일관 (수동 시연 패턴) / 시나리오 B 진입 시점 (CI/CD 통합) 트리거.

**옵션 C (보류)** = Cypress — Playwright 대안 / 무거움 / 영역 영역 영역.

근거: 옵션 A 영역 = 빠른 실행 (영역 5초) + Next.js 호환 + 의존성 영역 영역 영역 영역 (msw + user-event 2건). 옵션 B 영역 = 시연 영역 puppeteer (TG-2c) 영역 영역 영역 / 자동화 영역 영역 영역 영역 시점 트리거.

### 분기 2: 테스트 영역 — API 함수 영역 영역 (페이지 렌더링 X) — **선택**

근거: Next.js App Router 페이지 영역 vitest jsdom 영역 영역 영역 영역 영역 영역 영역 (`useRouter` / `useSearchParams` / `cookies()` 영역). 영역 영역 = API 함수 영역 영역 (`signUp` / `login` / `optimizePortfolio` / `runBacktest` / `sendChatMessage`) — 영역 영역 비즈니스 로직 (axios 영역 + interceptor + Zustand store + MSW intercept) 영역 영역 영역.

페이지 렌더링 테스트 = 옵션 B (Playwright) 시점 의무.

### 분기 3: 시나리오 범위 — 5 기능 정상만 + 에러 영역 — **선택**

근거: 본 카드 = Phase 1 Critical (시연 영역 영역 영역). 영역 정상 흐름 + 핵심 에러 (401 / 503 / 네트워크). Edge case 영역 영역 = DEV-FE-2 (별도 카드) 영역 영역.

5 파일:

1. `auth-flow.test.ts` (6 tests) — signup / login / getMe / logout / refresh / 409 DUPLICATE_EMAIL
2. `optimize.test.ts` (4 tests) — Sharpe 1.5971 / weights sum 1.0 / metrics / n_stocks
3. `backtest.test.ts` (4 tests) — 누적 155.74% / 8 메트릭 / Calmar / 16 리밸런싱
4. `chat.test.ts` (4 tests) — answer + sources / sources 구조 / analyzePortfolio / queryRAG
5. `error-handling.test.ts` (3 tests) — 503 / 409 / 네트워크 에러

### 분기 4: API mock 응답 — TG-2d 시연 결과 영역 일치 — **선택**

근거: handlers.ts 영역 mock 응답 영역 = TG-2d 영역 실제 백엔드 응답 영역 영역 일치 (Sharpe 1.5971 / 누적 155.74% / GOOGL 89.47% / AAPL 10.53% / 16회 리밸런싱). 영역 영역 영역 영역 영역 영역 영역 영역 / 시연 데이터 영역 testdata 영역 영역 영역.

### 분기 5: jsdom 영역 localStorage — vi.fn mock 영역 setup — **선택**

근거: vitest jsdom 영역 영역 영역 `window.localStorage` 영역 영역 영역 / authStore 영역 `setTokens` 호출 시 TypeError. setup 영역 `Object.defineProperty(window, 'localStorage', {...})` 영역 mock 영역 영역.

---

## 영향

### 신규

- `frontend/src/test/mocks/server.ts` — MSW node server (setupServer)
- `frontend/src/test/mocks/handlers.ts` (~200 LOC) — 11 endpoint mock (auth 5 + portfolio 4 + llm 4 + health 2) + errorHandlers 4건
- `frontend/src/__tests__/e2e/` 5 파일 (~270 LOC):
  - `auth-flow.test.ts` (6 tests)
  - `optimize.test.ts` (4 tests)
  - `backtest.test.ts` (4 tests)
  - `chat.test.ts` (4 tests)
  - `error-handling.test.ts` (3 tests)

### 갱신

- `frontend/vitest.setup.ts` — MSW lifecycle (`beforeAll` / `afterEach` / `afterAll`) + `localStorage` mock + `storage` reset
- `frontend/package.json` — `msw@^2.6.0` + `@testing-library/user-event@^14.5.2` 추가 (49 packages)

### 회귀

- frontend 영역 영역 영역 영역 영역 영역 — **26 passed (10 files)** / 기존 5 unit + 신규 21 E2E.
- `tsc --noEmit` 영역 영역 0.
- 코드 변경 X (테스트 + setup 영역).

---

## 결과

### 긍정적

- **시연 안정성 ↑↑**: 5 기능 (auth / optimize / backtest / chat / error) 영역 영역 영역 영역 영역 → 시연 시점 frontend 깨짐 위험 ↓↓.
- **회귀 검증 자동화**: CI 통합 영역 (`vitest run`) — 영역 PR 영역 영역 영역 영역.
- **면접 시그널 ↑**: AUDIT-1 발견 영역 (Critical 1) 영역 영역 영역 / 테스트 커버리지 ↑.
- **TG-2d 시연 결과 일치**: mock 응답 영역 = 실제 백엔드 영역 영역 / 영역 단일.
- **양면 정책 18 ADR** (0011-0028) — 정착 10 / 보류 4 / 메타 4 / 정리 1.

### 부정적

- **실제 브라우저 X**: jsdom 영역 영역 (Playwright 옵션 B 영역 영역 시나리오 B 진입 시점 트리거).
- **페이지 렌더링 테스트 X**: API 함수 영역 (Next.js App Router 영역 영역 영역 영역 영역 영역 영역) — 영역 시나리오 B 진입 시점 영역 옵션 B 영역 영역 영역.
- **MSW network mock 영역**: 실제 HTTP X — unit/integration 수준 영역.

### 트리거 (옵션 B / 옵션 C 진입 시점)

- 옵션 B (Playwright): 시나리오 B 진입 시점 (CI/CD 자동화 / 사용자 5+ 인터뷰 + PMF 10불) 트리거.
- 본 시점 = 영구 보류 / ADR 영역 영역.

---

## 인용 자료

- AUDIT_REPORT.md §1 / §3.1 — Critical 1 (DEV-FE-1)
- TEST_REPORT.md TG-2d §2.2 + §2.3 — 시연 결과 (Sharpe 1.5971 / 누적 155.74%)
- ADR 0026 / 0027 — DBG-1 / DBG-2 영역 영역 일관성
- 양면 정책 일관성 — ADR 0012 / 0019 / 0026 / 0027

---

## 카드 누적 영역

- ADR 0011-0028 = **양면 정책 18 ADR** (정착 10 / 보류 4 / 메타 4 / 정리 1).
- Phase 1 종료 (DBG-1 + DBG-2 + DEV-FE-1) → Phase 2 Major 11 카드 진입 영역.
