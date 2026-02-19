# ADR-005: 프론트엔드 토큰 저장 전략

## 상태: Accepted

---

## 맥락 (Context)

프론트엔드에서 JWT Access Token과 Refresh Token을 어디에 저장할지 결정해야 했다. OWASP 가이드라인에 따르면 토큰 저장은 XSS와 CSRF 공격 벡터를 모두 고려해야 한다.

**제약 조건**:
- SPA(Single Page Application) 아키텍처 → 클라이언트에서 토큰 관리
- auth-service는 별도 도메인(포트 8003) → httpOnly Cookie 설정에 제약 (SameSite, CORS)
- 새로고침 시 사용자가 재로그인하지 않아야 함
- XSS 공격 시 accessToken 탈취를 최소화해야 함

---

## 고려한 선택지

### 옵션 A: localStorage에 모든 토큰 저장

- **장점**: 구현 단순, 새로고침 생존, 모든 브라우저 지원
- **단점**: XSS 한 줄이면 accessToken + refreshToken 모두 탈취 가능 (`localStorage.getItem()`), OWASP에서 민감 데이터 저장을 비권장

### 옵션 B: httpOnly Cookie

- **장점**: JavaScript 접근 불가 → XSS로 토큰 직접 탈취 불가능
- **단점**: auth-service와 다른 도메인이면 `SameSite=None; Secure` 필요 → HTTPS 필수, CSRF 공격에 취약 → CSRF 토큰 별도 관리, 프론트엔드에서 토큰 내용(만료시간 등) 확인 불가

### 옵션 C: sessionStorage

- **장점**: 탭 닫으면 자동 삭제 → 공유 PC 안전
- **단점**: 새 탭에서 인증 상태 공유 불가, 새로고침은 생존하지만 탭 간 동기화 불가

### 옵션 D: accessToken 메모리 + refreshToken localStorage (하이브리드)

- **장점**: accessToken은 XSS로 localStorage에서 탈취 불가 (메모리에만 존재), refreshToken은 새로고침 생존, 새로고침 시 refreshToken으로 accessToken 재발급
- **단점**: 새로고침 시 한 번의 refresh 요청 필요 (~100ms 지연), refreshToken은 여전히 localStorage에 존재 → XSS 위험 잔존 (단, refresh 단독으로는 API 접근 불가)

---

## 결정 (Decision)

**옵션 D: accessToken 메모리 + refreshToken localStorage (하이브리드)** 선택.

```
┌─────────────────────────────────────────────────────┐
│  Access Token                                       │
│  저장: Zustand state (JavaScript 메모리)              │
│  수명: 30분                                          │
│  XSS 탈취: 불가능 (localStorage에 없음)               │
│  새로고침 시: 소멸 → refresh로 재발급                   │
├─────────────────────────────────────────────────────┤
│  Refresh Token                                      │
│  저장: localStorage ('aether-refresh-token' 키)      │
│  수명: 7일                                           │
│  XSS 탈취: 가능하지만 단독으로 API 접근 불가            │
│  용도: accessToken 재발급 전용                        │
└─────────────────────────────────────────────────────┘
```

**선택 이유**:
- httpOnly Cookie는 auth-service가 별도 포트(8003)에서 동작하므로 CORS + SameSite 설정이 복잡해지고, 개발 환경(HTTP)에서 Secure 플래그 사용 불가
- accessToken이 메모리에만 있으면 XSS로 localStorage를 덤프해도 accessToken 없음
- refreshToken이 탈취되어도 단독으로 API 호출 불가 — `/api/auth/refresh`로 새 accessToken을 받아야 함, 이때 서버에서 Reuse Detection (ADR-002) 발동
- Zustand `partialize`로 accessToken을 persist에서 제외하는 것이 자연스러움

---

## 결과 (Consequences)

**장점**:
- XSS 방어 강화: accessToken이 localStorage에 평문으로 노출되지 않음
- 새로고침 생존: refreshToken으로 자동 재발급 (axios 인터셉터에서 처리)
- 다중 계층 방어: refreshToken 탈취 시에도 Reuse Detection + 전체 세션 무효화 (서버 측)
- 구현 단순: Zustand `partialize` + `onRehydrateStorage`로 자연스럽게 구현

**트레이드오프**:
- 새로고침 시 ~100ms의 토큰 재발급 지연 (사용자 체감 불가 수준)
- refreshToken은 여전히 XSS에 노출 → CSP 헤더 + 입력 sanitize로 XSS 자체를 방지하는 것이 근본적 해결
- 탭 간 accessToken 불일치 가능 → 각 탭이 독립적으로 refresh 수행

---

## 재선택한다면?

프로덕션에서는 **BFF(Backend for Frontend) 패턴**을 도입하고 httpOnly Cookie를 사용하겠다. Next.js API Routes를 프록시로 활용하면 같은 도메인에서 Cookie를 설정할 수 있고, 프론트엔드 JavaScript에서 토큰을 아예 다루지 않게 된다. 현재는 아키텍처 복잡도와 개발 편의성을 고려해 하이브리드 방식을 선택했다.
