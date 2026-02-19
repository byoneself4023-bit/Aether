# Auth-Service 코드 리뷰 결과

## 개요

| 항목 | 내용 |
|------|------|
| 서비스 | auth-service (Java/Spring Boot 3.2.12) |
| 리뷰 관점 | 보안 전문가, 시니어 백엔드, DevOps/운영 (FAANG 시니어 기준) |
| 총 이슈 | 19개 (Critical 6 + Major 7 + Minor 6) |
| 테스트 변화 | 24 → 62개 (+38개) |
| 전부 해결 | ✅ |

## 종합 평가 (수정 후)

| 항목 | 수정 전 | 수정 후 | 비고 |
|------|---------|---------|------|
| 코드 구조 | 8/10 | 9/10 | JPA Auditing 분리, Config 정리 |
| API 설계 | 7.5/10 | 8.5/10 | 에러 응답 통일, CORS 정리 |
| 보안 | 5/10 | 8.5/10 | 시크릿 관리, Rate Limiting, 블랙리스트, 보안 헤더 |
| 테스트 | 6/10 | 8/10 | 24→62개, edge case 포함 |
| 운영 준비도 | 6/10 | 8.5/10 | Flyway, 구조화 로깅, Health Check, JVM 옵션 |

---

## Critical (보안 취약점, 즉시 수정)

### C1. JWT Secret 하드코딩 + 약한 키

**파일**: application.yml:29, application-docker.yml:30

**쉬운 설명**: JWT 시크릿이 코드에 박혀있었어요. 이 레포를 볼 수 있는 사람이면 누구나 `userId=1, role=ADMIN` 토큰을 만들어서 전체 시스템을 장악할 수 있었어요. 집 열쇠를 현관문에 테이프로 붙여놓은 것과 같아요.

**수정 내용**:
- application.yml: `jwt.secret` 기본값 제거, `${JWT_SECRET:}` placeholder만 유지
- application-docker.yml: fallback 제거 → `${JWT_SECRET}` (기본값 없이)
- `JwtProperties.validate()` 추가: 시크릿 미설정 시 `IllegalStateException`으로 앱 시작 실패
- 32바이트 미만 키도 거부

**테스트**: +5개 (시크릿 미설정, 짧은 키, 빈 값, 공백만, 정상 키)

---

### C2. DB 비밀번호 하드코딩

**파일**: application.yml:11

**쉬운 설명**: DB 아이디/비밀번호가 `aether / aether123`으로 코드에 박혀있었어요. 레포가 털리면 DB에 바로 접속해서 사용자 이메일, 해시된 비밀번호를 전부 빼갈 수 있었어요.

**수정 내용**:
- 환경변수로 분리: `${SPRING_DATASOURCE_USERNAME}`, `${SPRING_DATASOURCE_PASSWORD}`
- `.env.example` 생성 (필요한 환경변수 목록)
- `.gitignore`에 `.env` 추가

---

### C3. Bearer Token 파싱에 인덱스 하드코딩

**파일**: AuthController.java:60

**쉬운 설명**: 로그아웃할 때 `substring(7)`로 "Bearer " 접두사를 떼는데, "Bearer " 없이 보내면 `StringIndexOutOfBoundsException`이 터져서 500 에러가 났어요. 악의적 클라이언트가 이상한 헤더로 반복 요청하면 에러 로그가 폭발해요.

**수정 내용**:
- `resolveToken()` 메서드 추가: `startsWith("Bearer ")` 검증
- 실패 시 `BusinessException(ErrorCode.INVALID_TOKEN)` 반환
- `GlobalExceptionHandler`에 `MissingRequestHeaderException` 핸들러 추가

**테스트**: +4개 (정상 Bearer, Bearer 없음, 소문자 bearer, 헤더 자체 없음)

---

### C4. Rate Limiting 없음 (Brute Force 취약)

**파일**: SecurityConfig.java, 전반

**쉬운 설명**: 로그인 API에 호출 제한이 없어서 봇이 비밀번호를 초당 수천 번 시도할 수 있었어요. "aaaaaaaa" 같은 약한 비밀번호는 몇 초면 뚫려요.

**수정 내용**:
- Redis sliding window 기반 `RateLimitInterceptor` 구현
- `/api/auth/login`, `/api/auth/signup`에 IP당 분당 10회 제한
- 초과 시 429 Too Many Requests + `Retry-After` 헤더

