# META_REVIEW.md — Aether 시니어 메타 회고 ("처음부터 다시 짠다면")

> **본 문서의 본질**: Aether 시나리오 A(기술 데모) 본격 진행 일단락 시점에서 시니어 코드 리뷰어 시각의 자기 회고. 다음 프로젝트(Houseman Phase 7-12 진화) 적용 학습을 코드 / 페이지 / 기능 / 카드 진행 4 차원으로 추출.
>
> **작성일**: 2026-05-05 (M-1 카드)
> **결과물**: 본 문서 1개 (코드 변경 0 / 다른 docs 변경 0 / git 작업 0)
> **자료**: Explore × 3 병렬 측정 + PRINCIPLES.md / WORK_PATTERNS.md 직독 + git log 25 commit + ADR 0001-0010
> **출처 의무**: 모든 "시니어 권장" 표현에 구체 출처 박음 (PRINCIPLES.md 원칙 5 적용 — 결정 근거 추적)

---

## §0. Context — 왜 이 회고인가

### 도착점
| 영역 | 박힌 사실 | 출처 |
|---|---|---|
| Top 10 카드 | 9/10 머지 (T-1a/b · H-1/4/6/7/10 · L-7 · T-2 · T-6) — T-3 보류 | git log #1-#18 |
| ADR | 10건 (0001 microservice → 0010 T-3 deferred) | docs/adr/ |
| 문서 시스템 | PRINCIPLES v5 + WORK_PATTERNS v4 + AGENTS/CLAUDE + SCENARIO v3 + EVOLUTION | docs/agent-capability-audit/ |
| 차별화 카드 | T-2 MCP stdio (국내 도메인 0건 패턴) + T-6 운영급 Qdrant | ADR 0008 / 0009 |
| 보류 결정 | T-3 Multi-Agent (시나리오 A 본질 X) | ADR 0010 |

### 본 회고의 근본 질문 (PRINCIPLES.md §원칙 1 — "내가 원하는 게 뭔지")

> *"Aether 다시 짠다면 어떻게 다르게?"* — 면접관이 물었을 때 답할 수 있는가.

**답의 본질** (PRINCIPLES.md §시니어 판단 패턴 6 — *"박지 않은 결정 = 명시한 결정만큼 강한 시그널"*):
- 코드 비판 X
- 시나리오 적합성 회고 O
- 시간 / 학습 곡선 / 시나리오 본질 분리 O
- 다음 프로젝트 진화 트리거 O

---

## §1. 백엔드 (portfolio-service / auth-service / llm-service)

### §1.1 portfolio-service (FastAPI 3.11)

**박힌 패턴 인용**

| 항목 | 위치 | 평가 |
|---|---|---|
| Layer 분리 (routers → services → utils) | `app/routers/` `app/services/` | Clean ✓ |
| Domain 단일책임 | optimizer / risk / backtest / drift_detector | SOLID-S ✓ |
| MCP stdio 4 도구 외부 노출 | `app/mcp_server.py:87-108` | 차별화 시그널 ✓ (ADR 0008) |
| Cache 전략 패턴 | `app/services/cache.py:30-65` (InMemoryCache + RedisCache 인터페이스) | 가역 토글 ✓ |
| JWT 의존성 주입 | `app/middleware/auth.py` (verify_jwt) | DI 패턴 ✓ |
| 분산 추적 | `app/middleware/logging.py` (request_id ContextVar) | L-7 정착 ✓ |

**시니어 권장 패턴 + 출처**

| 안티 패턴 | 시니어 권장 | 출처 |
|---|---|---|
| `main.py:23-29` CORS `allow_methods=["*"]` | 명시 메서드 (GET/POST) | OWASP CORS Misconfiguration |
| `cache.py:30-65` InMemoryCache maxsize 부재 | LRU + size limit (메모리 누수 차단) | functools.lru_cache 공식 docs |
| `optimizer.py:42` 공분산 임계값(`max_condition_number=1e12`) 미문서화 | 결정 근거 ADR 또는 인라인 주석 (WHY) | PRINCIPLES.md §원칙 5 |
| `experiment.py` MLflow 통합 완료도 불명확 | 사용처 미증명 → 시나리오 A 본질 X 제거 후보 | PRINCIPLES.md §시니어 판단 4 |
| `mcp_server.py` stdio 인증 미적용 | 운영자 신뢰 기반 — 시나리오 A는 OK / B 진입 시 전환 의무 | ADR 0008 |

**5 품질 차원 평가**

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 8/10 | Layer 분리 명확. 한글 주석 도메인 가독성 우위 (CLAUDE.md §3 정합) |
| 유지보수성 | 8/10 | Service 단일책임. 18 테스트 / 3.7k LOC 안전망 |
| 확장성 | 9/10 | MCP 외부화 = 차별화 (Claude Desktop/Cursor 직접 호출 가능) |
| 테스트 가능성 | 7/10 | conftest.py JWT 우회 fixture로 통합 테스트 박힘. edge case 부족 |
| 디버깅 용이성 | 8/10 | request_id 자동 전파. 로깅 마스킹(Bearer ***) |

**차이 발생 이유**: 시나리오 A 본질 = "기술 데모". MCP / Drift Detector / MLflow 등 다층 박힘은 시니어 시그널 의도. 다만 일부(MLflow)는 사용처 미증명 — *"하면 좋아 보임"* 영역 (PRINCIPLES.md §시니어 판단 4 본질 vs 비본질).

### §1.2 auth-service (Spring Boot 3.2.12, Java 21)

**박힌 패턴 인용**

| 항목 | 위치 | 평가 |
|---|---|---|
| 표준 3-tier (Controller → Service → Repository) | `api/auth/` `application/auth/` `domain/user/` | Clean ✓ |
| JJWT 0.12.5 (최신) HS256 | `global/security/JwtTokenProvider.java` | 보안 시그널 ✓ |
| Refresh token Redis 저장 | TTL 기반 (REFRESH_TOKEN_PREFIX) | 운영 시그널 ✓ |
| Token blacklist (logout) | BLACKLIST_PREFIX | 보안 시그널 ✓ |
| JTI (UUID) 이중화 | JwtTokenProvider | 토큰 재사용 차단 ✓ |
| BCrypt password | PasswordEncoder 자동 설정 | 표준 ✓ |
| RateLimitInterceptor | `global/security/` | 인터셉터 기반 ✓ |
| GlobalExceptionHandler + ErrorCode enum | `global/error/` | 일관 에러 응답 ✓ |
| MDC 로깅 | `global/common/` (userId 컨텍스트) | 분산 추적 호환 ✓ |

