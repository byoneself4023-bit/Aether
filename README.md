# Aether — AI 투자 포트폴리오 최적화 플랫폼

Markowitz 최적화 + LLM 해석 + 실시간 리스크 분석을 제공하는 풀스택 핀테크 플랫폼

> 코드 리뷰 64건 수정 | 테스트 511개 | 통합 테스트 10/10 | 장애 시뮬레이션 14건 | ADR 8개

---

## 📌 Status (2026-05-10)

**Aether 시나리오 A 본질 정착 완료** — 카드 33 마감 / 양면 정책 19 ADR / 면접 시연 4/5 정착.

본 repo = 시연 + 면접 자료 보존. 다음 = Houseman (별도 repo / Phase 7-12 / 사용자 직접 정착).

### 진입자 자료

- **시연 가이드**: [`docs/TEST_GUIDE_MANUAL.md`](docs/TEST_GUIDE_MANUAL.md) — 일상 + 면접 시점 분리
- **면접 답변 시뮬**: [`docs/INTERVIEW_SIMULATION.md`](docs/INTERVIEW_SIMULATION.md) — 4 직무
- **종합 회고**: [`docs/RETROSPECTIVE.md`](docs/RETROSPECTIVE.md) — 32 카드 흐름 + 학습 10건
- **Houseman 진입 본질**: [`docs/HOUSEMAN_APPLICATION.md`](docs/HOUSEMAN_APPLICATION.md)
- **종료 결정 추적**: [`docs/adr/0029-aether-end-decision.md`](docs/adr/0029-aether-end-decision.md)

---

## 아키텍처

```
                       ┌──────────────────┐
                       │  frontend :3000  │
                       │  Next.js 16      │
                       └────────┬─────────┘
                                │
             ┌──────────────────┼──────────────────┐
             ▼                  ▼                   ▼
   ┌──────────────┐  ┌─────────────────┐  ┌──────────────┐
   │ auth :8003   │  │portfolio :8001  │  │  llm :8002   │
   │ Spring Boot  │  │    FastAPI      │  │   FastAPI    │
   │   3.2.12     │  │                 │  │   Gemini     │
   └──────┬───────┘  └────────┬────────┘  └──────┬───────┘
          │                   │                   │
    ┌─────┴──────┐            │             ┌─────┴──────┐
    │ PostgreSQL │       yfinance API       │  ChromaDB  │
    │  16-alpine │                          │   (local)  │
    └─────┬──────┘                          └────────────┘
          │
    ┌─────┴──────┐
    │   Redis    │
    │  7-alpine  │
    └────────────┘
```

Docker Compose로 6개 컨테이너 통합 실행: `docker compose up -d`

---

## 기술 스택

| 레이어 | 기술 | 버전 |
|--------|------|------|
| 프론트엔드 | Next.js + React + TypeScript | 16.1.6 / 19.2.3 |
| 스타일링 | Tailwind CSS | v4 |
| 상태 관리 | Zustand | 5.0.11 |
| 차트 | Recharts | 3.7.0 |
| 인증 | Spring Boot + Spring Security + JWT | 3.2.12 |
| DB | PostgreSQL + Flyway | 16-alpine |
| 캐시/세션 | Redis | 7-alpine |
| 최적화 | scipy.optimize (SLSQP) + Ledoit-Wolf Shrinkage | scipy 1.11.4 |
| 리스크 | Parametric VaR + Monte Carlo + CVaR | numpy 1.26.2 |
| LLM | Google Gemini 2.5 Flash | google-generativeai 0.3.2 |
| RAG | ChromaDB + gemini-embedding-001 | chromadb 0.4.x |
| 컨테이너 | Docker Compose | v2 |

---

## 핵심 기능

### 1. 포트폴리오 최적화
- Markowitz Mean-Variance Optimization (SLSQP solver)
- Ledoit-Wolf Shrinkage 공분산 추정
- 공분산 행렬 검증 + 자동 정칙화 (Ridge Regularization)
- 효율적 프론티어 계산 (20 포인트)
- 부분 실패 허용 (4개 중 2개 실패해도 나머지로 최적화)

### 2. 리스크 분석
- Parametric VaR (정규분포 가정)
- Monte Carlo VaR (10,000회 시뮬레이션)
- CVaR / Expected Shortfall
- 보유 기간, 신뢰 수준 커스터마이징

### 3. 백테스트
- Walk-forward backtest (시간순 분리)
- 거래비용 0.1% 반영
- 성과 메트릭: Sharpe, MDD, 턴오버, 누적 수익률

### 4. AI 해석 (RAG)
- ChromaDB 벡터스토어 + gemini-embedding-001
- 한국어 금융 지식 기반 RAG
- 포트폴리오 결과 자연어 해석
- 프롬프트 인젝션 방어 + Hallucination 검증

### 5. 인증
- JWT (Access 30분 + Refresh 7일) + Redis 블랙리스트
- Refresh Token Reuse Detection (탈취 감지 → 전체 세션 무효화)
- Redis Rate Limiting (IP당 분당 10회)
- BCrypt + 비밀번호 복잡성 검증

---

## 빠른 시작

### 사전 요구사항
- Docker + Docker Compose
- `.env` 파일 (`.env.example` 복사 후 값 입력)

