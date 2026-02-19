# Frontend 면접 포인트

## 30초 스토리

> "Next.js 16 + React 19 기반 프론트엔드를 3관점(시니어 프론트엔드, UX·UI, 보안·통신) 코드 리뷰를 통해 21개 이슈를 발견하고 우선순위별로 전부 수정했습니다. 특히 accessToken localStorage 노출, Route Guard 부재, API 인터셉터 없음 등 Critical 보안 이슈 4개를 먼저 해결했고, 전체 UI 한국어화, controlled input 전환, Zustand hydration mismatch 해결까지 프로덕션 배포 가능한 수준으로 완성했습니다."

---

## 이슈별 면접 포인트

### C1. Token 보안 — localStorage에서 메모리로

**한줄**: "accessToken을 Zustand persist에서 제외하여 메모리에만 보관하고, refreshToken만 별도 키로 localStorage에 저장합니다."

**깊이 답변**:
"기존에는 Zustand persist가 accessToken을 포함한 전체 상태를 localStorage에 JSON으로 저장했습니다. XSS가 한 줄만 성공해도 `JSON.parse(localStorage.getItem('aether-auth')).state.accessToken`으로 토큰을 탈취할 수 있었습니다. `partialize` 옵션에서 accessToken을 제외하여 JavaScript 메모리에만 존재하도록 변경했고, 페이지 새로고침 시에는 refreshToken으로 재발급받는 흐름입니다. refreshToken은 별도 키(`aether-refresh-token`)로 격리해서 Zustand state 객체와 분리했습니다."

**후속 Q&A**:
- Q: "메모리 토큰이면 새로고침마다 재발급인데 UX 문제 없나요?" → "refreshToken이 살아있으면 API 인터셉터가 자동으로 accessToken을 재발급합니다. 사용자 관점에서는 잠깐의 로딩 스피너 후 정상 진입이라 UX 저하가 거의 없습니다. 오히려 '로그인 상태가 갑자기 풀렸다'는 불만이 사라집니다."
- Q: "httpOnly cookie가 더 안전하지 않나요?" → "맞습니다. httpOnly cookie는 JavaScript에서 아예 접근 불가라 XSS에 완전 면역입니다. 다만 CSRF 방어가 추가로 필요하고, 백엔드가 쿠키 기반 인증을 지원해야 합니다. 현재 auth-service가 JWT Bearer 방식이라 메모리 토큰이 현실적 최선이고, 향후 BFF(Backend for Frontend) 패턴을 도입하면 httpOnly cookie로 전환할 수 있습니다."
- Q: "XSS가 발생하면 메모리 토큰도 위험하지 않나요?" → "XSS가 발생하면 `useAuthStore.getState().accessToken`으로 읽을 수 있어서 완전한 방어는 아닙니다. 하지만 localStorage와 차이는, localStorage는 XSS 종료 후에도 토큰이 남아있고, 메모리 토큰은 페이지를 닫으면 소멸합니다. 공격 윈도우를 '영구'에서 '세션 중'으로 줄인 거죠."

---

### C2. Route Guard — 인증 경계 설정

**한줄**: "dashboard layout에서 Zustand hydration 완료 후 `isAuthenticated`를 체크하여 미인증 시 `/login`으로 redirect합니다."

**깊이 답변**:
"Next.js App Router에서는 layout.tsx가 하위 모든 페이지를 감싸므로, `dashboard/layout.tsx` 한 곳에서 guard를 걸면 `/dashboard/*` 전체가 보호됩니다. 핵심은 `_hasHydrated` 플래그인데, Zustand persist는 비동기로 localStorage에서 상태를 복원하기 때문에 hydration 전에는 `isAuthenticated`가 항상 false입니다. hydration 전에 redirect하면 로그인한 사용자도 튕기게 되므로, `_hasHydrated`가 true가 될 때까지 로딩 스피너를 보여주고, 이후에 판단합니다."

**후속 Q&A**:
- Q: "middleware.ts로 하는 게 더 낫지 않나요?" → "Next.js middleware는 Edge Runtime에서 실행되어 모든 요청을 서버 레벨에서 차단할 수 있습니다. 하지만 Zustand 상태는 클라이언트에만 존재하므로 middleware에서 접근 불가합니다. 쿠키 기반 인증이면 middleware가 이상적이고, JWT Bearer 방식에서는 클라이언트 guard가 현실적입니다."
- Q: "서버 컴포넌트에서 guard는?" → "Server Component에서 cookies()로 인증 쿠키를 확인하는 게 가장 견고합니다. 현재 아키텍처에서는 JWT가 메모리에만 있어서 서버 컴포넌트가 토큰을 알 수 없으므로, Client Component guard를 선택했습니다."

