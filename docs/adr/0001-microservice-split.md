# ADR 0001 — Microservice Split: 4 Services + 2 Infra

- **상태**: Accepted
- **일자**: 2026-04-28
- **관련 작업**: H-1 (AGENTS.md / CLAUDE.md / ADR 3건 동시 작성)

---

## 컨텍스트

Aether는 포트폴리오 분석 + LLM 기반 RAG/도메인 분석 + 인증을 하나의 사용자 경험으로 제공한다. 책임이 명확히 다른 3종의 워크로드가 한 프로세스에 묶이면:

- 인증(JWT 검증, Redis 세션)의 가용성 요구가 LLM 호출 지연(60s timeout)과 동일 프로세스에 결합된다.
- 수치 계산(scipy/cvxpy)의 메모리 풋프린트와 LLM/embedding의 의존성(google-generativeai, chromadb)이 같은 빌드 단위에 들어간다.
- Java/Python 양 언어의 강점(Spring Security ↔ FastAPI + LLM 생태계)을 동시에 쓰기 어렵다.

또한 **호출 체인은 단방향**이며, 인증과 LLM은 직접 통합되지 않는다. frontend가 auth-service에서 JWT를 받아 portfolio/llm 호출 시 헤더에 동봉하는 방식이다 (`docs/agent-capability-audit/01_architecture.md:§1` 라인 8). 이 사실은 본 분할의 전제다 — auth가 다른 서비스의 동기 dependency가 되지 않으므로 4개 서비스를 독립 배포 가능 단위로 둘 수 있다.

---

## 결정

다음과 같이 4개 서비스 + 2개 인프라로 분할한다:

| 서비스 | 포트 | 스택 | 책임 |
|---|---|---|---|
| frontend | 3000 | Next.js 15 + React 19 | UI, JWT 보관, 백엔드 3종 호출 |
| auth-service | 8003 | Spring Boot + Java 17 | JWT 발급/검증, 리프레시, 블랙리스트 |
| portfolio-service | 8001 | FastAPI + Python 3.11 | 최적화·리스크·백테스트 수치 계산 |
| llm-service | 8002 | FastAPI + Python 3.11 | RAG, 도메인 LLM 분석 |
| postgres | 5433→5432 | postgres:16-alpine | auth-service 전용 (users) |
| redis | 6380→6379 | redis:7-alpine | auth-service 전용 (refresh/blacklist) |

근거: `docker-compose.yml:6-160`, `frontend/src/lib/utils/constants.ts:2-6` (3개 base URL).

서비스 간 통합:

- **llm-service → portfolio-service**: HTTP/JSON, httpx.AsyncClient, timeout 60s (`portfolio_client.py:33-39`).
- **frontend → 3 백엔드**: HTTP/JSON, Axios.
- **gRPC / 메시지 큐 / 이벤트 버스 — 미사용** (분석 범위 0건, 01:§2). 모든 서비스 간 호출은 동기 HTTP.

---

## 결과

**얻는 것**:

- 인증과 LLM이 격리되어 LLM 외부 호출 지연이 인증 가용성에 영향을 주지 않는다.
- Spring Security + Spring Data Redis의 성숙한 인증 스택과 FastAPI + LLM 생태계를 동시 활용.
- docker-compose `depends_on` + `condition: service_healthy`로 부팅 의존성 명시 (`docker-compose.yml:83-85, 114-118, 146-152`).

**감수하는 것**:

- 4개 서비스의 운영 부담 (각 서비스마다 Dockerfile, healthcheck, 빌드 캐시).
- 서비스 간 호출이 모두 HTTP — 비동기 메시징/이벤트 스트림으로 전환하려면 별도 ADR.
- 서비스 디스커버리는 docker-compose hostname (`portfolio-service:8001`). DNS-SD/Consul 부재.
- Kubernetes/Helm 자산 미보유. 배포는 SSH + `docker compose up -d` (`Jenkinsfile:147-169`).

---

## 영향

- 본 분할은 향후 모든 새 기능의 기본 가정. 새 서비스 추가는 별도 ADR로 정당화한다.
- 서비스 간 호출은 동기 HTTP가 디폴트. 비동기로 전환하려는 카드는 본 ADR 갱신을 동반한다.
- llm-service ↔ auth-service 통합 (LLM 엔드포인트 JWT 검증) 도입 시 본 ADR §결과의 "감수하는 것"을 재검토. 현재는 H-10 카드 범위.
