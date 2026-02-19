# ADR-002: JWT 토큰 인증 전략

## 상태: Accepted

---

## 맥락 (Context)

Aether는 4개 마이크로서비스(auth, portfolio, llm, frontend)로 구성된다. 사용자 인증 정보를 서비스 간에 전달하고, 인증 상태를 관리하는 전략이 필요했다.

**요구사항**:
- 서비스 간 stateless 인증 (서비스마다 세션 서버를 두지 않음)
- 로그아웃 시 즉시 무효화
- Refresh Token Rotation으로 토큰 탈취 감지
- 수평 확장(스케일 아웃) 시 인증 병목 없음

---

## 고려한 선택지

### 옵션 A: Server-Side Session (Spring Session + Redis)

- **장점**: 즉시 무효화 가능 (세션 삭제), 구현 단순, 서버가 세션 데이터 완전 제어
- **단점**: 매 요청마다 Redis 조회 필수 → 네트워크 홉 추가, Redis 장애 = 전체 인증 장애, 마이크로서비스마다 세션 공유 설정 필요

### 옵션 B: JWT (Access + Refresh) + Redis 블랙리스트

- **장점**: Stateless — 서명 검증만으로 인증, 서비스 간 토큰 전달 용이 (Authorization 헤더), 블랙리스트로 즉시 무효화 보완
- **단점**: 토큰 크기가 세션 ID보다 큼, 블랙리스트를 위해 결국 Redis 필요 → 순수 stateless 아님

### 옵션 C: OAuth2 + Authorization Server (Keycloak 등)

- **장점**: 표준 프로토콜, SSO 지원, 소셜 로그인 확장 용이
- **단점**: Keycloak 서버 추가 운영 부담, 학습 곡선 높음, 프로젝트 규모 대비 과도한 복잡도

---

## 결정 (Decision)

**옵션 B: JWT (Access + Refresh) + Redis 블랙리스트** 선택.

```
[Access Token]
- 수명: 30분
- 용도: API 인증 (Authorization: Bearer ...)
- 저장: 프론트엔드 메모리 (Zustand state)
- 무효화: Redis 블랙리스트 (TTL = 잔여 만료시간)

[Refresh Token]
- 수명: 7일
- 용도: Access Token 갱신
- 저장: 프론트엔드 localStorage, 서버 Redis
- 보안: JTI(고유 ID)로 Reuse Detection → 탈취 시 전체 세션 무효화
```

**선택 이유**:
- Access Token의 서명 검증만으로 인증 → portfolio-service, llm-service에서 Redis 조회 없이 검증 가능
- 로그아웃 시 Access Token 블랙리스트 등록 (TTL = 잔여 수명) → 만료 후 Redis에서 자동 삭제
- Refresh Token에 JTI 부여 + Redis 저장 → 탈취된 토큰으로 갱신 시도 시 불일치 감지 → 전체 세션 무효화
- auth-service만 Redis 의존, 나머지 서비스는 JWT 서명 검증만 수행

---

## 결과 (Consequences)

**장점**:
- 서비스 간 인증: portfolio, llm 서비스가 JWT 서명 키만 공유하면 독립적으로 인증 가능
- 즉시 무효화: 블랙리스트로 로그아웃 즉시 반영 (순수 JWT의 "만료까지 대기" 문제 해결)
- Reuse Detection: Refresh Token 탈취 시 경고 로그 + 전체 세션 무효화
- 자동 정리: 블랙리스트 TTL = 토큰 잔여 수명 → 만료 후 Redis에서 자동 삭제

**트레이드오프**:
- 순수 stateless가 아님: 블랙리스트 체크를 위해 매 요청마다 Redis 조회 (auth-service만)
- 토큰 크기: 세션 ID 대비 JWT는 ~500 bytes → 네트워크 오버헤드 미미하지만 존재
- 키 관리: JWT 서명 키를 안전하게 배포해야 함 (환경변수 + 최소 32바이트)

---

## 재선택한다면?

같은 선택. JWT + 블랙리스트 조합은 마이크로서비스 환경에서 가장 현실적인 밸런스다. 규모가 커지면 옵션 C (OAuth2 Authorization Server)로 전환하되, JWT 토큰 형식 자체는 유지할 수 있으므로 마이그레이션 비용이 낮다.