**테스트**: +6개 (제한 이내 통과, 초과 시 429, IP별 독립 카운트, Retry-After 헤더, 다른 경로 미적용, 시간 경과 후 리셋)

---

### C5. Refresh Token Rotation 시 Reuse Detection 누락

**파일**: AuthService.java:82-110, JwtTokenProvider.java:57-78

**쉬운 설명**: 해커가 refresh token을 탈취해서 먼저 사용하면? 이전엔 감지를 못했어요. 이제 모든 refresh token에 고유 ID(jti)를 넣고, 이미 교체된 토큰으로 재요청이 오면 "누가 내 토큰을 훔쳤다" → 해당 유저의 **전체 세션을 즉시 무효화**해요.

**수정 내용**:
- `createRefreshToken()`에 `jti` (UUID) claim 추가 + Redis 저장
- `validateRefreshToken()`에서 토큰 불일치 또는 jti 불일치 시 `invalidateAllTokens()` 호출
- 경고 로그 기록

**테스트**: +2개 (다른 토큰으로 요청 시 세션 무효화, jti 불일치 시 세션 무효화)

---

### C6. Access Token 블랙리스트 없음 (로그아웃 불완전)

**파일**: AuthService.java:112-115, JwtAuthenticationFilter.java:37-48

**쉬운 설명**: 로그아웃해도 access token이 30분간 살아있었어요. 공용 PC에서 로그아웃하고 떠나도, 누군가 네트워크에서 토큰을 잡으면 30분간 내 계정으로 활동할 수 있었어요.

**수정 내용**:
- `blacklistAccessToken()`: Redis에 토큰 저장 (TTL = 잔여 만료시간)
- `isBlacklisted()`: 블랙리스트 확인
- `JwtAuthenticationFilter`에서 매 요청마다 블랙리스트 체크
- `logout()`에서 access token도 블랙리스트 등록

**테스트**: +3개 (블랙리스트 등록, 확인-있음, 확인-없음)

---

## Major (설계 개선, 프로덕션 전 수정)

### M1. ddl-auto: update 프로덕션 사용 금지

**파일**: application.yml:16, application-docker.yml:14

**쉬운 설명**: Hibernate가 프로덕션에서 마음대로 테이블을 바꾸고 있었어요. 개발자가 `name` 필드를 `nickname`으로 바꾸면 기존 `name` 컬럼은 그대로 두고 `nickname`을 추가해서 기존 데이터가 null이 돼요. 롤백도 불가능.

**수정 내용**:
- application-docker.yml: `ddl-auto: validate` (검증만, 수정 안 함)
- Flyway 도입: `V1__init.sql`로 버전 관리된 마이그레이션
- 로컬/테스트: Flyway 비활성화, `update` 유지

---

### M2. 비밀번호 복잡성 검증 부재

**파일**: SignUpRequest.java:22

**쉬운 설명**: `@Size(min=8)`만 있어서 "aaaaaaaa"가 비밀번호로 통과됐어요. C4의 Rate Limiting 부재와 합쳐지면 몇 초면 뚫리는 조합이었어요.

**수정 내용**:
- `@Pattern` 정규식 추가: 대문자 1 + 소문자 1 + 숫자 1 + 특수문자 1 필수
- 기존 테스트의 비밀번호를 정책에 맞게 수정 (`password123` → `Password1!`)

**테스트**: +4개 (소문자만, 숫자만, 특수문자 없음, 강한 비밀번호)

---

### M3. CORS 설정 하드코딩 + 이중 구성

**파일**: CorsConfig.java:18-44

**쉬운 설명**: CORS 설정이 MVC 레벨과 Security 레벨 두 곳에 있어서 어떤 게 적용되는지 알 수 없었어요. origin도 코드에 박혀있어서 환경 바뀔 때마다 코드 수정 + 재배포해야 했어요.

**수정 내용**:
- `addCorsMappings()` 제거, `CorsConfigurationSource` Bean만 유지
- `SecurityConfig`에 `.cors(cors -> cors.configurationSource(...))` 명시
- origin을 `application.yml`의 `${CORS_ALLOWED_ORIGINS}` 환경변수로 외부화

---

### M4. JwtAuthenticationFilter에서 JWT 에러를 삼킴

**파일**: JwtAuthenticationFilter.java:38-48

