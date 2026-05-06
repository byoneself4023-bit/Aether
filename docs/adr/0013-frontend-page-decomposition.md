# ADR 0013 — Frontend 페이지 분리 정책 (D-3)

- **상태**: Accepted
- **일자**: 2026-05-06
- **관련 카드**: D-3 (`docs/agent-capability-audit/META_REVIEW.md` §2.2 페이지 회고 정착)
- **결정 근거**: META_REVIEW §2.2 + PRINCIPLES 패턴 6 + ADR 0011 / 0012 형식 인용

---

## 컨텍스트

백엔드는 라우터 / 서비스 / 모델 분리 본능 정착 (ADR 0001 microservice split + ADR 0002 module boundaries). 그러나 frontend는 단일 page.tsx 모놀리식 구조:

| 페이지 | LOC (D-3 진입 전) |
|---|---|
| `/dashboard/optimize/page.tsx` | 344 |
| `/dashboard/backtest/page.tsx` | 217 |

풀스택 자기 일관성 시그널 강화를 위해 frontend도 동일 분리 본능 적용.

---

## 결정

### 1. 200 LOC 임계 (페이지 / 컴포넌트 단위)

페이지 / 컴포넌트 / hook / utility 모두 **200 LOC 이하** 의무. 초과 시 분리 카드 진입.

### 2. 페이지 50 LOC 이하 (컴포넌트 조합만)

`app/dashboard/*/page.tsx`는 hook 호출 + 컴포넌트 조합만 — 비즈니스 로직 / JSX 본문 직접 포함 금지.

### 3. 비즈니스 로직 → hooks

- `frontend/src/hooks/useOptimize.ts`: 9 useState + handleOptimize + addTicker / removeTicker
- `frontend/src/hooks/useBacktest.ts`: 8 useState + handleBacktest + addTicker / removeTicker
- 페이지 props 폭발 방지: hook이 객체 1개 반환, 컴포넌트는 필요 props만 destructure

### 4. UI → 컴포넌트

| 페이지 | 컴포넌트 분리 |
|---|---|
| optimize | OptimizeForm / MetricsCards / AllocationChart / AIAnalysisPanel / ResultDisplay |
| backtest | BacktestForm / MetricsGrid / PerformanceChart / ResultsView |

### 5. 재사용 utility → /lib/utils/

`cleanAnalysisText()` (D-0에서 추가됨) → `frontend/src/lib/utils/text.ts` 추출.

---

## 영향

### 시그널 강화 (+)

- 가독성 / 유지보수성 강화 (페이지 50 LOC 이하 = 한 화면에 전체 흐름 파악)
- 컴포넌트 단위 테스트 가능 (vitest fine-grained 도입 시)
- **풀스택 자기 일관성** (백엔드 라우터 분리 ✓ + frontend 페이지 분리 ✓)

### LOC 결과 (D-3 후)

| 페이지 | Before | After |
|---|---|---|
| optimize/page.tsx | 344 | **42** |
| backtest/page.tsx | 217 | **39** |

### Reversibility (Type 2)

- git revert로 1줄 롤백 가능
- 컴포넌트 / hook 위치는 표준 디렉토리 구조 — 재합치기도 가능

---

## 미적용 영역 (시나리오 B 진입 시 트리거)

| 영역 | 트리거 조건 |
|---|---|
| shadcn/ui 정착 | Houseman 진화 + 디자인 시스템 필요 시점 |
| WCAG 접근성 (aria-label / 키보드 navigation) | 실 사용자 발생 시점 (시나리오 A 후순위) |
| 컴포넌트 단위 테스트 fine-grained | 회귀 자동화 우선순위 격상 시점 |
| Storybook | 컴포넌트 카탈로그 필요 시점 |
| React Server Components 활용 | Next.js 15+ data fetching 패턴 도입 시점 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **F-N (frontend 강화)** | 시나리오 B 진입 | shadcn/ui / WCAG / Storybook / RSC |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-06 | v1 | 초기 Accepted (D-3 산출). 200 LOC 임계 + hooks + 컴포넌트 분리 정책 정착. ADR 0011 / 0012 형식 인용. |