---

### C3. API 인터셉터 — 401 자동 갱신 + 요청 큐

**한줄**: "axios 인터셉터로 토큰 자동 주입과 401 발생 시 refresh → 재시도를 구현하고, 동시 401은 큐로 처리합니다."

**깊이 답변**:
"`createApiClient()` 팩토리 함수가 request 인터셉터(토큰 주입)와 response 인터셉터(401 처리)를 설정합니다. 401이 발생하면 `isRefreshing` 플래그를 세우고 refresh API를 호출합니다. 이 사이에 들어오는 다른 401 요청들은 `failedQueue` 배열에 Promise로 저장되고, refresh 성공 시 새 토큰으로 일괄 재시도합니다. refresh 자체가 실패하면 `logout()` → `/login` redirect 합니다. refresh 요청은 인터셉터가 붙지 않은 별도 axios 인스턴스(`publicApi`)로 보내서 무한 루프를 방지합니다."

**후속 Q&A**:
- Q: "왜 fetch 대신 axios를 쓰셨나요?" → "인터셉터 패턴이 내장되어 있어서 401 자동 갱신 같은 cross-cutting concern을 깔끔하게 처리할 수 있습니다. fetch에서는 wrapper 함수를 직접 만들어야 하고, 요청 취소도 AbortController를 수동 관리해야 합니다."
- Q: "동시 401 큐가 없으면 어떻게 되나요?" → "5개 API를 동시에 호출했는데 모두 401이면, refresh가 5번 호출됩니다. 두 번째부터는 이미 교체된 refresh token으로 요청하니까 서버에서 reuse detection이 발동해서 전체 세션이 무효화됩니다. 큐 패턴은 이 문제를 방지합니다."
- Q: "retry 횟수 제한은?" → "현재는 1회만 retry합니다. `_retry` 플래그를 원래 요청의 config에 붙여서 같은 요청이 다시 401을 받으면 큐에 넣지 않고 즉시 reject합니다."

---

### M2. 전체 한국어화

**한줄**: "i18n 라이브러리 없이 10개 파일의 UI 텍스트를 직접 한국어로 전환했습니다."

**깊이 답변**:
"랜딩 페이지, 로그인/회원가입, 대시보드, 최적화, 백테스트, 채팅, Header, Sidebar, Footer 등 10개 파일의 모든 사용자 노출 텍스트를 한국어로 변환했습니다. 프로젝트명 'Aether'와 기술 용어('Sharpe Ratio' 등)는 영어를 유지했고, 에러 메시지, placeholder, aria-label까지 한국어로 통일했습니다."

**후속 Q&A**:
- Q: "i18n 라이브러리를 안 쓴 이유는?" → "현재 한국어 단일 언어이고 다국어 요구사항이 없습니다. next-intl이나 react-i18next를 도입하면 번들 크기 증가, 메시지 키 관리 부담, SSR 설정 복잡도가 추가됩니다. 다국어가 필요해지면 그때 도입하는 게 YAGNI 원칙에 맞습니다."
- Q: "다국어 전환이 필요해지면?" → "next-intl의 Server Component 지원이 좋습니다. `[locale]` 동적 세그먼트로 URL 기반 라우팅을 하고, 메시지 파일을 JSON으로 분리합니다. 현재 텍스트가 컴포넌트에 직접 있어서, 메시지 추출 스크립트를 돌리면 자동 마이그레이션이 가능합니다."

---

### M5. Controlled Input 전환

**한줄**: "defaultValue 기반 uncontrolled input을 value+onChange 기반 controlled input으로 전환하여 React 상태와 UI를 동기화했습니다."

**깊이 답변**:
"백테스트 페이지의 슬라이더가 `defaultValue='33'`이어서 사용자가 조절해도 React state가 갱신되지 않았습니다. 화면의 퍼센트 표시는 '33%'로 고정, 실제 DOM 값은 변경되어 있어서 state와 UI가 분리된 상태였습니다. `weights` Record를 `useState`로 관리하고 슬라이더의 `value` + `onChange`로 양방향 바인딩했습니다. 합계 100% 실시간 검증도 state 기반이라 가능해졌습니다."

