# ADR-008: Docker Compose 아키텍처

## 상태: Accepted

---

## 맥락 (Context)

Aether는 6개의 컴포넌트로 구성된 마이크로서비스 아키텍처다:
- **인프라**: PostgreSQL, Redis
- **백엔드**: auth-service (Java/Spring Boot), portfolio-service (Python/FastAPI), llm-service (Python/FastAPI)
- **프론트엔드**: Next.js 16

개발자가 로컬에서 전체 시스템을 실행하고, 서비스 간 통합을 테스트할 수 있는 환경이 필요했다.

**요구사항**:
- 한 명령으로 전체 시스템 기동
- 서비스 간 네트워크 자동 구성 (hostname 기반 통신)
- 의존성 순서 보장 (DB → auth → frontend)
- Health check로 서비스 준비 상태 확인
- 로컬 환경과 포트 충돌 최소화

---

## 고려한 선택지

### 옵션 A: 로컬 직접 실행 (각 서비스 터미널)

```bash
# 터미널 1: PostgreSQL
brew services start postgresql

# 터미널 2: Redis
redis-server

# 터미널 3: auth-service
cd auth-service && ./gradlew bootRun

# 터미널 4: portfolio-service
cd portfolio-service && uvicorn app.main:app --port 8001

# 터미널 5: llm-service
cd llm-service && uvicorn app.main:app --port 8002

# 터미널 6: frontend
cd frontend && npm run dev
```

- **장점**: 디버깅 용이 (각 서비스에 breakpoint 설정), 빌드 시간 없음
- **단점**: 터미널 6개 관리, 환경변수 수동 설정, Python/Java/Node.js 버전 충돌, 새 팀원 온보딩 시 "내 PC에서는 되는데" 문제

### 옵션 B: Docker Compose

- **장점**: `docker compose up` 한 명령으로 전체 기동, 네트워크 자동 구성 (컨테이너명 = hostname), `depends_on` + `healthcheck`로 의존성 순서 보장, `.env`로 환경변수 중앙 관리, 환경 재현성 100%
- **단점**: 빌드 시간 (초기 ~5분), 코드 변경 시 리빌드 필요, 디버깅이 로컬 직접 실행보다 불편

### 옵션 C: Kubernetes (minikube/kind)

- **장점**: 프로덕션 환경과 동일한 오케스트레이션, 서비스 디스커버리, 로드밸런싱, 롤링 업데이트
- **단점**: 학습 곡선 높음, YAML 매니페스트 작성 (Deployment, Service, ConfigMap, Secret 등), minikube 리소스 소비 (메모리 4GB+), 로컬 개발에는 과도한 복잡도

---

## 결정 (Decision)

**옵션 B: Docker Compose** 선택.

```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports: ["5433:5432"]          # 로컬 충돌 방지
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aether"]

  redis:
    image: redis:7-alpine
    ports: ["6380:6379"]          # 로컬 충돌 방지
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  auth-service:
    build: ./auth-service
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/${POSTGRES_DB}
      - SPRING_DATA_REDIS_HOST=redis

  portfolio-service:
    build: ./portfolio-service
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')"]

  llm-service:
    build: ./llm-service
    depends_on:
      portfolio-service: { condition: service_healthy }
    environment:
      - PORTFOLIO_SERVICE_URL=http://portfolio-service:8001  # 컨테이너 hostname

  frontend:
    build: ./frontend
    depends_on:
      auth-service: { condition: service_healthy }
      portfolio-service: { condition: service_healthy }
      llm-service: { condition: service_healthy }

networks:
  aether-network:
    driver: bridge
```

**선택 이유**:
- 4개 서비스 + 2개 인프라 = 6개 컴포넌트 → 로컬 직접 실행은 관리 불가
- `depends_on: condition: service_healthy`로 DB가 ready된 후에만 auth-service 시작
- 컨테이너 hostname으로 서비스 간 통신 → 코드에 `localhost` 하드코딩 불필요
- `.env` 파일 하나로 모든 서비스의 환경변수 관리
- Kubernetes는 현재 규모(6개 서비스)에서 오버엔지니어링

---

## 결과 (Consequences)

**장점**:
- 원커맨드 기동: `docker compose up -d` → 6개 컨테이너 순서대로 시작
- 환경 재현성: 팀원 누구나 동일한 환경에서 테스트 가능
- 통합 테스트: 서비스 간 실제 HTTP 통신 테스트 (curl로 E2E 검증)
- 이슈 발견: 통합 테스트에서 8개 이슈 발견 (환경변수 불일치, 포트 충돌, 라이브러리 호환성, 미들웨어 충돌 등)

**트레이드오프**:
- 초기 빌드 시간: 4개 서비스 이미지 빌드 ~5분 (캐시 활용 시 ~30초)
- 디버깅: `docker logs`와 `docker exec`에 의존 → IDE 디버거 연결은 추가 설정 필요
- 리소스: 6개 컨테이너가 로컬 리소스 점유 (Docker Desktop 메모리 설정 필요)
- 코드 변경 시: 해당 서비스 리빌드 필요 (`docker compose build <service>`)

---

## 재선택한다면?

같은 선택. 단, 두 가지 개선을 추가:
1. **개발용 docker-compose.override.yml**: 소스 코드 볼륨 마운트 + hot reload → 리빌드 없이 코드 반영
2. **프로덕션 전환 시 Kubernetes**: 현재 Docker Compose 구조가 K8s 매니페스트로 변환하기 쉬운 형태 (서비스별 Dockerfile + 환경변수 분리가 이미 완료)

Docker Compose는 "로컬 개발/테스트용"이라는 명확한 경계를 유지하고, 프로덕션 배포는 별도의 오케스트레이션 도구를 사용하는 것이 적절하다.