**시니어 권장 패턴 + 출처**

| 안티 패턴 | 시니어 권장 | 출처 |
|---|---|---|
| RateLimitInterceptor 로컬 상태 | Redis 분산 락 (Bucket4j-Redis) | Spring Boot Reference Guide §Distributed Rate Limiting |
| 8 테스트 시나리오 (간단 시나리오만) | 토큰 만료 / 중복 이메일 / 동시 refresh edge case | WORK_PATTERNS §체크리스트 G |
| Audit (생성/수정 시간) 미확인 | JpaAuditingConfig + @CreatedDate / @LastModifiedDate | Spring Data JPA 공식 docs |
| Flyway 9.22.3 (구버전) | 최신화 체크 (10.x) | Flyway 공식 release notes |

**5 품질 차원 평가**

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 9/10 | 표준 3-tier + Lombok @RequiredArgsConstructor (Spring 정합) |
| 유지보수성 | 8/10 | Layer 명확 + ErrorCode enum 추가 시 영향 범위 작음 |
| 확장성 | 8/10 | 표준 3-tier 재사용 가능 (다른 도메인 추가 시 같은 패턴) |
| 테스트 가능성 | 6/10 | MockMvc + @DataJpaTest 박힘. edge case 부족 |
| 보안 | 8/10 | JWT Redis blacklist + JTI + BCrypt + RateLimit = 보안 다층 박힘 |

### §1.3 llm-service (FastAPI + LangGraph + Gemini 2.5-Flash)

**박힌 패턴 인용**

| 항목 | 위치 | 평가 |
|---|---|---|
| ReAct Agent (T-1b) | `app/agents/react_agent.py:20-43` | LLM 자율 1 호출 ✓ (ADR 0006) |
| Tool Registry lazy init | `app/agents/tools.py:12-41` | WORK_PATTERNS 자기 일관성 패턴 1 적용 ✓ |
| Prompt Registry 버전 관리 | `app/services/prompt_registry.py` (8 prompts v1.0) | ADR 0003 정착 ✓ |
| RAG (ChromaDB → Qdrant 어댑터) | `app/services/rag.py` | T-6 ADR 0009 ✓ |
| LLM Provider 추상화 | `app/services/llm.py` (call_llm / call_llm_structured) | 어댑터 패턴 ✓ |
| Token Tracker | `app/services/token_tracker.py` (비용 메트릭) | LLMOps 시그널 ✓ |
| Portfolio Client (httpx + retry) | `app/services/portfolio_client.py` | 분산 추적 박힘 (event_hooks) ✓ |
| Guardrails (sanitize_user_input) | `app/services/guardrails.py` | 입력 검증 ✓ |

**LangGraph ReAct 통합 흐름** (`react_agent.py:20-43`)
```
chat.py:331-356
  └─ if settings.use_react_agent:
       react_agent.ainvoke(messages)
       → LangGraph create_react_agent 호출
       → Tool 호출 결과 → _extract_tool_results 어댑터 (4키 dict)
       → frontend 회귀 0 (응답 호환 어댑터 — WORK_PATTERNS 패턴 3)
     else:
       절차적 4 호출 fallback (USE_REACT_AGENT 토글로 즉시 롤백)
```

**시니어 권장 패턴 + 출처**

| 안티 패턴 | 시니어 권장 | 출처 |
|---|---|---|
| `main.py:27-32` API 키 RuntimeError (런타임) | startup 이벤트 fail-fast | FastAPI 공식 docs §Lifespan Events |
| `rag.py:76` Gemini embedding 단건 호출 반복 | batch_embed() — google-genai 공식 batch API | google-genai SDK docs |
| RAG 청크 사이즈 명시 부재 (단락 기반 split만) | token-aware chunking + overlap (LangChain TextSplitter 패턴) | LangChain 공식 docs |
| `_chroma_client` 전역 변수 | Singleton lazy init 캡슐화 | WORK_PATTERNS 자기 일관성 패턴 1 |
| ReAct ainvoke 결과 dict/string 분기 | 응답 호환 어댑터 명시 (try/except + isinstance) | WORK_PATTERNS 문제 7 (ToolMessage.content 가정 오류) |

**5 품질 차원 평가**

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 7/10 | 모듈 분산 (agents/services/routers) — 신규 진입자가 ReAct 흐름 파악에 시간 |
| 유지보수성 | 7/10 | Provider 추상화 ✓. RAG 청크 정책 미문서화 — 변경 영향 범위 불명 |
| 확장성 | 8/10 | LangGraph + ChromaDB→Qdrant 어댑터 (T-6) = 운영급 전환 검증됨 |
| 테스트 가능성 | 7/10 | 4.4k LOC 테스트. ReAct 통합 테스트 박힘 (chat_react_integration.py) |
| 디버깅 용이성 | 7/10 | Token Tracker + 분산 추적 ✓. ReAct 메시지 흐름 추적은 중급 난이도 |

### §1.4 백엔드 학습 (Houseman 적용 가능)

1. **Lazy Init Singleton 자기 일관성**: prompt_registry / tool_registry / chroma_client 동일 패턴 박힘 ✓ → Houseman 시작 시점부터 자기 일관성 박기 (WORK_PATTERNS 패턴 1).
2. **CORS 명시 메서드**: 첫날부터 `allow_methods=["GET", "POST"]` (와일드카드 X) — OWASP 시그널.
3. **Cache maxsize**: InMemoryCache는 LRU + maxsize 박기 — 운영급 결정 미리.
4. **Rate Limit 분산화**: 단일 인스턴스 가정 X → Redis 분산 락 (시나리오 B 진입 시점 트리거).
5. **외부 SDK 마이그레이션**: 응답 호환 어댑터 한 줄로 흡수 (WORK_PATTERNS 패턴 3) — H-6 디벨롭 사례 정착.
6. **ADR 결정 근거 추적**: 0001-0010 = 6개월 후 *"왜 이렇게?"* 답 가능 (PRINCIPLES.md §원칙 5).

---

## §2. 프론트엔드 + 페이지 (Next.js 16 + Tailwind 4 + Zustand)

### §2.1 컴포넌트 / 상태 관리 회고

**박힌 패턴**

