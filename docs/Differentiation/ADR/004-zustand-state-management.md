# ADR-004: Zustand 상태 관리

## 상태: Accepted

---

## 맥락 (Context)

Aether 프론트엔드는 Next.js 16 + React 19 기반이다. 다음 전역 상태를 관리해야 한다:
- 인증 상태: user, accessToken, isAuthenticated
- UI 상태: 사이드바 open/close, 테마

별도의 서버 상태(캐싱, 뮤테이션)는 현재 범위에 없고, API 호출은 axios 인터셉터 + 컴포넌트 로컬 state로 처리한다.

**요구사항**:
- SSR(Server-Side Rendering)과 호환
- localStorage persist (새로고침 시 상태 유지)
- hydration mismatch 방지
- 보일러플레이트 최소화

---

## 고려한 선택지

### 옵션 A: Redux Toolkit

- **장점**: 업계 표준, DevTools 우수, 미들웨어 생태계 (thunk, saga), 대규모 팀에서 검증됨
- **단점**: slice + action + reducer 보일러플레이트, 현재 전역 상태가 2~3개뿐인데 과도, `redux-persist` 별도 설치 필요

### 옵션 B: Zustand 5

- **장점**: 보일러플레이트 최소 (함수 하나로 store 생성), 내장 `persist` 미들웨어, `partialize`로 특정 필드만 persist 가능, React 외부에서도 `getState()` 접근 가능 (인터셉터에서 활용), 번들 크기 ~1KB
- **단점**: 대규모 앱에서의 레퍼런스가 Redux 대비 적음, 미들웨어 생태계가 작음

### 옵션 C: Recoil / Jotai

- **장점**: 원자(atom) 기반 → 세밀한 리렌더링 최적화, React Suspense 호환
- **단점**: Recoil은 Meta 내부 사용 중심 + 유지보수 불투명, Jotai는 persist가 별도 라이브러리, atom 기반이라 토큰 관리에는 overkill

### 옵션 D: React Context API

- **장점**: 추가 라이브러리 없음, React 내장
- **단점**: context 값 변경 시 하위 컴포넌트 전부 리렌더링, persist/hydration을 직접 구현해야 함, 복잡한 상태 로직에는 부적합

---

## 결정 (Decision)

**옵션 B: Zustand 5** 선택.

```typescript
export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      _hasHydrated: false,

      setTokens: (accessToken, refreshToken) => {
        localStorage.setItem('aether-refresh-token', refreshToken);
        set({ accessToken, isAuthenticated: true });
      },

      logout: () => {
        localStorage.removeItem('aether-refresh-token');
        set({ user: null, accessToken: null, isAuthenticated: false });
      },
    }),
    {
      name: 'aether-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        // accessToken 제외 → 메모리에만 보관
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
```

**선택 이유**:
- 전역 상태가 인증(5개 필드) + UI(2개 필드) 수준 → Redux의 slice/action/reducer 패턴이 불필요
- `partialize`: accessToken을 persist에서 제외하는 것이 한 줄로 가능 → 보안 요구사항 충족
- `getState()`: React 컴포넌트 외부(axios 인터셉터)에서 토큰 접근 필요 → Zustand는 React 트리 밖에서도 동작
- `onRehydrateStorage`: SSR hydration 완료 시점을 알 수 있음 → `_hasHydrated`로 hydration mismatch 방지

---

## 결과 (Consequences)

**장점**:
- 보일러플레이트 제로: Redux 대비 코드량 약 70% 감소
- 보안 통합: `partialize`로 accessToken을 localStorage에서 자연스럽게 제외
- 인터셉터 통합: `useAuthStore.getState().accessToken`으로 React 외부에서 토큰 접근
- SSR 안정: `_hasHydrated` 패턴으로 서버/클라이언트 출력 일치 보장

**트레이드오프**:
- DevTools: Redux DevTools만큼 상세하지 않음 (별도 zustand devtools 미들웨어 추가 가능)
- 팀 규모 확장 시 Redux의 명시적 action/reducer 패턴이 코드 리뷰에 유리할 수 있음
- 미들웨어 생태계: Redux saga/thunk 같은 고급 비동기 패턴이 필요하면 직접 구현 필요

---

## 재선택한다면?

같은 선택. 현재 프로젝트 규모에서 Zustand는 최적이다. 팀이 10명 이상이고 상태가 20개 이상의 slice로 분리되어야 하면 Redux Toolkit을 고려하겠지만, 그 시점에는 서버 상태를 TanStack Query로 분리하는 것이 우선이다.
