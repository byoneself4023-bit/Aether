# ADR 0027 — DBG-2 이메일 형식 검증 강화 (@Email + @Pattern)

- **상태**: Accepted
- **일자**: 2026-05-10
- **관련 카드**: DBG-2 (이메일 형식 검증 강화 / TG-2c + TG-2d Edge-1 발견 영역 정착)
- **결정 근거**: TEST_REPORT.md (TG-2c §2.1 Edge-1 / TG-2d §2.1 Edge-1) + AUDIT_REPORT.md §1 (Critical 3) + ADR 0026 (DBG-1 본질 시그널 일관성)

---

## 컨텍스트

TG-2c (PR #44 / 98839b8) Edge-1 + TG-2d (PR #45 / 0b2be3f) Edge-1 영역 발견 — Spring `@Email` annotation 영역 = `@` 문자 영역 영역 검증 / TLD 검증 X. 결과:

- TG-2c 영역 `foo@bar` 영역 정상 signup (id=17)
- TG-2d 영역 `foo<ts>@bar` 영역 정상 signup (id=19) — 본 시점 영역 회귀 검증

데이터 무결성 위반 = 시연 + 면접 시점 시그널 약화. AUDIT-1 (PR #48) 영역 Critical 3 분류 정착.

본질 — Spring `@Email` 영역 영역 RFC 5322 영역 영역 영역 영역 X (영역 영역 broad pattern). TLD ≥ 2자 영역 영역 정규식 추가 의무.

---

## 결정 (양면 정책 / 5 분기 추적)

### 분기 1: 옵션 A (@Email + @Pattern 이중) vs 옵션 A2 (Commons Validator) — **A 채택**

**옵션 A (선택)** = `@Email` + `@Pattern` (RFC 5322 영역 정규식 / TLD ≥ 2자 / Spring 내장 의존성만 영역) — 의존성 영역 X / 본 카드 영역 영역.

**옵션 A2 (대안)** = `commons-validator:1.8.0` 통합 (RFC 822 / 5322 영역 검증) — 외부 라이브러리 영역 / Gradle 영역 영역 / 영역 영역 시점 검토.

근거: 옵션 A 영역 = Spring 내장 영역 + 의존성 X / 영역 영역 영역 정규식 영역 영역 영역. 옵션 A2 영역 = false negative ↓ / 단 외부 의존성 영역 영역 (시나리오 A 영역 영역 영역 영역 X).

### 분기 2: 정규식 영역 — `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$` — **선택**

근거:

- local-part: `[a-zA-Z0-9._%+-]+` — 영역 영역 영역 영역 / `+` `_` `.` `%` `-` 영역 영역
- `@` 의무
- domain: `[a-zA-Z0-9.-]+` — 영역 영역 영역 영역 (`.co.kr` 등 다단 TLD 영역)
- `\\.[a-zA-Z]{2,}$` — TLD ≥ 2자 의무 (영역 영역 시그널 / `foo@bar` / `foo@bar.c` 차단)

### 분기 3: 옵션 B (이메일 인증 / verify token + SMTP) — **보류 (시나리오 B 트리거)**

근거: 실사용자 진입 시점 의무 / SMTP 인프라 + 토큰 관리 + 만료 정책 의무. 본 시점 = 시나리오 A (사용자 0명) → 보류. 시나리오 B 진입 (사용자 5+ 인터뷰 + PMF 10불) 시점 트리거 명시.

### 분기 4: 기존 user 처리 — **보존 (마이그레이션 X)**

근거:

- 기존 user (`foo@bar` id=17 / `foo<ts>@bar` id=19) 영역 = 시나리오 A 영역 영역 시연 데이터 (사용자 0명 / 운영 영역 영역 X)
- 마이그레이션 영역 = 운영 비용 ↑ / 시그널 X
- 시나리오 B 진입 시점 영역 영역 영역 (이메일 재인증 영역 영역 영역 영역) 의무 — 본 시점 보류

### 분기 5: 기존 정상 이메일 회귀 검증 — **테스트 추가 (PlusTagEmail / MultiLevelTld)** — **선택**

근거: 정규식 영역 false positive (정상 이메일 차단) 영역 영역 영역 영역 — 회귀 테스트 의무. `user+tag@example.com` (`+` 특수문자) + `user.name@example.co.kr` (다단 TLD `.co.kr`) 영역 영역 통과 의무.

---

## 영향

### 갱신

- `auth-service/src/main/java/com/aether/auth/domain/user/dto/SignUpRequest.java` (line 18-26 영역):
  - `@Pattern` 추가 — `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$`
  - 메시지: "올바른 이메일 형식이 아닙니다 (도메인 + TLD 의무)"
- `auth-service/src/test/java/com/aether/auth/api/AuthControllerTest.java` 영역 7 테스트 추가:
  - `signUp_NoTLD_Fail` (`foo@bar` → C002)
  - `signUp_NoAtSign_Fail` (`notanemail` → C002)
  - `signUp_NoDomain_Fail` (`foo@` → C002)
  - `signUp_TldTooShort_Fail` (`foo@bar.c` → C002 / TLD ≥ 2자)
  - `signUp_FooTsAtBar_Fail` (`foo1778310495@bar` → C002 / TG-2d Edge-1 회귀)
  - `signUp_PlusTagEmail_Success` (`user+tag@example.com` → 201 / 회귀 검증)
  - `signUp_MultiLevelTld_Success` (`user.name@example.co.kr` → 201 / 회귀 검증)

### 회귀

- auth-service `./gradlew test` 영역 영역 영역 영역 — **BUILD SUCCESSFUL** (DBG-2 7건 통과 + 기존 회귀 0).
- portfolio-service / llm-service / frontend = 영향 X (코드 변경 0).

### 운영

- 신규 signup 영역 정규식 검증 영역 — `foo@bar` / `notanemail` / `foo@` / `foo@bar.c` 영역 → C002 응답 (이전 = 정상 signup 가능).
- 기존 user (id=17 / id=19) 보존 — 영역 영역 영역 영역 영역 영역 / 영역 영역 영역 영역 X (시나리오 A 일관성).

---

## 결과

### 긍정적

- **데이터 무결성 ↑**: TG-2c / TG-2d Edge-1 영역 영역 영역 — `foo@bar` 영역 신규 signup 영역 차단.
- **면접 시그널 ↑**: DBG-2 분리 결정 (한 카드 1책임) + 정착 + 회귀 검증 (TG-2d Edge-1 영역 회귀 테스트 정착) — 영역 추적 영역 영역.
- **양면 정책 일관성**: 옵션 A 정착 / 옵션 A2 (Commons Validator) + 옵션 B (이메일 인증) 보류 영역 영역 트리거 영역 명시.
- **회귀 0**: 정상 이메일 (`+`/`.`/다단 TLD) 영역 영역 통과 검증.

### 부정적

- **정규식 false negative 영역**: RFC 5322 100% 영역 영역 영역 영역 영역 영역 X — 영역 한글 도메인 / 신규 TLD (`.app` / `.dev`) / 영역 비문자 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역. 시나리오 B 진입 시점 영역 옵션 A2 (Commons Validator) 영역 영역 영역 영역.
- **기존 user 영역 영역**: 마이그레이션 X / 영역 영역 영역 영역 영역 영역 영역 영역 영역 영역.

### 트리거 (옵션 A2 / 옵션 B 진입 시점)

- 옵션 A2 (Commons Validator): false negative 영역 영역 (사용자 영역 영역) 시점 트리거.
- 옵션 B (이메일 인증 + SMTP): 시나리오 B 진입 (사용자 5+ + PMF 10불) 시점 트리거.
- 본 시점 = 영구 보류 / ADR 영역 영역.

---

## 인용 자료

- TEST_REPORT.md TG-2c §2.1 Edge-1 + TG-2d §2.1 Edge-1
- AUDIT_REPORT.md §1 / §3.1 — Critical 3 (DBG-2)
- ADR 0026 — DBG-1 본질 시그널 일관성 (transient vs 영구)
- PRINCIPLES.md 패턴 6 (미적용 결정 = 시그널)
- 양면 정책 일관성 — ADR 0012 / 0019 / 0026

---

## 카드 누적 영역

- ADR 0011-0027 = **양면 정책 17 ADR** (정착 9 / 보류 4 / 메타 4 / 정리 1 — DBG-2 영역 정착 1 영역).