| 영역 | 위치 | 평가 |
|---|---|---|
| 상태 관리 | `src/store/authStore.ts` (Zustand persist) | 가벼움 ✓ |
| HTTP 클라이언트 | `src/lib/api/client.ts:5-19` (Axios + 401 refresh queue) | 일반 패턴 ✓ |
| API 분리 | authApi / portfolioApi / llmApi | 도메인 분리 ✓ |
| 인증 흐름 | accessToken 메모리 + refreshToken localStorage | XSS 방어 의도 ✓ |
| 라우팅 | App Router (Next.js 16) | 표준 ✓ |
| 차트 | Recharts (LineChart / PieChart) | 표준 ✓ |

**시니어 권장 패턴 + 출처**

| 안티 패턴 | 시니어 권장 | 출처 |
|---|---|---|
| shadcn/ui 미설치 X — 100+ 인라인 className 누적 | shadcn/ui 공식 컴포넌트 + design tokens | shadcn 공식 docs |
| Form state useState 분산 (optimize 5 입력) | react-hook-form + zod | RHF 공식 docs |
| `client.ts:5-19` failedQueue race condition (동시 401) | Atomic refresh lock (mutex 패턴) | Axios interceptor 패턴 사례 |
| useState 페이지 레벨 결과 보존 (페이지 reload 시 손실) | localStorage 캐시 + SWR/React Query | TanStack Query 공식 docs |
| ARIA live region 부재 (chat 메시지 / 에러 alert) | role="status" + aria-live="polite" | WAI-ARIA 공식 spec |
| 색상만으로 위험 표시 (red = negative) | 색상 + 텍스트 + 아이콘 (3중) | WCAG 2.1 1.4.1 색 사용 |

### §2.2 페이지별 회고 (실측 LOC)

**전체 페이지 7개**

| 페이지 | 라인 수 | 목적 | 시나리오 A 적합성 | 다시 짠다면 |
|---|---|---|---|---|
| `/` | (홈) | Hero + Feature 4개 + CTA | OK | shadcn 컴포넌트로 정리 |
| `/login` | (간소) | 2-field form | OK | RHF + zod 박기 |
| `/signup` | (간소) | 3-field form | OK | RHF + zod 박기 |
| `/dashboard` | 91 | KPI 4 카드 + Quick Action 3 | OK | 그대로 (간결 ✓) |
| `/dashboard/optimize` | **344** | Ticker 선택 → 최적화 → Pie/Metric/AI 분석 | 본질 ✓ (시그널 강함) | **컴포넌트 분리 의무** |
| `/dashboard/backtest` | **217** | Ticker 선택 → 백테스트 → Line/8 metric 카드 | 본질 ✓ | **컴포넌트 분리 의무** |
| `/dashboard/chat` | 167 | RAG 기반 AI 어시스턴트 | 본질 ✓ (RAG 시그널) | type guards 추가 |

**§2.2.1 `/dashboard/optimize` (344 LOC) — 모놀리식 페이지 본질 안티**

- **현재 박힌 구조**: form + 차트 + AI 분석 텍스트 cleanup + Result 카드 모두 1 파일
- **시니어 권장 (Next.js 공식 docs §Server Components / App Router)**:
  ```
  src/app/dashboard/optimize/page.tsx (50 LOC)
  ├─ src/components/optimize/OptimizationForm.tsx
  ├─ src/components/optimize/AllocationChart.tsx
  ├─ src/components/optimize/AIAnalysisPanel.tsx
  └─ src/hooks/useOptimize.ts (mutation hook)
  ```
- **차이 발생 이유**: 시간 / 학습 곡선 (Next.js 16 App Router 첫 적용) — *"동작 먼저 박고 정리는 나중"* 패턴.

**§2.2.2 `/dashboard/backtest` (217 LOC) — 같은 패턴**

- 동일 모놀리식. config + 결과 표 8 카드 + Line chart 모두 inline.
- **시니어 권장**: 같은 추출 패턴.

**§2.2.3 `/dashboard/chat` (167 LOC) — RAG UI**

- 메시지 렌더 루프 / 마크다운 렌더 / 자동 스크롤 박힘 ✓
- **안티**: 메시지 type guards 부재 — `<ChatMessage role={msg.role}>` 분리 권장.

### §2.3 5 품질 차원 평가

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 7/10 | 다크 테마 정합 ✓. 인라인 className 누적이 신규 진입자 부담 |
| 유지보수성 | 6/10 | 모놀리식 페이지 → 작은 변경도 영향 범위 큼 |
| 확장성 | 6/10 | shadcn 미설치 → 신규 컴포넌트 추가마다 인라인 누적 |
| 테스트 가능성 | 5/10 | vitest 5건만 (Dashboard/Chat/Backtest/Optimize/Header) — 통합 테스트 부족 |
| 접근성 | 4/10 | ARIA 부재 / 색상만 표시 — WCAG 2.1 미준수 |

### §2.4 프론트엔드 학습 (Houseman 적용)

1. **shadcn/ui 첫날 설치**: 인라인 className 누적 차단 — 100+ 패턴 → 컴포넌트 props.
2. **모놀리식 페이지 회피**: 200 LOC 임계 — 초과 시 즉시 hooks + 컴포넌트 분리 (Next.js 공식 docs).
3. **RHF + zod**: form state 분산 차단.
4. **React Query / SWR**: 결과 캐시 + 재시도 + 오프라인 처리 (Houseman은 도메인 데이터 양 큼 — 시나리오 B 진입 시).
5. **WCAG 2.1**: 첫날부터 ARIA + 색상 + 텍스트 3중.

---

## §3. 인프라 (docker-compose 6 서비스)

### §3.1 박힌 패턴

| 서비스 | 이미지 | 포트 | 평가 |
|---|---|---|---|
| postgres | postgres:16-alpine | 5433→5432 | auth 전용 ✓ |
| redis | redis:7-alpine | 6380→6379 | auth 토큰/rate-limit ✓ |
| portfolio-service | python:3.11-slim | 8001 | health check 박힘 ✓ |
| llm-service | python:3.11-slim | 8002 | Qdrant 마이그 완료 (T-6) ✓ |
| auth-service | Spring Boot | 8003 | actuator/health ✓ |
| frontend | Next.js 16 | 3000 | wget --spider health ✓ |

**환경 분리**: `.env` 단일 (JWT_SECRET 공유 / GEMINI_API_KEY / CORS_ORIGINS).
**네트워크**: aether-network (단일 bridge).
**Health Check**: 모든 서비스 박힘 (interval 30s / timeout 10s / retries 3).

### §3.2 시니어 권장 패턴 + 출처