**쉬운 설명**: 토큰이 만료되면 Spring Security 기본 에러 페이지가 나왔어요. 프론트엔드가 `ApiResponse` JSON만 파싱하도록 되어있으면 "알 수 없는 에러"가 표시돼요.

**수정 내용**:
- `CustomAuthenticationEntryPoint` 생성: 401을 `ApiResponse` JSON으로 통일
- `SecurityConfig`에 `.exceptionHandling(ex -> ex.authenticationEntryPoint(...))` 등록

---

### M5. Actuator 엔드포인트 과다 노출

**파일**: SecurityConfig.java:39, application.yml:36-41

**쉬운 설명**: `/actuator/**` 전체가 인증 없이 열려있어서 DB 버전, Redis 호스트/포트 같은 내부 인프라 정보가 누구에게나 보였어요.

**수정 내용**:
- `show-details`: 로컬 `when_authorized`, 프로덕션 `never`
- SecurityConfig: `/actuator/health`만 `permitAll`, 나머지 `authenticated`

---

### M6. 보안 헤더 미설정

**파일**: SecurityConfig.java 전반

**쉬운 설명**: HSTS(HTTPS 강제)와 CSP(콘텐츠 보안 정책)가 없어서 중간자 공격이나 XSS에 취약할 수 있었어요. CSRF 비활성화도 주석 없이 되어있어서 "실수인지 의도인지" 알 수 없었어요.

**수정 내용**:
- HSTS: 1년 + `includeSubDomains`
- CSP: `default-src 'self'`
- CSRF disable에 주석: "JWT 기반 stateless 아키텍처이므로 CSRF 비활성화"

---

### M7. 테스트 커버리지 보강

**파일**: AuthControllerTest, AuthServiceTest, JwtTokenProviderTest

**쉬운 설명**: Happy path(성공 케이스)만 테스트하고 실패/에러 케이스가 없었어요. "만료된 토큰으로 접근하면?" "비활성화 계정으로 로그인하면?" 같은 edge case가 전부 미테스트.

**수정 내용**:
- 토큰 갱신 실패 (만료/불일치 refresh token): +2
- `/me` 내 정보 조회 성공/실패: +2
- 비활성화 계정 로그인: +1
- refresh 실패 (토큰 없음, 사용자 없음): +2
- 만료된 access token 검증: +1
- MockMvc + `@AuthenticationPrincipal` 호환성 해결

**테스트**: +12개 (총 38→56)

---

## Minor (코드 품질, 운영 편의)

### m1. Health Check가 의존성 상태를 미반영

**파일**: HealthController.java:12-19

**쉬운 설명**: `/health` 치면 DB가 죽어있어도 "healthy"라고 답했어요. 로드밸런서가 이걸 보고 "이 서버 괜찮다"고 판단해서 죽은 서버로 트래픽을 보내요.

**수정 내용**:
- DB ping + Redis ping 실행
- 전부 OK → "healthy" (200)
- 하나라도 실패 → "degraded" (503) + 개별 상태 표시
- `checks` 딕셔너리 + `timestamp` 포함
- 버전: `app.version` 설정으로 외부화

**테스트**: +3개 (전부 UP, DB DOWN, Redis DOWN)

---

### m2. 구조화된 로깅 미적용

**파일**: AuthService.java:45,73,103,114

**쉬운 설명**: `log.info("User logged in: kim@...")`처럼 평문이어서 ELK에서 "로그인 실패만 모아봐"가 안 됐어요. 해킹 시도가 있어도 어떤 IP에서 왔는지 추적이 불가능했어요.

**수정 내용**:
- `logstash-logback-encoder` 의존성 추가
- `logback-spring.xml`: 로컬(평문+MDC), docker(JSON) 프로파일 분리
- `MdcLoggingFilter`: 모든 요청에 `requestId`(UUID), `clientIp`, 요청 duration 기록
- 응답에 `X-Request-ID` 헤더 포함 (프론트엔드 디버깅용)
- AuthService: 로그인 성공/실패에 구조화된 이벤트 로그

**테스트**: +3개 (MDC 설정, requestId UUID 형식, X-Forwarded-For IP 추출)

---

### m3. @EnableJpaAuditing 위치

**파일**: AuthServiceApplication.java:10

