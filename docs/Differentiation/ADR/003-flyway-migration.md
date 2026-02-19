# ADR-003: Flyway DB 마이그레이션

## 상태: Accepted

---

## 맥락 (Context)

auth-service에서 `spring.jpa.hibernate.ddl-auto: update`를 프로덕션 환경에서도 사용하고 있었다. Hibernate가 엔티티 변경을 감지해 자동으로 DDL을 실행하는데, 이 방식은 위험하다:
- 필드명 변경 시 기존 컬럼을 삭제하지 않고 새 컬럼 추가 → 기존 데이터 null
- 인덱스 삭제가 자동으로 안 됨
- 롤백 불가능 — 어떤 DDL이 실행됐는지 기록이 없음

**요구사항**:
- 스키마 변경 이력 추적 (누가, 언제, 무엇을)
- 롤백 가능한 마이그레이션
- CI/CD 파이프라인에서 자동 실행
- 환경별(로컬/도커/프로덕션) 독립적 적용

---

## 고려한 선택지

### 옵션 A: Flyway

- **장점**: SQL 기반 → DBA 친화적, Spring Boot 자동 통합 (`spring.flyway.enabled`), 학습 곡선 낮음, 버전 넘버링이 직관적 (`V1__init.sql`, `V2__add_index.sql`)
- **단점**: 롤백은 유료 버전(Teams)에서만 지원, XML/YAML 형식 미지원

### 옵션 B: Liquibase

- **장점**: XML/YAML/JSON/SQL 모두 지원, 무료 롤백 지원, 세밀한 변경 추적 (changeset 단위)
- **단점**: XML 설정이 복잡, Spring Boot 통합은 되지만 Flyway보다 설정이 많음, 프로젝트 규모 대비 과도

### 옵션 C: 수동 SQL 관리

- **장점**: 도구 의존성 없음
- **단점**: 버전 추적 없음, 환경별 적용 상태 파악 불가, 실수로 같은 SQL 두 번 실행 가능, CI/CD 자동화 어려움

---

## 결정 (Decision)

**옵션 A: Flyway** 선택.

```
db/migration/
  V1__init.sql          ← 초기 스키마 (users 테이블)
```

```yaml
# application.yml
spring:
  jpa:
    hibernate:
      ddl-auto: validate    # 프로덕션: 검증만, 수정 안 함
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
```

```yaml
# application.yml (로컬/테스트)
spring:
  jpa:
    hibernate:
      ddl-auto: update      # 개발: Hibernate 자동 관리
  flyway:
    enabled: false           # 개발: Flyway 비활성화
```

**선택 이유**:
- auth-service의 스키마가 단순 (users 테이블 1개) → Liquibase의 세밀한 기능이 필요 없음
- SQL 파일로 마이그레이션 작성 → DBA나 다른 개발자가 즉시 이해 가능
- Spring Boot `spring.flyway.enabled`만 설정하면 앱 시작 시 자동 마이그레이션
- `ddl-auto: validate`로 엔티티와 실제 스키마 불일치 시 앱 시작 실패 → 안전장치

---

## 결과 (Consequences)

**장점**:
- 스키마 이력 추적: `flyway_schema_history` 테이블에 모든 마이그레이션 기록
- 환경 일관성: 모든 환경에서 동일한 SQL 순서로 적용
- CI/CD 통합: 앱 시작 시 자동 실행 → 별도 배포 스크립트 불필요
- 안전장치: `ddl-auto: validate`가 엔티티-스키마 불일치 감지

**트레이드오프**:
- 무료 버전은 롤백 미지원 → 롤백이 필요하면 역방향 마이그레이션 SQL을 수동 작성
- 로컬 개발에서 Flyway를 끄고 Hibernate `update`를 사용 → 로컬과 프로덕션 스키마가 미묘하게 다를 수 있음

---

## 재선택한다면?

같은 선택. 현재 스키마 규모(테이블 1개)에서 Liquibase는 과도하다. 스키마가 10개 이상으로 늘어나고 롤백이 빈번해지면 Liquibase로 전환을 검토할 수 있지만, Flyway의 단순함이 현재 프로젝트에 적합하다.