| 안티 패턴 | 시니어 권장 | 출처 |
|---|---|---|
| 메모리 / CPU limits 미설정 | `deploy.resources.limits` 명시 | Docker Compose 공식 docs §deploy.resources |
| `.env` 단일 (.env.prod 분리 부재) | 12-factor app §III Config 분리 | 12factor.net |
| auth start_period 60s 과다 | 30s 또는 startup probe | Docker Compose 공식 docs §healthcheck.start_period |
| Postgres 비밀번호 환경변수 평문 | Docker Secrets / Vault | Docker 공식 docs §Secrets |
| Qdrant 5-8GB 운영급 — 백업 정책 미명시 | Snapshot 정책 ADR 박기 | Qdrant 공식 docs §Snapshots |

### §3.3 5 품질 차원 평가

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 8/10 | 6 서비스 명확 / 네트워크 단일 / health check 일관 |
| 유지보수성 | 7/10 | 단일 .env — production/staging 분리 시 변경 범위 큼 |
| 확장성 | 6/10 | 단일 호스트 가정 (k8s 전환 시 재작성 필요) — 시나리오 A 적합 |
| 테스트 가능성 | 7/10 | docker-compose up으로 전체 통합 가능 |
| 디버깅 용이성 | 8/10 | docker logs / compose logs 박힘 |

### §3.4 인프라 학습 (Houseman 적용)

1. **첫날부터 deploy.resources limits**: 메모리 누수 차단.
2. **.env.prod / .env.dev 분리**: 12-factor 첫날 정착.
3. **health check start_period 보수적**: 30s 기준 + startup probe 분리.
4. **Docker Secrets**: 비밀번호 평문 환경변수 회피.
5. **Qdrant 백업 ADR**: 운영급 벡터 DB 첫 도입 시 backup 정책 박힘.

---

## §4. 문서 시스템 (Aether의 강점)

### §4.1 박힌 자산

| 문서 | 위치 | 역할 |
|---|---|---|
| AGENTS.md | repo root | What (코드 사실 / 지배 숫자) |
| CLAUDE.md | repo root | How (작업 규칙 / PR 게이트 / 위험 작업 확인) |
| PRINCIPLES.md | docs/agent-capability-audit/ | 범용 본질 (5 원칙 + 시니어 판단 7 패턴) |
| WORK_PATTERNS.md | docs/agent-capability-audit/ | 18 누적 문제 + 체크리스트 A-G + 자기 일관성 5 + F-패턴 |
| SCENARIO.md | docs/agent-capability-audit/ | 시나리오 A/B/C 분류 + 정착 사례 |
| EVOLUTION.md | docs/agent-capability-audit/ | 프로젝트 진화 트리거 |
| ADR 0001-0010 | docs/adr/ | 결정 근거 10건 |
| phase3/ 카드 | docs/agent-capability-audit/phase3/ | 카드별 §1-§11 절차 |

### §4.2 시니어 권장 패턴 + 출처

| 측면 | 평가 | 출처 |
|---|---|---|
| What/How 분리 (AGENTS / CLAUDE) | ✓ 정착 | CLAUDE.md §본 문서의 본질 |
| 결정 근거 추적 (ADR 10건) | ✓ 강점 | PRINCIPLES.md §원칙 5 — *"AI 추천 vs 본인 결정 분리 추적"* |
| 평가 시스템을 AI가 구축 (WORK_PATTERNS) | ✓ 강점 | PRINCIPLES.md §원칙 3 |
| 본질 원칙 추적 (PRINCIPLES.md) | ✓ 강점 | 랄프톤 영상 인용 (Jensen Huang / Orchid 사례) 박혀있음 |
| Notion / Confluence vs git-native | git-native 우위 | 정합성 / 검색 / blame / PR 리뷰 통합 |

### §4.3 5 품질 차원 평가 (강점 영역)

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 9/10 | CLAUDE.md §2 PR 게이트 표 / WORK_PATTERNS 카테고리 A-G — 시니어 시그널 강함 |
| 유지보수성 | 9/10 | 갱신 의무 박힘 (PR 체크리스트) — 30일 14 commit 평균 2일/카드 |
| 확장성 | 9/10 | PRINCIPLES.md = 범용 (Houseman 그대로 사용 가능) |
| 추적성 | 10/10 | ADR 10건 + git log + 카드 phase3/ — 6개월 후 답 가능 |
| 자기 일관성 | 9/10 | WORK_PATTERNS 패턴 1 (Lazy Init Singleton) = 코드와 문서 동일 정착 |

**시니어 회고**: 문서 시스템은 **Aether의 본질 강점**. 다시 짜도 동일 채택 + Houseman에 그대로 이식.

### §4.4 문서 시스템 학습 (Houseman 적용)

1. **PRINCIPLES.md 그대로 이식**: 범용 본질 (5 원칙 + 시니어 판단 7 패턴) — 프로젝트 무관 적용.
2. **WORK_PATTERNS.md 빈 상태 시작**: 새 프로젝트 18 문제 누적 박힐 자리.
3. **ADR 첫날부터**: 0001 → microservice / 0002 → module boundaries / 0003 → tech stack 등 패턴 동일.
4. **AGENTS.md(What) + CLAUDE.md(How) 분리**: 첫날 정착.
5. **SCENARIO.md 첫날**: A/B/C 명확 박기 (PRINCIPLES.md §시나리오 분류 가이드 적용).

---

## §5. AI 통합 (LangGraph + RAG + MCP + Qdrant)

### §5.1 박힌 패턴 인용

| 항목 | 위치 | 평가 |
|---|---|---|
| LangGraph ReAct (T-1b) | `app/agents/react_agent.py:20-43` (`create_react_agent`) | LLM 자율 1 호출 ✓ (ADR 0006) |
| Tool Registry lazy init | `app/agents/tools.py:12-41` (4 @tool) | WORK_PATTERNS 패턴 1 ✓ |
| Prompt Registry 버전 관리 (8 prompts) | `app/services/prompt_registry.py` | ADR 0003 ✓ |
| RAG ChromaDB→Qdrant 어댑터 (T-6) | `app/services/rag.py` | 운영급 전환 ✓ (ADR 0009) |
| MCP stdio 4 도구 (T-2) | `portfolio-service/app/mcp_server.py` | 차별화 ✓ (ADR 0008) |
| Gemini 2.5-Flash native structured output | `app/services/llm.py` (response_schema) | H-6 디벨롭 ✓ (ADR 0007) |
| Token Tracker (비용 메트릭) | `app/services/token_tracker.py` | LLMOps 시그널 ✓ |
| RAG Evaluator (6 평가 쿼리) | `app/services/rag_evaluator.py` | 평가 시스템 ✓ (PRINCIPLES.md §원칙 3) |