**쉬운 설명**: `@EnableJpaAuditing`이 메인 클래스에 있으면 `@DataJpaTest` 같은 슬라이스 테스트에서 "Auditing 빈이 없다"고 터질 수 있어요. 5분짜리 수정이지만 테스트 안정성에 중요해요.

**수정 내용**:
- `JpaAuditingConfig.java` 별도 `@Configuration` 생성
- `AuthServiceApplication`에서 `@EnableJpaAuditing` 제거

---

### m4. Dockerfile에 JVM 메모리 옵션 누락

**파일**: Dockerfile:45

**쉬운 설명**: Docker 컨테이너에 메모리 512MB 제한 걸어놨는데 JVM이 그걸 무시하고 2GB 쓰려다가 OS가 프로세스를 강제로 죽여요 (OOM Killer). 서비스가 갑자기 사라지는데 에러 로그도 없어요.

**수정 내용**:
- `ENTRYPOINT`에 `-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0` 추가
- 컨테이너 메모리의 75%만 힙으로 사용

---

### m5. Spring Boot 버전

**파일**: build.gradle:3

**쉬운 설명**: 3.2.2(2024-01)는 이후 보안 패치가 10개 이상 나왔어요. 면접에서 "왜 최신 패치 안 적용했어요?" 물어보면 할 말이 없어지거든요.

**수정 내용**:
- 3.2.2 → 3.2.12 (3.2.x 최종 공식 패치)
- 전체 테스트 통과 확인

---

### m6. @Component + @ConfigurationProperties 중복

**파일**: JwtProperties.java:8-9

**쉬운 설명**: `@ConfigurationPropertiesScan`이 이미 빈을 등록하는데 `@Component`도 붙어있어서 "이거 왜 두 번 등록해요?" 코드 리뷰에서 지적받을 수 있어요. 동작은 같지만 Spring 관례에 어긋나요.

**수정 내용**:
- `JwtProperties.java`에서 `@Component` 제거

---

## 수정된 파일 목록

### 신규 생성
- `RateLimitInterceptor.java` — Redis 기반 rate limiting
- `WebConfig.java` — 인터셉터 등록
- `CustomAuthenticationEntryPoint.java` — 401 응답 통일
- `JpaAuditingConfig.java` — JPA Auditing 분리
- `MdcLoggingFilter.java` — 구조화 로깅 (requestId, clientIp)
- `logback-spring.xml` — 로그 포맷 (로컬: 평문, docker: JSON)
- `V1__init.sql` — Flyway 마이그레이션
- `.env.example` — 환경변수 가이드

### 수정
- `application.yml` — 시크릿 제거, 환경변수화, Flyway, CORS, Actuator
- `application-docker.yml` — 시크릿 fallback 제거, ddl-auto: validate
- `SecurityConfig.java` — CORS 명시, Actuator 제한, 보안 헤더, EntryPoint
- `CorsConfig.java` — 이중 구성 제거, origin 외부화
- `AuthController.java` — resolveToken() 안전 파싱
- `AuthService.java` — logout 시그니처 변경, 구조화 로그
- `JwtTokenProvider.java` — jti, 블랙리스트, reuse detection
- `JwtAuthenticationFilter.java` — 블랙리스트 체크
- `JwtProperties.java` — validate(), @Component 제거
- `SignUpRequest.java` — @Pattern 비밀번호 복잡성
- `GlobalExceptionHandler.java` — MissingRequestHeaderException 핸들러
- `HealthController.java` — DB/Redis ping, degraded 상태
- `AuthServiceApplication.java` — @EnableJpaAuditing 제거
- `Dockerfile` — JVM 메모리 옵션
- `build.gradle` — Spring Boot 3.2.12, Flyway, logstash-encoder
- `.gitignore` — .env 추가

### 테스트 (신규/수정)
- `JwtPropertiesTest.java` — 시크릿 검증 5개
- `AuthControllerTest.java` — Logout 4개, 비밀번호 4개, /me 2개, refresh 실패 2개
- `AuthServiceTest.java` — 비활성화 계정, refresh 실패 3개
- `JwtTokenProviderTest.java` — Reuse Detection 2개, Blacklist 3개, 만료 토큰 1개
- `RateLimitInterceptorTest.java` — Rate Limiting 6개
- `HealthControllerTest.java` — Health Check 3개
- `MdcLoggingFilterTest.java` — MDC 3개