**후속 Q&A**:
- Q: "Controlled vs Uncontrolled, 어떤 경우에 뭘 쓰나요?" → "폼 데이터를 실시간으로 검증하거나, 다른 UI와 연동하거나, 제출 전에 가공해야 하면 controlled. 단순한 검색창처럼 submit 시에만 값이 필요하면 uncontrolled + `useRef`가 re-render를 줄여서 성능이 좋습니다. 복잡한 폼은 react-hook-form이 둘의 장점을 결합합니다."
- Q: "성능 이슈는 없나요?" → "슬라이더를 빠르게 움직이면 매 픽셀마다 setState + re-render가 발생합니다. 현재 규모에서는 문제 없지만, 대규모 폼이면 `useDeferredValue`나 `useTransition`으로 우선순위를 낮추거나, debounce를 적용할 수 있습니다."

---

### M7. Zustand Hydration Mismatch

**한줄**: "Zustand persist의 `onRehydrateStorage` 콜백으로 `_hasHydrated` 플래그를 관리하고, hydration 전에는 auth-dependent UI를 렌더링하지 않습니다."

**깊이 답변**:
"SSR에서 Zustand state는 초기값(isAuthenticated=false)으로 렌더링됩니다. 클라이언트에서 hydrate되면 localStorage에서 true로 바뀌면서 서버/클라이언트 출력이 달라집니다. React는 이를 hydration mismatch로 감지하고 전체 subtree를 re-render합니다. Header에서 `_hasHydrated`가 false인 동안은 고정 크기 placeholder를 렌더링하고, hydration 완료 후에 실제 auth UI를 표시합니다. 서버와 클라이언트 모두 동일한 placeholder를 출력하므로 mismatch가 사라집니다."

**후속 Q&A**:
- Q: "suppressHydrationWarning으로 해결하면 안 되나요?" → "경고만 숨기지 실제 문제를 해결하지 않습니다. React가 전체 subtree를 재생성하는 비용은 그대로이고, 사용자에게 깜빡임이 보입니다. placeholder 패턴이 근본적 해결입니다."
- Q: "Next.js에서 hydration mismatch가 자주 발생하는 다른 케이스는?" → "Date.now(), Math.random() 같은 비결정적 값, window/document 접근, 브라우저 확장 프로그램이 DOM을 수정하는 경우 등이 있습니다. 일반적으로 useEffect 안에서 클라이언트 전용 로직을 실행하거나, dynamic import with `ssr: false`로 해결합니다."

---

## 기술 선택 근거

### Zustand vs Redux vs Recoil

| 기준 | Zustand | Redux Toolkit | Recoil |
|------|---------|---------------|--------|
| 보일러플레이트 | 최소 (create 한 줄) | 중간 (slice, store 설정) | 중간 (atom, selector) |
| 번들 크기 | ~1KB | ~11KB | ~20KB |
| React 19 호환 | ✅ | ✅ | ❌ (메인테이너 중단) |
| persist 미들웨어 | 내장 | redux-persist 별도 | 별도 구현 |
| SSR 지원 | `onRehydrateStorage` | 복잡한 설정 필요 | 실험적 |

**선택 이유**: React 19 호환, 최소 번들, persist 내장, Next.js SSR과의 hydration 처리가 간단.

### 메모리 토큰 vs localStorage vs httpOnly Cookie

| 기준 | 메모리 (현재) | localStorage | httpOnly Cookie |
|------|-------------|-------------|----------------|
| XSS 내성 | 중간 (세션 중만 노출) | 낮음 (영구 노출) | 높음 (JS 접근 불가) |
| CSRF 내성 | 높음 (헤더 전송) | 높음 (헤더 전송) | 낮음 (자동 전송) |
| 새로고침 유지 | ❌ (refresh 필요) | ✅ | ✅ |
| 백엔드 변경 | 불필요 | 불필요 | 쿠키 설정 필요 |

**선택 이유**: 백엔드 수정 없이 적용 가능한 최선. refreshToken으로 새로고침 시 복구. 향후 BFF 도입 시 httpOnly cookie 전환 계획.

### Server Component vs Client Component 판단 기준