### §5.2 시니어 권장 패턴 + 출처

**박힌 강점**

| 패턴 | 출처 |
|---|---|
| ReAct 결과 4키 dict 어댑터 (frontend 회귀 0) | WORK_PATTERNS 자기 일관성 패턴 3 (응답 호환 어댑터) |
| `USE_REACT_AGENT` 토글 (즉시 롤백) | WORK_PATTERNS 패턴 4 (환경변수 즉시 롤백) |
| T-1a (인프라) + T-1b (동작) 2단 분해 | WORK_PATTERNS 패턴 5 (옵션 B 회귀 위험 분리) |
| ChromaDB→Qdrant 어댑터 (호출자 0 변경) | WORK_PATTERNS 패턴 3 |
| MCP stdio 외부 노출 (Claude Desktop / Cursor 직접 호출) | ADR 0008 + 랄프톤 영상 (Orchid 사례 — *"AI에게 어떻게 할지 연구 시키기"*) |

**미적용 / 안티 패턴**

| 안티 패턴 | 시니어 권장 | 출처 |
|---|---|---|
| RAG 청크 사이즈 명시 부재 (단락 기반 split) | token-aware chunking + overlap | LangChain TextSplitter 공식 docs |
| Gemini embedding 배치 부재 (단건 호출 반복) | `embed_content_batch` (google-genai 1.74) | google-genai SDK docs |
| MCP stdio 인증 미적용 | 시나리오 A 적합 / B 진입 시 인증 의무 | ADR 0008 트리거 |
| ReAct ToolMessage.content 가정 의존 | isinstance 분기 + try/except | WORK_PATTERNS 문제 7 |

### §5.3 LangGraph 채택 회고 (ADR 0005 / 0006)

**랄프톤 영상 인용** (PRINCIPLES.md §원칙 4):
> *"AI can do a lot of things. You just need to ask it how it can. Ask it to research how it can achieve something."* — Orchid 우승자

→ T-1 진입 시 *"LangGraph 어떻게 박을지 연구 시키기"* 패턴 적용. 절차적 4 호출 → ReAct 1 호출 = *"AI 자율"* 위임 (PRINCIPLES.md §원칙 4 §위임 패턴 1 — 결과 명시 + 방법 위임).

### §5.4 5 품질 차원 평가

| 차원 | 점수 | 근거 |
|---|---|---|
| 가독성 | 7/10 | LangGraph 처음 진입자에 학습 곡선. ReAct 메시지 흐름은 추상도 높음 |
| 유지보수성 | 8/10 | Tool Registry / Prompt Registry / RAG 어댑터 = 단일 진입점 (변경 영향 범위 작음) |
| 확장성 | 9/10 | LangGraph + MCP + Qdrant = 운영급 / 외부 LLM 통합 / 다중 도구 추가 용이 |
| 테스트 가능성 | 7/10 | 4.4k LOC / chat_react_integration / RAG evaluator 박힘 |
| 디버깅 용이성 | 7/10 | Token Tracker + 분산 추적 ✓. ReAct 메시지 흐름 추적 중급 |

### §5.5 AI 통합 학습 (Houseman 적용)

1. **LangGraph 첫날부터** (Houseman 도메인 = 부동산 / 가전 추천 등 — 도구 호출 패턴 동일).
2. **MCP 외부 노출 패턴 그대로 이식**: Houseman 핵심 도구 → MCP stdio 노출 = Claude Desktop 통합 차별화.
3. **Prompt Registry 버전 관리 첫날**: 프롬프트 변경 추적 + A/B 테스트.
4. **Qdrant 첫 선택**: ChromaDB → Qdrant 마이그 비용 0 (Houseman은 데이터 양 큼).
5. **응답 호환 어댑터 패턴 (WORK_PATTERNS 패턴 3)**: 외부 SDK 변경 흡수 한 줄.
6. **Token Tracker / RAG Evaluator**: LLMOps 시그널 — 첫날부터.
7. **Multi-Agent는 시나리오 B 진입 시점**: T-3 보류 패턴 그대로 (PRINCIPLES.md §시니어 판단 6).

---

## §6. 기능 선택 회고

### §6.1 박힌 기능 목록 (실측)

**llm-service**:
- chat (RAG 기반 AI 어시스턴트)
- chat structured (분석 / 백테스트 / 추천 4키 dict)
- 4 도구 (analyze_portfolio / explain_risk / summarize_backtest / get_recommendation)

**portfolio-service**:
- optimize (포트폴리오 최적화 — Mean-Variance / Risk Parity)
- backtest (히스토리 백테스트)
- risk (리스크 메트릭)
- experiment (MLflow 통합)
- drift_detector (volatility/correlation 변화 / 시장 레짐)
- weight_monitor (비중 변화 알림)
- MCP stdio 4 도구 외부 노출

**auth-service**:
- signup / login / refresh / logout / me 5 엔드포인트

### §6.2 시나리오 A 적합성 평가 (PRINCIPLES.md §시니어 판단 4 — 본질 vs 비본질)

| 기능 | 본질 / 비본질 | 근거 |
|---|---|---|
| chat (RAG) | **본질 ✓✓** | RAG = AI 통합 시그널 강함 / 면접 직격 |
| chat structured | **본질 ✓✓** | Gemini native structured output = 시니어 시그널 |
| optimize | **본질 ✓** | 도메인 코어 + AI 분석 텍스트 통합 시그널 |
| backtest | **본질 ✓** | 도메인 코어 + 시각화 |
| MCP 4 도구 외부 노출 | **본질 ✓✓✓** | T-2 차별화 — 국내 도메인 0건 패턴 |
| Qdrant 마이그 (T-6) | **본질 ✓✓** | 운영급 결정 근거 실증 (TECH §1) |
| risk | 보조 | 도메인 보조 기능 |
| drift_detector | **비본질** | 사용처 미증명 (시그널은 있지만 데모 동작 X) |
| weight_monitor | **비본질** | 알림 구독자 부재 |
| experiment (MLflow) | **비본질** | MLflow 통합 완료도 불명확 / 사용처 미증명 |
| auth (signup/login/...) | 본질 ✓ | JWT + Redis blacklist + Rate Limit = 보안 시그널 |

### §6.3 다시 짠다면 박을 기능 (시니어 시그널 우선)

