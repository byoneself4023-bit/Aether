# Auth-Service 면접 포인트

## 30초 스토리

> "Spring Boot 기반 인증 서비스를 3관점(보안 전문가, 시니어 백엔드, DevOps) 코드 리뷰를 통해 19개 이슈를 발견하고 우선순위별로 전부 수정했습니다. 특히 JWT 시크릿 하드코딩, Rate Limiting 부재, Refresh Token 탈취 감지 누락 같은 Critical 보안 이슈 6개를 먼저 해결하고, Flyway 마이그레이션, 구조화 로깅 등 운영 이슈까지 처리하면서 테스트를 24개에서 62개로 늘렸습니다."

---

## 이슈별 면접 포인트

### C1. JWT Secret 관리

**한줄**: "JWT 시크릿이 소스코드에 평문으로 커밋되어 있어서 환경변수 필수 + 앱 시작 시 검증으로 수정했습니다."

**깊이 답변**:
"application.yml에 시크릿이 평문으로 있고 docker 프로파일의 fallback도 동일한 문자열이어서, 레포 접근 권한이 있는 누구나 ADMIN 토큰을 위조할 수 있었습니다. `JwtProperties`에 `@PostConstruct` 검증을 추가해서 시크릿 미설정이면 앱 자체가 뜨지 않도록 했고, 32바이트 미만 키도 거부합니다. 이미 커밋된 시크릿은 로테이션이 필요한 상황입니다."

**후속 Q&A**:
- Q: "HS256 vs RS256 중 뭘 쓰셨고, 왜?" → "HS256(대칭키)을 사용했습니다. 단일 서비스에서는 키 관리가 간단하지만, MSA에서 여러 서비스가 토큰을 검증해야 하면 RS256(비대칭키)이 적합합니다. 비밀키는 auth-service만 갖고 공개키를 다른 서비스에 배포하면 됩니다."
- Q: "시크릿 로테이션은 어떻게?" → "kid(Key ID) claim을 사용해서 여러 키를 동시에 지원하고, 새 키로 발급하면서 이전 키는 만료까지만 검증 허용합니다."

---

### C4. Rate Limiting

**한줄**: "Redis sliding window 기반 IP당 분당 10회 제한으로 brute force 공격을 차단했습니다."

**깊이 답변**:
"로그인 API에 호출 제한이 없어서 credential stuffing 공격에 노출되어 있었습니다. Redis의 `INCR` + `EXPIRE`로 sliding window 카운터를 구현하고, 429 응답에 `Retry-After` 헤더를 포함시켰습니다. `/api/auth/login`과 `/signup`에만 적용하고, `/health`, `/actuator`는 제외했습니다."

**후속 Q&A**:
- Q: "IP 기반 제한의 한계는?" → "NAT 뒤의 사용자가 같은 IP를 공유하면 정상 사용자도 차단될 수 있습니다. 개선 방향으로 계정당 제한(이메일 기준)을 추가하고, IP + 계정 복합 키를 사용할 수 있습니다."
- Q: "Token Bucket vs Sliding Window 차이는?" → "Token Bucket은 버스트를 허용하고 Sliding Window는 균일한 제한입니다. 로그인 API는 버스트를 허용하면 안 되니까 Sliding Window를 선택했습니다."
- Q: "분산 환경에서 Rate Limiting은?" → "Redis가 중앙 저장소 역할을 하니까 서버가 여러 대여도 IP당 카운트가 공유됩니다. Redis 자체가 죽으면 fail-open(제한 없이 통과) vs fail-close(전부 차단) 정책을 선택해야 하는데, 보안 API라서 fail-close가 적합합니다."

---

### C5. Refresh Token Reuse Detection

**한줄**: "이미 사용된 refresh token으로 재요청이 오면 토큰 탈취로 판단하고 해당 유저의 전체 세션을 무효화합니다."

