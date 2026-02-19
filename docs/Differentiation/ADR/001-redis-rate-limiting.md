# ADR-001: Redis 기반 Rate Limiting

## 상태: Accepted

---

## 맥락 (Context)

auth-service의 로그인(`/api/auth/login`)과 회원가입(`/api/auth/signup`) 엔드포인트에 호출 제한이 없었다. 공격자가 봇으로 초당 수천 건의 로그인 요청을 보내 Brute Force 공격을 수행할 수 있었고, 비밀번호 복잡성 검증이 없던 시점에서는 "aaaaaaaa" 같은 비밀번호가 몇 초면 뚫리는 상황이었다.

**요구사항**:
- IP당 분당 최대 요청 수 제한
- 다중 인스턴스(스케일 아웃) 환경에서도 정확한 카운팅
- 윈도우 만료 후 자동 리셋
- 429 응답에 `Retry-After` 헤더 포함

---

## 고려한 선택지

### 옵션 A: In-Memory ConcurrentHashMap

- **장점**: 외부 의존성 없음, 구현 단순
- **단점**: 인스턴스 간 공유 불가 → 3대 서버면 30회/분 허용, 서버 재시작 시 카운터 초기화, 메모리 누수 위험 (만료 처리 직접 구현 필요)

### 옵션 B: Redis Counter + TTL

- **장점**: 다중 인스턴스 공유, `INCR`이 원자적 연산, `EXPIRE`로 자동 만료, 이미 auth-service가 Redis를 사용 중 (refresh token 저장)
- **단점**: Redis 장애 시 rate limiting 무력화 (fail-open vs fail-close 결정 필요)

### 옵션 C: API Gateway (nginx rate_limit)

- **장점**: 애플리케이션 코드 변경 없음, 검증된 솔루션
- **단점**: 현재 아키텍처에 API Gateway 없음, 추가 인프라 도입 비용, 엔드포인트별 세밀한 제어 어려움

---

## 결정 (Decision)

**옵션 B: Redis Counter + TTL** 선택.

```java
String key = RATE_LIMIT_PREFIX + path + ":" + clientIp;
Long currentCount = redisTemplate.opsForValue().increment(key);  // 원자적 증가
if (currentCount == 1) {
    redisTemplate.expire(key, WINDOW_SECONDS, TimeUnit.SECONDS); // 첫 요청 시 TTL 설정
}
if (currentCount > MAX_REQUESTS_PER_MINUTE) {
    // 429 Too Many Requests + Retry-After 헤더
}
```

**선택 이유**:
- auth-service가 이미 Redis를 사용 중 → 인프라 추가 비용 제로
- `INCR` 명령은 단일 명령어로 읽기+증가+반환이 원자적 → 동시 요청에도 정확
- `EXPIRE`로 TTL 설정 → 윈도우 만료 시 Redis가 자동 삭제 → 메모리 누수 없음
- Spring `HandlerInterceptor`로 구현 → Security Filter Chain과 분리, 테스트 용이

---

## 결과 (Consequences)

**장점**:
- Brute Force 방어: IP당 분당 10회 → 10만 개 비밀번호 시도에 약 7일 소요
- 정확한 분산 카운팅: 서버가 몇 대든 Redis에서 통합 관리
- 자동 정리: TTL 만료로 메모리 관리 불필요
- 테스트: 6개 테스트 케이스 (제한 이내, 초과 429, IP별 독립, Retry-After, 다른 경로 미적용, 리셋)

**트레이드오프**:
- Redis 장애 시 rate limiting 비활성화 (현재 fail-open 정책 — 가용성 우선)
- `INCR` + `EXPIRE`가 별도 명령이므로 INCR 후 서버 크래시 시 TTL 미설정 가능 (Lua 스크립트로 개선 가능)
- Fixed Window 방식이라 윈도우 경계에서 burst 가능 (Sliding Window Log로 개선 가능)

---

## 재선택한다면?

같은 선택. 단, 프로덕션에서는 두 가지 개선을 고려:
1. `INCR` + `EXPIRE`를 **Lua 스크립트**로 묶어 원자성 보장
2. Fixed Window → **Sliding Window Counter** (두 윈도우의 가중 평균)로 burst 방지