1. **chat (RAG)** + **chat structured** — AI 통합 시그널
2. **optimize** + **backtest** — 도메인 코어
3. **MCP 외부 노출** — T-2 차별화 첫날 박기 (선후 의존성 X)
4. **Qdrant** — 첫날 채택 (ChromaDB→Qdrant 마이그 비용 절감)
5. **auth (5 엔드포인트)** — 보안 다층 박기

### §6.4 빼야 했던 기능 후보

| 기능 | 사유 | 처리 |
|---|---|---|
| experiment (MLflow) | 시나리오 A 본질 X / 사용처 미증명 | Houseman에 박지 X |
| drift_detector | *"하면 좋아 보임"* 영역 | 시나리오 B 진입 시점 트리거 박기 |
| weight_monitor | 알림 구독자 부재 | 시나리오 B 진입 시점 |

→ PRINCIPLES.md §시니어 판단 4 적용 — **"본질 vs 비본질" 기준으로 첫날부터 박지 않기.**

### §6.5 가정 페르소나 시나리오

**페르소나 1 — 면접관 (시니어 백엔드)**:
- 본 프로젝트의 차별화 한 줄? → MCP stdio 외부 노출 (T-2)
- ADR 10건 / WORK_PATTERNS 18 문제 / PRINCIPLES 5 원칙 = 시그널 강함
- 약점 질문: "MLflow / drift_detector 왜 박았어요?" → 시나리오 A 본질 X 인정 + 보류 트리거 명시 = 시니어 답

**페르소나 2 — 채용 담당**:
- README.md 가독성 → CLAUDE.md §2 PR 게이트 표 + 6 서비스 docker-compose 한눈에 = OK
- 시각적 시그널: optimize/backtest 페이지 차트 + 다크 테마 정합

**페르소나 3 — 동료 시니어**:
- 코드 가독성: 백엔드 8/10 / 프론트엔드 7/10 (모놀리식 페이지 감점)
- 자기 일관성: 백엔드 ✓ (Lazy Init 일관) / 프론트엔드 X (인라인 누적)
- 결정 추적: ADR 10건 = 강점

---

## §7. 카드 진행 순서 회고

### §7.1 실제 진행 (git log #1-#18 + 추가 카드)