**깊이 답변**:
"Refresh token에 jti(JWT ID)를 추가하고 Redis에 저장합니다. refresh 요청 시 토큰 값과 jti를 모두 검증하는데, 하나라도 불일치하면 `invalidateAllTokens()`로 해당 유저의 refresh token + jti를 전부 삭제합니다. 공격자가 탈취한 토큰으로 먼저 refresh하면, 정상 사용자가 refresh할 때 불일치가 감지되어 전체 세션이 날아가고 재로그인을 강제합니다."

**후속 Q&A**:
- Q: "Token Family란?" → "같은 refresh token 체인에서 파생된 토큰들을 하나의 family로 묶는 개념입니다. family ID를 jti 대신 사용하면 여러 디바이스에서의 동시 로그인을 family별로 관리할 수 있습니다."
- Q: "정상 사용자가 세션 무효화되면?" → "맞습니다. 정상 사용자도 재로그인해야 합니다. 하지만 보안 관점에서 '탈취 가능성이 있는 상태에서 계속 사용'보다 '재로그인 강제'가 안전합니다."

---

### C6. Access Token 블랙리스트

**한줄**: "로그아웃 시 access token을 Redis 블랙리스트에 등록하여 즉시 무효화합니다."

**깊이 답변**:
"기존에는 로그아웃해도 access token이 30분(만료시간)까지 유효했습니다. Redis에 토큰을 key로, TTL을 잔여 만료시간으로 저장하면 만료되면 자동 삭제됩니다. `JwtAuthenticationFilter`에서 `validateToken()` 통과 후 `isBlacklisted()` 체크를 추가했습니다."

**후속 Q&A**:
- Q: "매 요청마다 Redis 조회하면 성능 이슈는?" → "Redis `EXISTS` 명령은 O(1)이고 보통 0.1ms 이내입니다. 블랙리스트는 TTL이 최대 30분이라 데이터도 작습니다. 정 걱정되면 로컬 캐시(Caffeine)를 앞에 두고 1분 TTL로 설정할 수 있습니다."
- Q: "블랙리스트 vs 화이트리스트 차이는?" → "블랙리스트는 '차단 목록'이라 대부분 요청이 Redis를 안 타지만, 화이트리스트는 '허용 목록'이라 모든 요청이 Redis를 탑니다. JWT의 stateless 장점을 최대한 유지하려면 블랙리스트가 적합합니다."

---

### M1. Flyway 마이그레이션

**한줄**: "프로덕션에서 `ddl-auto: validate`로 변경하고 Flyway로 버전 관리된 마이그레이션을 도입했습니다."

**깊이 답변**:
"Hibernate `ddl-auto: update`는 컬럼 추가만 할 수 있고 삭제/이름변경은 못 합니다. 개발자가 엔티티를 수정하면 예기치 않은 스키마 변경이 프로덕션에 적용되고 롤백도 불가능합니다. Flyway를 도입해서 `V1__init.sql`로 초기 스키마를 관리하고, 프로덕션은 `validate`(검증만), 로컬은 `update` 유지했습니다."

**후속 Q&A**:
- Q: "Flyway vs Liquibase 차이는?" → "Flyway는 SQL 기반이라 직관적이고 PostgreSQL 네이티브 문법을 그대로 씁니다. Liquibase는 XML/YAML로 DB 독립적이지만 복잡합니다. 단일 DB를 쓰는 서비스라 Flyway가 적합합니다."
- Q: "롤백은 어떻게?" → "Flyway Community는 자동 롤백을 지원하지 않아서, `V2__rollback_xxx.sql`처럼 수동 롤백 스크립트를 작성합니다. Flyway Teams(유료)는 `undo` 명령을 지원합니다."

---

### M4. JWT 에러 응답 통일

**한줄**: "`CustomAuthenticationEntryPoint`로 모든 401 응답을 `ApiResponse` JSON 형식으로 통일했습니다."

**깊이 답변**:
"Spring Security 기본 `AuthenticationEntryPoint`는 HTTP Basic 스타일의 에러 페이지를 반환합니다. 프론트엔드가 `ApiResponse` 형식만 파싱하면 토큰 만료 시 '알 수 없는 에러'가 표시됩니다. `CustomAuthenticationEntryPoint`에서 `ObjectMapper`로 `ApiResponse.error()`를 JSON 직렬화하여 응답합니다."

