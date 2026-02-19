# 장애 시뮬레이션 테스트

## 개요

| 항목 | 내용 |
|------|------|
| 목표 | 서비스 의존성 장애 시 graceful degradation 확인 |
| 방법 | 모킹 기반 장애 주입 (Mockito, unittest.mock) |
| 범위 | auth-service (8개) + portfolio-service (6개) = **14개 테스트** |
| 실행 환경 | Docker 없이 단위 테스트로 실행 가능 |

---

## auth-service 장애 시뮬레이션 (8개)

### A. Redis 장애

| # | 시나리오 | 기대 동작 | 결과 |
|---|---------|----------|------|
| A-1 | Redis 연결 실패 시 Rate Limiting | 현재: fail-close (예외 전파). 요청 차단됨 | 동작 문서화 완료 |
| A-2 | Redis 연결 실패 시 JWT 블랙리스트 체크 | 현재: 예외 전파. 블랙리스트 확인 불가 | 동작 문서화 완료 |
| A-3 | Redis 연결 실패 시 Refresh Token 저장 | 저장 실패 → RedisConnectionFailureException | PASS |

**발견 사항:**
- Rate Limiting과 JWT 필터에 Redis 장애 시 try-catch가 없음
- 프로덕션에서는 fail-open 전략 추가를 권장 (가용성 우선)
- 현재 동작은 보안 관점에서 fail-close (안전하지만 가용성 희생)

### B. DB 장애

| # | 시나리오 | 기대 동작 | 결과 |
|---|---------|----------|------|
| B-4 | PostgreSQL 연결 실패 시 회원가입 | RuntimeException 전파 → 500 에러 | PASS |
| B-5 | PostgreSQL 연결 실패 시 health check | status="degraded", HTTP 503, DB check="DOWN" | PASS |

### C. 외부 요청 이상 (JWT)

| # | 시나리오 | 기대 동작 | 결과 |
|---|---------|----------|------|
| C-6 | 잘못된 JWT 시그니처 | BusinessException(INVALID_TOKEN) → 401 | PASS |
| C-7 | 만료된 JWT | BusinessException(TOKEN_EXPIRED) → 401 | PASS |
| C-8 | 블랙리스트된 JWT | SecurityContext 비설정 → 인증 실패 | PASS |

---

## portfolio-service 장애 시뮬레이션 (6개)

### A. 외부 API 장애

| # | 시나리오 | 기대 동작 | 결과 |
|---|---------|----------|------|
| A-1 | yfinance 네트워크 에러 | 전체 실패 → ValueError("Insufficient valid tickers") | PASS |
| A-2 | yfinance 빈 데이터 반환 | 전체 실패 → ValueError("Insufficient valid tickers") | PASS |
| A-3 | 4개 중 2개만 성공 | 2개로 최적화 수행 + failed_tickers 리스트 반환 | PASS |

### B. 수치 안정성

| # | 시나리오 | 기대 동작 | 결과 |
|---|---------|----------|------|
| B-4 | 완전 상관(rho=1.0) 종목 | validate에서 탐지 → 정칙화 → 정상 최적화 | PASS |
| B-5 | 데이터 부족 (5일치) | 공분산 문제 시 정칙화 → 결과 반환 | PASS |
| B-6 | 음수 가중치 방지 | bounds=(0,1) → 모든 가중치 >= 0 | PASS |

---

## 장애 대응 전략 요약

| 장애 유형 | 전략 | 이유 | 구현 |
|-----------|------|------|------|
| **Redis 장애** | fail-close (현재) | 보안 우선 (Rate Limit, 블랙리스트) | 예외 전파 |
| **DB 장애** | fail-fast | 데이터 무결성 보장 | 즉시 에러 반환, health check에 반영 |
| **외부 API 장애** | partial failure | 가용성 우선 (일부 성공으로 계속) | FetchResult에 성공/실패 분리 |
| **수치 불안정** | auto-regularize | 결과 반환 우선 + 진단 정보 포함 | Covariance validation + ridge |

### 전략 간 트레이드오프

```
보안 ◀━━━━━━━━━━━━━━━━━━━━━▶ 가용성

fail-close          fail-open
(Redis 장애 시       (Redis 장애 시
 요청 차단)           요청 허용)

현재 auth-service:    권장 개선:
Redis 예외 전파       try-catch + 로그 + 허용
```

---

## 면접 포인트

### "Redis가 죽으면 어떻게 되나요?"

> 현재 auth-service는 **fail-close** 전략입니다. Redis가 죽으면 Rate Limiting과 블랙리스트 체크가 실패하면서 요청이 차단됩니다. 이는 보안 관점에서는 안전하지만 가용성을 희생합니다.
>
> 프로덕션에서는 **fail-open + 모니터링** 조합을 권장합니다: Redis 장애 시 Rate Limiting을 건너뛰되, 즉시 알림을 발송하고 복구를 진행합니다. 블랙리스트의 경우 Access Token TTL이 30분이므로, 최대 30분간의 위험을 수용하는 판단이 필요합니다.

### "외부 API가 느리면?"

> portfolio-service는 **partial failure** 전략을 씁니다. yfinance에서 4개 종목 중 2개만 성공하면, 성공한 2개로 최적화를 수행하고 실패한 종목을 `failed_tickers` 리스트에 담아 응답합니다. 최소 2개 이상 성공해야 하며, 미달 시 명확한 에러를 반환합니다.
>
> 데이터 수집은 개별 티커 단위로 수행하여 (batch가 아닌 개별 fetch), 하나의 실패가 전체를 막지 않도록 설계했습니다.

### "fail-open vs fail-close 차이는?"

> | | fail-open | fail-close |
> |---|-----------|------------|
> | 동작 | 장애 시 요청 허용 | 장애 시 요청 차단 |
> | 우선순위 | 가용성 | 보안/일관성 |
> | 적합 | 캐시, Rate Limiting | 결제, 인증 |
> | 위험 | 일시적 보안 약화 | 서비스 불가 |
>
> auth-service에서 Rate Limiting은 fail-open이 적합합니다 (Redis 잠깐 죽었다고 로그인 자체를 막으면 안 됨). 반면 결제 시스템이라면 fail-close가 맞습니다.
>
> 핵심은 **"이 기능이 실패했을 때, 허용하는 게 더 위험한가 vs 차단하는 게 더 위험한가"** 판단입니다.