| 순서 | 카드 ID | 한 줄 | 시점 (PR 번호) |
|---|---|---|---|
| 1 | H-7 | PR 게이트 6단계 도입 (ruff/black/mypy/pytest-cov + vitest/eslint/tsc + markdownlint) | dd32308 |
| 2 | H-1 | AGENTS.md / CLAUDE.md / ADR 0001-0003 정착 | 3ad31aa |
| 3 | H-4 | RAG 프롬프트 prompt_registry 일원화 | e9acdf8 |
| 4 | H-6 | Gemini 네이티브 구조화 출력 도입 | fe07ee1 (PR #1) |
| 5 | H-10/L-7 | JWT 검증 + X-Request-ID 자동 전파 | 2ea2d00 (PR #2) |
| 6 | T-1a + H-2 | LangGraph 인프라 + tool_registry + 4 도구 @tool 래핑 | 35e64c8 (PR #3) |
| 7 | T-1b | chat.py 절차적 4 호출 → LangGraph ReAct 1 호출 통합 | 0040f48 (PR #4) |
| 8 | H-1c | AGENTS.md §7 지배 숫자 표 중복 행 정리 | e7dc1ea (PR #5) |
| 9 | H-6 디벨롭 | google-generativeai → google-genai SDK 마이그레이션 | e28d7d3 (PR #6) |
| 10 | WORK_PATTERNS v1 | 18 문제 + 체크리스트 + 자기 일관성 + 메모리 통합 | e96ce75 (PR #7) |
| 11 | T-2 Blocked | fastapi 0.104.1 vs mcp 1.x 충돌 ADR | 0cb25cb (PR #9) |
| 12 | H-X (선행) | fastapi 0.104.1 → 0.119.1 업그레이드 | 877eaf2 (PR #10) |
| 13 | docs cleanup | AETHER_ prefix 제거 | 4d647d2 (PR #11) |
| 14 | T-2 본격 | MCP stdio 서버 4 도구 외부 노출 | dfe8ae3 (PR #12) |
| 15 | WORK_PATTERNS v4 | F-패턴 (검증 + 분기 + 머지 자동화) 추가 | 27a863e (PR #13) |
| 16 | T-6 | ChromaDB → Qdrant 어댑터 마이그레이션 | 64620dd (PR #14) |
| 17 | PRINCIPLES v4 | 시니어 판단 패턴 섹션 신규 추가 | 3b1edba (PR #15) |
| 18 | WORK_PATTERNS v5 | plan 검수 13 영역 가이드 신규 섹션 추가 | b46a7c2 (PR #16) |
| 19 | C-1 / T-3 보류 | T-3 보류 결정 + ADR 0010 + EVOLUTION + PRINCIPLES 6/7 + SCENARIO v3 | c8700cc (PR #18) |

### §7.2 다시 짠다면 최적 순서 (의존성 사슬 분석)

```
[Phase 0 — 문서 시스템 먼저]
  PRINCIPLES.md (범용 — 빈 프로젝트라도 즉시 적용 가능)
  ↓
  AGENTS.md + CLAUDE.md + SCENARIO.md (프로젝트 본질 박음)
  ↓
[Phase 1 — 안전망]
  H-7 (PR 게이트) → 모든 후속 카드의 안전망
  ↓
  H-1 (ADR 0001-0003 + 컨텍스트 엔지니어링)
  ↓
[Phase 2 — 인증/추적 인프라]
  H-10 + L-7 (JWT + X-Request-ID) → 모든 서비스 통신 전제
  ↓
[Phase 3 — AI 통합 코어]
  H-4 (Prompt Registry) → 프롬프트 일원화
  ↓
  H-6 (Gemini structured output) → AI 호출 안정화
  ↓
  T-1a (LangGraph 인프라) → T-1b (ReAct 통합)
  ↓
[Phase 4 — 차별화 카드]
  T-2 (MCP stdio) → 외부 LLM 통합
  ↓
  T-6 (Qdrant) → 운영급 벡터 DB
  ↓
[Phase 5 — 평가 시스템]
  WORK_PATTERNS (18 문제 누적) — 카드 진행 중 자연스럽게 누적
  ↓
[Phase 6 — 보류 결정]
  T-3 (Multi-Agent) 보류 → ADR 0010 + Houseman 진화 시점 트리거
```

### §7.3 보류 결정 분석 (PRINCIPLES.md §시니어 판단 6 — 박지 않은 결정)

**T-3 (Multi-Agent) 보류 결정 (ADR 0010 / PR #18)**

> *"기술 도입 = 누구나 가능 (LangGraph supervisor / MCP / Multi-Agent 등). 시니어 차이 = '박지 않은 결정 + 진입 트리거 명시'"* (PRINCIPLES.md §시니어 판단 6)

**보류 사유**:
- 시나리오 A(기술 데모) 본질 X — Multi-Agent 복잡도 과다
- LangGraph supervisor + worker 패턴 학습 + 적용 통합 = Houseman 진화 시점 트리거 명시

**시그널 가치**: 면접관에게 *"왜 Multi-Agent 안 박았어요?"* 물으면 답 가능 = 시니어 의사결정 시그널.

### §7.4 의존성 학습 (어떤 카드 먼저면 후속이 쉬웠나)

| 의존성 | 결과 |
|---|---|
| **H-7 (PR 게이트) 가장 먼저** | 후속 모든 카드의 안전망 — coverage 81% / vitest / tsc 차단 = 회귀 0건 |
| **H-1 (문서 시스템) 두 번째** | 후속 모든 카드가 AGENTS/CLAUDE 정합 가능 |
| **H-10 (JWT) → T-2 (MCP)** | JWT 박힌 후 MCP stdio 외부 노출 결정 (인증 미적용 / 운영자 신뢰) 명확 |
| **T-1a (인프라) → T-1b (동작)** | 회귀 위험 분리 — WORK_PATTERNS 패턴 5 (옵션 B 2단 분해) |
| **H-X (fastapi 업그레이드) → T-2 본격** | T-2 Blocked 인지 후 선행 카드 분리 = WORK_PATTERNS 문제 18 |

### §7.5 학습 누적

- **WORK_PATTERNS 18 문제** = 카드 진행 중 자연스럽게 누적된 학습 자산.
- **PRINCIPLES.md 시니어 판단 7 패턴** = 카드 회고에서 추출.
- **ADR 10건** = 6개월 후 본인 답 가능 자산 (PRINCIPLES.md §원칙 5).

---

## §8. 종합 학습 (Houseman Phase 7-12 진화 적용)

### 학습 1 — 문서 시스템 첫날 박기
- PRINCIPLES.md 그대로 이식 (범용)
- AGENTS.md + CLAUDE.md + SCENARIO.md 첫날 정착
- ADR 0001 microservice / 0002 module boundaries 패턴 동일
- WORK_PATTERNS.md 빈 상태 시작 → 18 문제 누적 자리

### 학습 2 — 5 가드 (메모리 #22) + 자기 일관성 패턴 5종 첫날
- Decision Budget / Reversibility / Done Definition / Round Cap / First Principle
- 의사결정 마비 차단 (Aether T-2 진입 직전 7 라운드 분석 사례 — WORK_PATTERNS 문제 9)

### 학습 3 — 시나리오 A/B/C 첫날 명확 박기
- PRINCIPLES.md §시나리오 분류 가이드 적용
- *"가장 위험한 패턴 = 시나리오 혼동"* 차단
- Houseman 시나리오 결정 — A(포트폴리오) / B(소수 사용자) / C(SaaS) 명시 의무

### 학습 4 — 차별화 카드 우선
- Aether T-2 MCP / T-6 Qdrant = 국내 도메인 0건 패턴 (시니어 시그널)
- Houseman 차별화 카드 후보: Multi-Agent supervisor (Aether 보류분 흡수) / 도메인 RAG / MCP 외부화

### 학습 5 — 모놀리식 페이지 회피
- Aether: optimize 344 LOC / backtest 217 LOC = 신규 진입자 부담
- Houseman: 첫날부터 hooks + 컴포넌트 분리 (Next.js 공식 docs §App Router)
- 200 LOC 임계 — 초과 시 즉시 분리 의무

### 학습 6 — 운영급 결정 미리 박기
- Cache maxsize / Rate Limit 분산화 / .env.prod 분리 / Docker resources limits
- 시나리오 B 진입 시점 트리거 명시 (Aether는 미적용 — 시나리오 A 본질 적합)

### 학습 7 — T-3 보류 패턴 그대로 (학습 + 적용 통합)
- 별도 학습 repo 만들지 않음 (재사용 어려움 + 가치 미흡)
- *"진짜 적용 시점 + 학습 + 구현 동시 통합"* — Houseman Phase 7-12 진화 시점에 Multi-Agent 통합

### 학습 8 — F-패턴 (검증 + 분기 + 머지 자동화)
- 사용자 한 줄 프롬프트로 pre-existing 검증 + 자동 분기 + 머지 4단계 처리
- 검증 누락 0건 + Claude 검증 패턴 일관성 (WORK_PATTERNS v4)

### 학습 9 — 응답 호환 어댑터 패턴 (WORK_PATTERNS 패턴 3)
- 외부 SDK 변경 흡수 한 줄 (H-6 디벨롭 google-genai 마이그 / T-1b ReAct 결과 / T-6 Qdrant 어댑터 = 3건 정착)
- Houseman: 외부 API 의존 영역 (부동산 시세 API / 가전 데이터 API) 첫날 어댑터 패턴 박기

### 학습 10 — ADR 결정 근거 추적 (PRINCIPLES.md §원칙 5)
- Aether ADR 10건 = 6개월 후 답 가능 자산
- Houseman 첫날부터 ADR 0001-N 박기 (AI 추천 vs 본인 결정 분리)

---

## §9. 면접 답변 — *"Aether 다시 짠다면 어떻게?"* (3 깊이)

### §9.1 한 줄 답 (5초)
> *"문서 시스템과 5 가드를 먼저 박고, 모놀리식 페이지를 컴포넌트로 분리하고, 시나리오 A 본질 X 기능(MLflow / drift_detector)은 박지 않았을 거예요."*

### §9.2 3 문장 답 (30초)

**코드 측면**:
> *"백엔드는 Lazy Init Singleton / 응답 호환 어댑터 / 환경변수 즉시 롤백 같은 자기 일관성 패턴이 잘 박혔지만, 캐시 maxsize / Rate Limit 분산화 / API 키 startup 검증은 첫날부터 박았을 거예요."*

**기능 측면**:
> *"chat (RAG) / optimize / MCP 외부화 / Qdrant는 시나리오 A 본질에 맞지만, MLflow / drift_detector / weight_monitor는 *'하면 좋아 보임'* 영역이라 빼고, 시나리오 B 진입 시점 트리거만 명시했을 거예요."*

**페이지 측면**:
> *"optimize 344 LOC / backtest 217 LOC 같은 모놀리식 페이지는 첫날부터 hooks + 컴포넌트로 분리하고, shadcn/ui와 RHF + zod를 박아서 인라인 className 누적과 form state 분산을 차단했을 거예요."*

### §9.3 디테일 답 (3분)

**(1) 문서 시스템 — 첫날 박을 자산**

PRINCIPLES.md를 그대로 이식하고, AGENTS.md (What) + CLAUDE.md (How) + SCENARIO.md (시나리오 결정) + ADR 0001 (microservice) / 0002 (module boundaries)을 첫날 박을 거예요. Aether에서 H-7 (PR 게이트) 1번 → H-1 (문서) 2번 순서가 정착이 잘 됐는데, 다시 짠다면 H-7 / H-1 동시 박을 가능성이 높아요. 문서 시스템이 박힌 후 모든 카드가 정합 보장되거든요.

**(2) 코드 측면 — 자기 일관성 패턴**

WORK_PATTERNS 자기 일관성 패턴 5종 (Lazy Init Singleton / Autouse Fixture / 응답 호환 어댑터 / 환경변수 즉시 롤백 / 옵션 B 2단 분해)을 첫날부터 박을 거예요. Aether에서 prompt_registry / tool_registry / chroma_client가 같은 lazy init 패턴을 자기 일관성 있게 박았는데, frontend 인라인 className은 그렇지 못했어요. 다시 짠다면 백엔드/프론트 모두 자기 일관성 박을 거예요.

운영급 결정도 첫날부터 박을 거예요 — cache maxsize / Rate Limit 분산화 / .env.prod 분리 / Docker resources limits / Qdrant 백업 정책 ADR.

**(3) AI 통합 — Aether의 강점 그대로**

LangGraph ReAct + Tool Registry + Prompt Registry + RAG (Qdrant 첫날) + MCP stdio + Gemini structured output = Aether의 본질 강점. 다시 짜도 동일 채택.

차이는 RAG 청크 사이즈 명시 (token-aware chunking + overlap) + Gemini embedding 배치 호출 + ReAct ToolMessage.content isinstance 분기 = 첫날부터 박기.

**(4) 기능 선택 — 시나리오 A 본질 적합**

박을 기능: chat (RAG) / optimize / backtest / MCP 4 도구 외부화 / auth 5 엔드포인트.

빼야 했던 기능: MLflow / drift_detector / weight_monitor = 시나리오 A 본질 X / 사용처 미증명. 시나리오 B 진입 시점 트리거만 명시하고 박지 않을 거예요. PRINCIPLES.md §시니어 판단 6 — *"박지 않은 결정 = 명시한 결정만큼 강한 시그널"* 적용 사례.

**(5) 페이지 — 모놀리식 차단**

Aether optimize 344 LOC / backtest 217 LOC = 모놀리식. 다시 짠다면 200 LOC 임계 박고, 초과 시 즉시 hooks + 컴포넌트 분리. shadcn/ui 첫날 설치 (인라인 className 누적 차단) + RHF + zod (form state 분산 차단) + WAI-ARIA 첫날 박기.

**(6) 카드 진행 순서 — 의존성 사슬 학습**

H-7 (PR 게이트) → H-1 (문서) → H-10/L-7 (JWT/RID) → H-4 (Prompt Registry) → H-6 (structured output) → T-1a/b (LangGraph) → T-2 (MCP) → T-6 (Qdrant) → T-3 보류 (Houseman 트리거 명시) 순서가 의존성 사슬상 최적이고, 실제로도 Aether에서 그렇게 박혔어요.

**(7) 다음 프로젝트 (Houseman Phase 7-12) 진화 적용**

Aether 18 문제 (WORK_PATTERNS) + 7 시니어 판단 패턴 (PRINCIPLES) + 10 학습 (본 §8) = Houseman 첫날 자산. 별도 학습 repo 만들지 않고, *"학습 + 적용 통합"* — Houseman Phase 7-12 진입 시점에 Multi-Agent (Aether T-3 보류분) + 도메인 RAG + 부동산/가전 API 어댑터를 한 번에 박을 거예요.

---

## §10. 부록 — 자기 검수 (PRINCIPLES.md §자가 점검 4 레벨 적용)

### Level 1 — 카드 단위 점검
- [x] 본 카드 끝나면 무엇이 가능? → 면접 직격 답 + Houseman 진화 트리거
- [x] 진짜 원하는 거? → 시니어 메타 회고 본질 ✓
- [x] *"하면 좋아 보임"* X → 학습 추출 본질 O
- [x] AI 추천 그대로? → 출처 의무 박힘 (P/W/V/ADR/공식 docs)
- [x] 첫 프롬프트 4 요소 (작업 / 디테일 / 포인트 / 평가) 박힘
- [x] 시간 cap → 1 라운드 분석 / 재분석 X (G4)

### Level 2 — 프로젝트 본질 점검
- [x] Aether 시나리오 A (기술 데모) 본질 박힘
- [x] 본 회고가 그 본질 회고 (X 비판)
- [x] 시나리오 혼동 X (Houseman 진화 = 별도 프로젝트 트리거 명시)

### Level 3 — AI 협업 점검
- [x] *"위임"* O (META_REVIEW.md 자체 시니어 메타 분석 위임)
- [x] *"주니어 디렉션 시니어"* 관점 박힘
- [x] *"AI 못 한다"* 가정 X — Explore × 3 + 출처 자료 박힘
- [x] AI 결과 검수 ✓ — git log / ADR / LOC 실측 완료
- [x] AI가 본질 결정 침범 X — 면접 답 작성은 사용자 본인 검토 후 채택 의무
- [x] 결정 근거 추적 O — 모든 출처 박힘

### Level 4 — 외부 시각 점검
- [x] 면접관 *"왜 했어요?"* 답 가능 → §9 면접 답변 3 깊이
- [x] *"AI가 추천해서요"* X → §3 출처 매핑 박힘
- [x] *"무엇을 원했나 → 후보 비교 → 선택 + 트레이드오프"* 박힘 → §6 기능 선택 + §7 카드 순서

---

## §11. 마지막 한 문장

> *"Aether는 시나리오 A(기술 데모) 본질 박힘. 다시 짜도 본질 채택은 동일. 차이는 운영급 결정 첫날 박기 + 모놀리식 페이지 회피 + 본질 X 기능 명시 보류. 학습 자산은 Houseman 진화 시점에 통합."*

— PRINCIPLES.md §원칙 5 적용 종결: *"AI 추천 vs 본인 결정 분리 추적"*. 본 회고는 본인 결정 회고.