| 기준 | Server Component | Client Component |
|------|-----------------|-----------------|
| 사용 조건 | 정적 콘텐츠, 데이터 fetch | useState, useEffect, 이벤트 핸들러 |
| SEO | ✅ (HTML 완성 전달) | ❌ (JS 실행 후 렌더링) |
| 번들 크기 | 0 (서버에서만 실행) | JS 번들에 포함 |

**적용 예시**:
- `page.tsx` (랜딩): 서버 컴포넌트 → SEO 최적화 (m3에서 'use client' 제거)
- `dashboard/*`: 클라이언트 컴포넌트 → useState, 이벤트 핸들러 필수
- `Footer.tsx`: 서버 컴포넌트 → 정적 콘텐츠만

### Controlled vs Uncontrolled Input

| 기준 | Controlled | Uncontrolled |
|------|-----------|-------------|
| 실시간 검증 | ✅ (매 입력마다) | ❌ (submit 시에만) |
| 다른 UI 연동 | ✅ (state 공유) | ❌ |
| 성능 | 매 입력마다 re-render | re-render 없음 |
| 적합한 경우 | 폼 검증, 동적 UI | 단순 입력, 대규모 폼 |

**적용 예시**: 백테스트 슬라이더는 합계 100% 실시간 검증이 필요해서 controlled 필수.

---

## 면접 킬러 답변

### "프론트엔드에서 가장 어려웠던 보안 이슈는?"

> "accessToken 저장 위치 설계요. localStorage는 XSS에 취약하고, httpOnly cookie는 CSRF 방어가 필요하며 백엔드 변경이 수반됩니다. 메모리 토큰 + refresh 자동 갱신을 선택했는데, 핵심은 '동시 401 큐 처리'였습니다. 5개 API가 동시에 401을 받으면 refresh가 5번 호출되어 서버의 reuse detection이 발동합니다. `isRefreshing` 플래그와 `failedQueue` Promise 배열로 첫 번째 401만 refresh를 실행하고 나머지는 대기시킨 뒤 새 토큰으로 일괄 재시도하는 패턴을 구현했습니다."

### "한국어화를 i18n 없이 한 이유는?"

> "YAGNI 원칙입니다. 현재 한국어 단일 언어이고, next-intl 도입 시 번들 +5KB, 메시지 키 관리, SSR 라우팅 복잡도가 추가됩니다. 다국어 요구사항이 확정되면 현재 컴포넌트의 텍스트를 메시지 파일로 추출하는 마이그레이션은 자동화 가능하고, URL 기반 `[locale]` 라우팅을 추가하면 됩니다. '나중에 필요할 수도 있으니까' 지금 도입하는 건 오버엔지니어링이라고 판단했습니다."

### "Next.js SSR에서 주의할 점은?"

> "세 가지입니다. 첫째, **hydration mismatch** — localStorage, Date.now() 같은 클라이언트 전용 값이 서버 렌더링과 달라지면 React가 전체 subtree를 재생성합니다. Zustand persist의 `_hasHydrated` 패턴으로 해결했습니다. 둘째, **'use client' 경계** — 불필요한 'use client'는 서버 컴포넌트의 SEO/성능 이점을 버리는 것이고, 필요한 곳에 안 붙이면 useState가 터집니다. 랜딩 페이지에서 'use client'를 제거해서 서버 렌더링으로 전환했습니다. 셋째, **window/document 접근** — 서버에는 브라우저 API가 없으므로 `typeof window !== 'undefined'` 가드가 필수입니다. authStore의 `getRefreshToken()`에서 이 패턴을 적용했습니다."

---

## 아키텍처 한눈에 보기

```
[Browser]
  ├── Landing (Server Component) ← SEO 최적화
  ├── Login/Signup (Client) ← API 통신
  └── Dashboard Layout (Client) ← Route Guard
       ├── Dashboard (Client)
       ├── Optimize (Client) ← Controlled Input
       ├── Backtest (Client) ← Controlled Input + 검증
       └── Chat (Client) ← ChatMessage 타입 통합

[State]
  Zustand (persist) → accessToken: 메모리만
                    → refreshToken: 별도 localStorage 키
                    → user, isAuthenticated: persist
                    → _hasHydrated: hydration 추적

[API Layer]
  createApiClient() → Request 인터셉터: 토큰 자동 주입
                    → Response 인터셉터: 401 → refresh → 큐 재시도
                    → publicApi: 인터셉터 없음 (login, signup, refresh)
                    → authApi: 인터셉터 있음 (logout, getMe)
```