### 실행

```bash
cp .env.example .env
# .env에 GEMINI_API_KEY 등 실제 값 입력
docker compose up -d
```

### 서비스 접속

| 서비스 | URL | 설명 |
|--------|-----|------|
| Frontend | http://localhost:3000 | 대시보드 UI |
| Portfolio API | http://localhost:8001/docs | 최적화/리스크/백테스트 |
| LLM API | http://localhost:8002/docs | AI 해석/RAG 챗봇 |
| Auth API | http://localhost:8003/swagger-ui | 인증/회원관리 |

---

## 프로젝트 구조

```
Aether/
├── frontend/               # Next.js 16 (React 19, TypeScript, Tailwind v4)
├── auth-service/           # Spring Boot 3.2 (JWT + Redis + Flyway)
├── portfolio-service/      # FastAPI (Markowitz + Risk + Backtest)
├── llm-service/            # FastAPI (Gemini + RAG + ChromaDB)
├── docker-compose.yml      # 6개 컨테이너 오케스트레이션
├── .env.example            # 환경변수 템플릿
└── docs/
    ├── Phase/              # 구현 계획 (5개 Phase)
    ├── Review/             # 서비스별 코드 리뷰 결과 (64건)
    ├── Integration/        # Docker Compose 통합 테스트 (10/10)
    └── Differentiation/    # Before→After, ADR 8개, 장애 시뮬레이션
```

---

## 코드 품질

### 코드 리뷰 수정: 64건

| 서비스 | Critical | Major | Minor | 합계 |
|--------|:--------:|:-----:|:-----:|:----:|
| auth-service | 6 | 7 | 6 | 19 |
| portfolio-service | 4 | 4 | 3 | 11 |
| llm-service | 4 | 5 | 4 | 13 |
| frontend | 4 | 7 | 10 | 21 |
| **합계** | **18** | **23** | **23** | **64** |

### 테스트: 511개

| 서비스 | 테스트 수 | 주요 커버리지 |
|--------|:---------:|-------------|
| auth-service | 70 | 인증, JWT, Rate Limiting, Health Check, 장애 시뮬레이션 |
| portfolio-service | 209 | 최적화, 리스크, 백테스트, 드리프트 탐지, 수치 안정성, 장애 시뮬레이션 |
| llm-service | 232 | LLM 호출, RAG, 프롬프트 인젝션 방어, 캐시, Rate Limiting, 토큰 추적 |

### 통합 테스트: 10/10 시나리오 통과

8개 런타임 이슈 발견 및 수정 (환경변수 불일치, 포트 충돌, 외부 API Breaking Change, async 미들웨어 충돌 등)

---

## 차별화 포인트

### 1. Before→After 시각화 (6개 사례)

코드 리뷰 전후를 코드 비교로 시각화

→ [docs/Differentiation/BeforeAfter.md](docs/Differentiation/BeforeAfter.md)

### 2. ADR (Architecture Decision Record) 8개

"왜 이 기술을 선택했는가" — 검토한 대안과 트레이드오프 기록

| ADR | 주제 |
|-----|------|
| 001 | Redis Rate Limiting (vs In-Memory, API Gateway) |
| 002 | JWT 토큰 전략 (vs Session, OAuth2) |
| 003 | Flyway DB 마이그레이션 (vs Hibernate auto, Liquibase) |
| 004 | Zustand 상태 관리 (vs Redux, Recoil, Context) |
| 005 | 토큰 저장 전략 (vs localStorage, httpOnly Cookie) |
| 006 | Markowitz 최적화 (vs Black-Litterman, Risk Parity) |
| 007 | FastAPI sync endpoints (vs async, httpx) |
| 008 | Docker Compose (vs 수동 실행, Kubernetes) |

→ [docs/Differentiation/ADR/](docs/Differentiation/ADR/)

### 3. 장애 시뮬레이션 14개

Redis/DB/외부 API 장애 시 graceful degradation 테스트

→ [docs/Differentiation/ResilienceTest.md](docs/Differentiation/ResilienceTest.md)

---

## 문서 목록

| 경로 | 내용 |
|------|------|
| [docs/Phase/](docs/Phase/) | 구현 계획 5단계 |
| [docs/Review/Auth.md](docs/Review/Auth.md) | auth-service 코드 리뷰 (19건) |
| [docs/Review/LLM.md](docs/Review/LLM.md) | llm-service 코드 리뷰 (13건) |
| [docs/Review/Frontend.md](docs/Review/Frontend.md) | frontend 코드 리뷰 (21건) |
| [docs/Integration/DockerCompose.md](docs/Integration/DockerCompose.md) | 통합 테스트 (10/10) |
| [docs/Differentiation/BeforeAfter.md](docs/Differentiation/BeforeAfter.md) | Before→After 코드 비교 (6개) |
| [docs/Differentiation/ADR/](docs/Differentiation/ADR/) | 기술 선택 근거 (8개) |
| [docs/Differentiation/ResilienceTest.md](docs/Differentiation/ResilienceTest.md) | 장애 시뮬레이션 (14개) |

---

## 면책 문구

> 본 서비스는 투자 참고 정보를 제공하며, 투자 조언이 아닙니다. 모든 투자 판단과 책임은 이용자 본인에게 있습니다.
