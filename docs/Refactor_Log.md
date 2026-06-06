# Refactor Log

> 6원칙(`docs/6_Principle.md`) 기반 리팩터 추적. 한 행 = 한 카드 = 한 결정. before/after와 "왜"를 비용·장애 언어로 남긴다.

| 카드 | 원칙 | 위치 | before | after | 사유 |
|---|---|---|---|---|---|
| C | ①SSoT / ③일관성 | `auth-service` `JwtTokenProvider.java`(서명 2곳) + `JwtProperties.java` | 키 길이로 서명 알고리즘 **암묵 결정**(`.signWith(secretKey)` → 32B=HS256·48B=HS384·64B=HS512), 최소 길이 32 | `.signWith(secretKey, Jwts.SIG.HS512)` **명시** + `MINIMUM_SECRET_LENGTH` 64로 강제 | 시크릿이 32~63B면 Java=HS256/384 / Python=HS512로 어긋나 **전 서비스 인증 붕괴**. 알고리즘을 명시·강제해 미래 misconfiguration의 silent 다운그레이드 차단. Python 양 서비스는 이미 `algorithms=["HS512"]`(무변경). |
| D | ② SRP | `portfolio-service` `routers/optimize.py` `optimize_portfolio()` + 신규 `mappers/optimization_mapper.py` | 라우터 한 함수가 조회+검증+메트릭+계산+**직렬화(응답 매핑)**+로깅을 다 함(변경 이유 5+) | 응답 매핑 3개(metrics 연율화 / diagnostics 중첩 / frontier 모양)를 mapper 순수함수로 분리. 조회·계산은 기존 `services/` 그대로 호출(라우터=오케스트레이션) | 변경 이유 분리 — 응답 스키마/연율화/frontier 모양 변경이 라우터를 안 건드림. 동작 불변(테스트 227→227 green). |

## 제외 (과적용 경계 — `docs/6_Principle.md` §0.3)

- **E. JWT secret 3중복(auth·portfolio·llm) "통일"은 제외.** 세 서비스는 `docker-compose.yml`이 동일 `${JWT_SECRET}`를 주입하므로 **`.env`가 이미 SSoT**다. 값이 코드에 박혀 분기된 게 아니라 단일 출처에서 참조될 뿐이라 중복이 아니다. 별도 통일 레이어를 만드는 건 SSoT 과적용 → 제외.
- **weights_dict(4줄)·period 문자열·최종 `OptimizeResponse` 조립은 라우터에 유지.** 단순 필드 결합은 오케스트레이션이며 SRP는 줄 수가 아니라 변경 이유 개수다(§2②). 5줄 함수까지 더 쪼개지 않는다.
- **조회·계산 로직(`services/data.py`·`services/optimizer.py`)은 이미 분리됨 → 건드리지 않음(중복 분리 금지).**
- mapper의 연율화는 기존 인라인 `*252`/`*√252` 수식을 그대로 옮김(`covariance.annualize`로 갈아끼우지 않음 — behavior drift 방지).

## 메모 — 프롬프트 전제 정정 (C 작업 중 실측)

- 작업 지시는 "현재 시크릿 48B / 인증 붕괴 / `InsecureKeyLengthWarning(48 bytes)`"를 전제했으나 실제 repo는 달랐다: 실 `.env` `JWT_SECRET`은 **64B**, 그런 경고 코드는 **부재**, 64B라 **이미 HS512로 정상 동작 중**이었다. 따라서 C는 break-fix가 아니라 **계약을 명시·강제하는 hardening**이다. 로컬 `.env`는 무교체(이미 ≥64B), 커밋 대상 `.env.example` 2개만 64자+ 예시로 강화.
- **교차 검증 한계(B와 동일 정직성):** 단위 테스트는 JVM↔Python 두 런타임을 실제로 가로지르지 못한다. "Java=HS512 발급"(`JwtTokenProviderTest.AlgorithmContract`: 토큰 헤더 `alg==HS512` 단언) + "Python=HS512 검증"(각 서비스 `test_auth_middleware.py`의 HS512 fixture/검증)을 **각 런타임에서 증명**해 계약 일치를 입증한다.
