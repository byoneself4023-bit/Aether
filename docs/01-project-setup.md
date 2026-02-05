# Claro 프로젝트 설정 가이드

> Spring Boot 마이크로서비스 학습 프로젝트

---

## 1. 기술 선택 이유

### 빌드 도구: Gradle

| 비교 | Gradle | Maven |
|------|--------|-------|
| 빌드 속도 | 2~10배 빠름 (증분 빌드, 캐싱) | 느림 |
| 문법 | Groovy DSL (간결) | XML (장황) |
| 유연성 | 높음 | 낮음 |

```groovy
// Gradle - 한 줄
implementation 'io.jsonwebtoken:jjwt-api:0.12.5'
```

```xml
<!-- Maven - 5줄 -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.5</version>
</dependency>
```

---

### 언어: Java

| 선택지 | 장점 | 단점 |
|--------|------|------|
| **Java** | Spring 표준, 레퍼런스 최다, 취업 시장 | 보일러플레이트 |
| Kotlin | 간결한 문법, Null Safety | 학습 곡선 추가 |

> 처음 Spring 배울 때는 Java로 기본기 → 나중에 Kotlin 전환 고려

---

### Spring Boot 버전: 4.0.x (LTS)

| 버전 표기 | 의미 |
|-----------|------|
| 4.0.2 (녹색) | 정식 릴리즈, 프로덕션 OK |
| SNAPSHOT | 개발 중, 불안정 |
| M1, RC | 베타/릴리즈 후보 |

> **원칙**: 항상 녹색 원(stable) + LTS 버전 선택

---

### Java 버전: 21 (LTS)

| 버전 | 지원 기간 | 선택 이유 |
|------|----------|----------|
| **21** | 2031년까지 | 현재 LTS, 가상 스레드 등 신기능 |
| 17 | 2029년까지 | 이전 LTS, 여전히 많이 사용 |
| 25 | 단기 지원 | LTS 아님, 실무 부적합 |

---

### 패키징: Jar vs War

| Jar | War |
|-----|-----|
| 내장 Tomcat 포함 | 외부 WAS 필요 |
| `java -jar app.jar` 실행 | Tomcat 별도 설치 |
| **현대적 방식** | 레거시 방식 |

---

## 2. Dependencies 선택 이유

| 의존성 | 역할 | 사용 예 |
|--------|------|---------|
| **Spring Web** | REST API | `@RestController`, `@GetMapping` |
| **Spring Security** | 인증/인가 | JWT 필터, 권한 체크 |
| **Spring Data JPA** | DB ORM | `UserRepository extends JpaRepository` |
| **Spring Data Redis** | 캐시/세션 | Refresh Token 저장 |
| **PostgreSQL Driver** | DB 연결 | JDBC 드라이버 |
| **Validation** | 입력 검증 | `@Valid`, `@Email`, `@NotBlank` |
| **Lombok** | 보일러플레이트 제거 | `@Getter`, `@RequiredArgsConstructor` |

---

## 3. 패키지 네이밍 컨벤션

```
com.claro.auth          ← Group + Artifact
    ├── global/         ← 공통 설정, 예외, 유틸
    ├── domain/         ← 엔티티, 레포지토리
    ├── application/    ← 비즈니스 로직 (Service)
    └── api/            ← 컨트롤러 (진입점)
```

| 패턴 | 설명 |
|------|------|
| `com.회사명.서비스명` | 역방향 도메인 (Java 표준) |
| 레이어드 아키텍처 | Controller → Service → Repository |

---

## 4. 탑 티어 개발자 원칙

| 원칙 | 적용 |
|------|------|
| **Why First** | 모든 기술 선택에 이유가 있어야 함 |
| **Trade-off** | 완벽한 정답 없음, 상황에 맞는 최선 |
| **YAGNI** | 지금 필요한 것만 구현 |
| **KISS** | 단순하게 유지 |

> *"6개월 후 새벽 3시에 장애 대응할 때도 이해할 수 있는 코드"*

---

## 5. Spring Initializr 설정 요약

| 항목 | 값 | 이유 |
|------|-----|------|
| Project | Gradle - Groovy | 빌드 속도, 간결함 |
| Language | Java | 표준, 레퍼런스 |
| Spring Boot | 4.0.x | Stable LTS |
| Group | com.claro | 역방향 도메인 |
| Artifact | auth-service | 서비스 이름 |
| Packaging | Jar | 내장 Tomcat |
| Java | 21 | LTS |

---

## 참고 자료

- [Spring Initializr](https://start.spring.io)
- [Spring Boot Reference](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Gradle User Guide](https://docs.gradle.org/current/userguide/userguide.html)