**후속 Q&A**:
- Q: "AccessDeniedHandler와 차이는?" → "AuthenticationEntryPoint는 '인증 안 됨(401)', AccessDeniedHandler는 '인증은 됐지만 권한 없음(403)'입니다. 둘 다 커스텀해야 일관된 에러 형식을 유지합니다."

---

### m2. 구조화된 로깅

**한줄**: "MDC 기반 requestId/clientIp + JSON 로그 포맷으로 ELK에서 요청 추적이 가능하도록 했습니다."

**깊이 답변**:
"`MdcLoggingFilter`가 모든 요청에 UUID requestId와 clientIp를 MDC에 설정합니다. `logback-spring.xml`에서 로컬은 평문, docker 프로파일은 `logstash-logback-encoder`로 JSON 출력합니다. 응답에 `X-Request-ID` 헤더를 포함시켜서 프론트엔드가 에러 리포트에 requestId를 첨부하면 백엔드 로그와 즉시 매칭할 수 있습니다."

**후속 Q&A**:
- Q: "MDC가 뭔가요?" → "Mapped Diagnostic Context, 스레드 로컬 변수에 키-값을 저장하고 로그 출력 시 자동 포함합니다. 요청 처리가 끝나면 `MDC.clear()`로 정리해야 스레드 풀에서 데이터가 섞이지 않습니다."
- Q: "분산 추적은?" → "현재는 단일 서비스라 requestId면 충분하지만, MSA에서는 Spring Cloud Sleuth나 OpenTelemetry로 traceId/spanId를 전파해야 서비스 간 요청 흐름을 추적할 수 있습니다."

---

## 기술 선택 근거 요약

| 선택 | 대안 | 선택 이유 |
|------|------|-----------|
| Redis Rate Limiting | Bucket4j, Guava | 분산 환경 지원, 서버 간 카운트 공유 |
| Flyway | Liquibase | SQL 기반 직관성, PostgreSQL 네이티브 |
| jti claim | Token Family | 단일 서비스에서 충분, 구현 단순 |
| Redis 블랙리스트 | 매 요청 DB 조회 | O(1) 조회, TTL 자동 정리 |
| logstash-logback-encoder | 자체 JSON 포매터 | 표준 ELK 호환, 유지보수 불필요 |
| @PostConstruct 검증 | EnvironmentPostProcessor | 에러 메시지 명확, 디버깅 용이 |

---

## 면접 킬러 답변

### "auth-service에서 가장 어려웠던 부분은?"

> "Refresh Token Reuse Detection이요. 단순히 토큰을 교체하는 게 아니라, '이미 교체된 토큰이 다시 들어오면 탈취로 판단하고 전체 세션을 무효화'하는 로직이 필요했습니다. jti claim과 Redis를 조합해서 토큰 체인의 일관성을 보장하면서도, 정상 사용자가 재로그인하면 바로 복구되도록 설계했습니다."

### "보안 점수가 5/10 → 8.5/10으로 개선된 핵심은?"

> "세 가지입니다. 첫째, 시크릿 관리 — 코드에서 완전히 분리하고 시작 시 검증. 둘째, 토큰 생명주기 — 발급부터 갱신, 로그아웃, 탈취 감지까지 전체 흐름을 방어. 셋째, 입구 방어 — Rate Limiting으로 brute force 자체를 차단."

### "이 프로젝트가 실무와 다른 점은?"

> "실무에서는 AWS Secrets Manager나 Vault로 시크릿을 관리하고, WAF 레벨에서 Rate Limiting을 걸 수 있습니다. 하지만 애플리케이션 레벨에서도 방어해야 하는 이유는, WAF가 우회되거나 내부 네트워크에서의 공격에 대비하기 위해서입니다. 저는 '인프라가 도와줄 거야'가 아니라 '애플리케이션 자체가 안전해야 한다'는 관점으로 구현했습니다."
