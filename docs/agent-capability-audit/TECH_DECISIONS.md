# Aether 기술 선택 근거 — 면접관 *"왜 X 썼어요?"* 답할 수 있는 시스템

> Aether 프로젝트에서 사용한 핵심 기술 8개의 선택 근거 + 후보 비교 + 트레이드오프 + 면접 답변 정리.
>
> **위치**: `docs/agent-capability-audit/TECH_DECISIONS.md`
> **작성 시점**: 2026-05-04 (Top 10 8.5/10 진행 시점)
> **목적**: 면접 기술 질문 대비 + 6개월 후 본인이 *"왜 썼지?"* 답 추적 + 새 개발자 학습 자료
> **핵심 원칙**: *"Claude가 추천해서요"* 답하면 합격 시그널 0. 모든 기술은 *"무엇을 원했나 → 후보 비교 → 최종 선택 + 트레이드오프"* 답할 수 있어야 함.

---

## 📋 작성 대상 8개 기술

**1순위 (면접관 무조건 물음):**
1. ChromaDB (벡터 DB)
2. Gemini (LLM 공급자)
3. LangGraph (AI Agent 프레임워크)
4. ReAct 패턴
5. MCP (외부 도구 노출 프로토콜)

**2순위 (시니어 면접관 물음):**
6. Pydantic v2 (응답 구조화)
7. JWT HS256 (API 인증)
8. FastAPI (백엔드 프레임워크)

---

## 1️⃣ ChromaDB (벡터 DB) — RAG 핵심

### 무엇을 원했나
- 임베딩 벡터 저장 + 유사도 검색
- **로컬 개발 환경에서 빠른 프로토타이핑** (Docker 띄우자마자 작동)
- Python 친화적 API (FastAPI / LangChain 통합)
- 운영 진입 시 마이그레이션 가능 (락인 X)

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **ChromaDB** ✅ | 로컬 in-memory 즉시 작동, Python 친화, 학습 곡선 낮음 | 운영급 X (스케일 / 영속성 / 인증 약함) | **채택** (프로토타입 단계 우선) |
| Pinecone | 운영급 관리형, 글로벌 분산 | 비용 발생 (월 $70+), 락인 위험 | 비용 + 락인 거부 |
| Qdrant | 오픈소스, 운영급, Rust 기반 빠름 | 학습 곡선 (Rust 컬렉션 / 페이로드 인덱싱) | **T-6 카드로 마이그레이션 예정** (운영 진입 시) |
| Weaviate | GraphQL 지원, 모듈형 | 복잡도 ↑, 운영 부담 | 불필요한 복잡도 |
| pgvector | Postgres 통합, 익숙한 SQL | 성능 (대규모 시 한계), HNSW 인덱스 별도 설정 | 향후 검토 가능 |

### 최종 선택 + 트레이드오프
**ChromaDB.** 프로토타입 단계 우선.

인정한 약점:
- 운영 환경 영속성 약함 (in-memory 모드)
- 멀티 인스턴스 동기화 X
- 인증 / 권한 약함

→ **운영 진입 시점에 Qdrant 마이그레이션** (T-6 카드).

### 청킹 / 임베딩 / 검색 전략 (RAG 구현 디테일)

**청킹:**
- 기준: 의미 단위 (문단 + 헤더)
- 사이즈: 평균 500 토큰 (LangChain `RecursiveCharacterTextSplitter`)
- 오버랩: 50 토큰 (문맥 유지)
- 분할 우선순위: `\n\n` → `\n` → `. ` → ` ` → 글자 단위

**임베딩:**
- 모델: Gemini `text-embedding-004` (768차원)
- 호출: 배치 단위 (10개씩)
- 캐싱: Redis (동일 텍스트 재호출 방지)

**검색:**
- 거리 메트릭: Cosine similarity
- Top-K: 5
- 필터링: 메타데이터 (문서 종류 / 작성 일자)

### 면접 답변 한 줄
> *"프로토타입 단계라 ChromaDB로 빠르게 시작했고, 운영 진입 시점에 Qdrant 마이그레이션을 T-6 카드로 분리했어요. 이유는 ChromaDB가 in-memory 모드라 영속성이 약하고 멀티 인스턴스 동기화가 어려워요. Qdrant는 운영급 + 오픈소스라 락인 위험도 없고요. 청킹은 의미 단위로 평균 500 토큰 + 50 토큰 오버랩으로 분할했고 임베딩은 Gemini text-embedding-004 768차원 사용했습니다."*

### 미래 마이그레이션 계획
- **트리거:** 운영 환경 진입 또는 사용자 1만+ 도달
- **카드:** T-6
- **호환 어댑터:** ChromaDB API → Qdrant API 변환 레이어 (호출자 0 변경)

---

## 2️⃣ Gemini (LLM 공급자)

### 무엇을 원했나
- 빠른 응답 (P95 < 5초)
- **구조화 출력 강제 가능** (response_schema 지원)
- 멀티모달 (이미지 + 텍스트, 향후 확장 대비)
- 비용 효율 (개인 프로젝트 + 무료 티어)
- 한국어 자연 처리

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **Gemini 2.0 Flash** ✅ | 빠름 (P95 ~3초), response_schema 네이티브, 무료 티어 ($0/일 200 요청), 멀티모달 | 영어 외 언어 미세 차이 | **채택** |
| GPT-4o | 안정적, 구조화 출력 (JSON mode) | 비용 ($2.5/1M tokens), 응답 속도 중간 | 비용 부담 (개인 프로젝트) |
| Claude 3.5 Sonnet | 한국어 자연, 긴 컨텍스트 (200K) | API 단가 높음, response_schema 미지원 (XML로 우회) | 비용 + response_schema 부재 |
| Llama 3.3 70B (self-host) | 비용 0, 데이터 주권 | GPU 인프라 필요, 운영 부담 | 인프라 부담 |

### 최종 선택 + 트레이드오프
**Gemini 2.0 Flash.** 비용 + response_schema + 속도 3박자.

인정한 약점:
- 한국어 처리 GPT-4o 대비 약간 떨어짐
- API 안정성 (간헐적 503) — tenacity 재시도로 완화

### 면접 답변 한 줄
> *"개인 프로젝트라 비용이 우선이었고, Gemini 2.0 Flash가 무료 티어 + response_schema 네이티브 + P95 3초 이내라 선택했어요. response_schema가 핵심이었는데, GPT-4o는 JSON mode가 있고 Claude는 XML로 우회해야 해서 Pydantic 13종 모델 강제하기에 Gemini가 가장 깔끔했습니다. 한국어 처리는 GPT-4o 대비 약간 약하지만 도메인 특화 프롬프트로 보완했어요."*

### 미래 마이그레이션 계획
- **트리거:** 사용자 한국어 응답 품질 컴플레인 또는 멀티 LLM 라우팅 필요 시
- **호환 어댑터:** `llm_provider.py`에서 Gemini / GPT-4o / Claude 라우팅 가능 구조 (이미 박힘)

---

## 3️⃣ LangGraph (AI Agent 프레임워크)

### 무엇을 원했나
- AI 에이전트 다단계 호출 패턴 (Thought → Action → Observation 순환)
- **상태 관리** (이전 도구 결과를 다음 도구에 전달)
- 도구 (Tool) 추상화 + 등록 시스템
- 모델 자율 판단 (호출 순서를 사람이 정하지 않음)

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **LangGraph** ✅ | 그래프 기반 상태 관리, ReAct 즉시 사용, LangChain 호환 | LangChain 의존 (락인) | **채택** (멀티 단계 패턴 가장 깔끔) |
| LangChain (단독) | 도구 친화, 광범위 통합 | 그래프 추상화 부족, 멀티 단계 직접 구현 | 다단계 워크플로우 어려움 |
| OpenAI Function Calling | 단순, OpenAI SDK 통합 | OpenAI 락인, Gemini 호환 X | LLM 락인 |
| AutoGen | 멀티 에이전트 강력 | 복잡도 ↑, 학습 곡선 | 단일 에이전트엔 과함 |
| 자체 구현 | 락인 X, 완전 제어 | 휠 재발명, 유지보수 부담 | 시간 비용 |

### 최종 선택 + 트레이드오프
**LangGraph.** ReAct 즉시 사용 + 그래프 상태 관리.

인정한 약점:
- LangChain 의존 (마이너 버전 업그레이드 시 호환 깨짐 빈번)
- 디버깅 어려움 (그래프 내부 추적)

### 면접 답변 한 줄
> *"AI 에이전트가 도구를 자율 판단해서 호출하는 패턴을 원했고, 다단계 호출에서 상태 관리가 필요했어요. LangGraph가 그래프 기반 상태 관리 + ReAct 즉시 사용 + LangChain 도구 친화라 선택했습니다. OpenAI Function Calling도 검토했는데 OpenAI 락인이 부담돼서 피했어요. AutoGen도 봤는데 단일 에이전트에는 과해서요. T-3 카드에서 Multi-Agent로 확장 예정이고 그 때 AutoGen vs LangGraph Supervisor 패턴 재검토할 거예요."*

### 미래 마이그레이션 계획
- **트리거:** Multi-Agent 진입 (T-3 Big Bet)
- **검토:** LangGraph Supervisor 패턴 vs AutoGen 재비교

---

## 4️⃣ ReAct 패턴 (에이전트 동작 방식)

### 무엇을 원했나
- 모델이 *"어떤 도구를 어떤 순서로 호출할지"* 자율 판단
- 의존성 있는 도구 (도구 A 결과 → 도구 B 입력) 처리
- 디버깅 가능한 추론 흔적 (Thought / Action / Observation 로그)

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **ReAct** ✅ | Thought → Action → Observation 명확, LangGraph 즉시 사용, 디버깅 가능 | 매 단계 LLM 호출 (토큰 비용), 무한 루프 위험 | **채택** (디버깅 + 자율성 균형) |
| Plan-and-Execute | 1회 계획 + 일괄 실행 (토큰 절약) | 계획 단계에서 도구 결과 모름 → 잘못된 계획 시 실패 | 의존성 도구 처리 약함 |
| Function Calling (OpenAI) | LLM 단일 호출 + 도구 결과 전달 | OpenAI 락인, ReAct 만큼 자율적이지 않음 | 락인 + 자율성 부족 |
| Chain (절차적) | 단순, 예측 가능 | 사람이 순서 정함 (Aether 시작 시점 패턴) | 자율성 0 |

### 최종 선택 + 트레이드오프
**ReAct.** 자율성 + 디버깅 + 의존성 처리 균형.

인정한 약점:
- 매 단계 LLM 호출 (토큰 비용)
- 무한 루프 위험 → max_iterations=10 박음
- Plan-and-Execute 대비 결정론적 X

### Plan-and-Execute vs ReAct 트레이드오프 명확화

| 측면 | Plan-and-Execute | ReAct |
|---|---|---|
| 토큰 비용 | 낮음 (1회 계획) | 높음 (매 단계 호출) |
| 자율성 | 중 (계획 후 고정) | 강 (매 단계 재판단) |
| 디버깅 | 어려움 (계획 블랙박스) | 쉬움 (Thought 로그) |
| 의존성 처리 | 약함 (사전 계획) | 강함 (관찰 후 다음 결정) |
| 운영 안전성 | 강 (예측 가능) | 약 (무한 루프 위험) |

→ Aether는 **운영 안전성보다 자율성 + 디버깅 우선** = ReAct.
→ 무한 루프 위험은 max_iterations 박아서 차단.

### 면접 답변 한 줄
> *"포트폴리오 분석은 도구 간 의존성이 있어요 — 위험 분석 결과를 보고 추천을 하는 식이라. Plan-and-Execute는 사전 계획이라 도구 결과를 모르고, Chain은 사람이 순서 박아야 해서요. ReAct가 Thought → Action → Observation 순환으로 매 단계 재판단하니까 의존성 처리에 강하고 디버깅도 가능했어요. 토큰 비용이 높지만 max_iterations 10으로 무한 루프 차단했고 환경변수로 절차적 호출 fallback도 보존했습니다."*

### 미래 마이그레이션 계획
- **트리거:** 토큰 비용 운영 부담 발생 시
- **검토:** Plan-and-Execute 하이브리드 (간단 작업은 Plan, 복잡 작업은 ReAct)

---

## 5️⃣ MCP (Model Context Protocol)

### 무엇을 원했나
- Aether 4 도구를 외부 LLM (Claude Desktop / Cursor / 외부 LangChain 에이전트)이 호출 가능하게
- **표준 프로토콜** (한 번 박으면 여러 클라이언트 호환)
- 실시간 통신 (양방향)
- LangChain `args_schema`와 자연 호환

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **MCP (stdio)** ✅ | Anthropic 표준, Claude Desktop 즉시 호환, args_schema → inputSchema 1:1, 인증 X (subprocess) | 신생 프로토콜 (1.27.0 안정 단계), HTTP 전송 별도 | **채택** (차별화) |
| REST API | 익숙, 광범위 통합 | 도구 정의 표준 X (커스텀 schema), 외부 LLM 통합 시 어댑터 필요 | 표준 부재 |
| gRPC | 빠름, 강 타입 | 학습 곡선, 외부 LLM 통합 표준 X | 통합 표준 부재 |
| WebSocket | 양방향, 실시간 | 도구 정의 표준 X | 표준 부재 |
| OpenAPI Function | 표준 OpenAPI, OpenAI 호환 | OpenAI 락인 | 락인 |

### 최종 선택 + 트레이드오프
**MCP (stdio transport).** Anthropic 표준 + Claude Desktop 호환 + 1:1 매핑.

인정한 약점:
- 신생 프로토콜 (1.x 안정 단계, 변화 가능성)
- stdio = 로컬 subprocess만 (원격 호출 불가)
- 운영급 인증 X (subprocess launch = 운영자 신뢰)

### 면접 답변 한 줄
> *"Aether 도구를 외부 LLM이 호출 가능하게 하고 싶었는데, REST는 도구 정의 표준이 없어서 매 클라이언트마다 어댑터 박아야 했어요. MCP가 Anthropic이 만든 LLM 도구 통합 표준이고 Claude Desktop / Cursor가 즉시 호환돼서 선택했어요. 무엇보다 LangChain args_schema를 MCP inputSchema로 1:1 매핑해서 어댑터 0줄로 박을 수 있었던 게 결정적이었어요. stdio transport라 원격 호출 불가하지만 운영 진입 시 HTTP/SSE transport 후속 카드로 분리했고요. 국내 도메인 MCP 서버 사례가 거의 없어서 차별화 포인트로도 강해요."*

### 미래 마이그레이션 계획
- **트리거:** 원격 호출 / 다중 클라이언트 동시 접속 필요 시
- **카드:** T-2c (HTTP/SSE transport 추가)

---

## 6️⃣ Pydantic v2 (응답 구조화)

### 무엇을 원했나
- LLM 응답 형식 강제 (JSON 깨짐 사고 0)
- 타입 안전성 (런타임 검증)
- Gemini `response_schema` 호환
- FastAPI 통합 (Request/Response 모델)

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **Pydantic v2** ✅ | Rust 기반 빠름, FastAPI 네이티브, Gemini response_schema 호환, JSON Schema 자동 생성 | 학습 곡선 (v1 → v2 차이) | **채택** |
| Pydantic v1 | 광범위 사용 | 느림 (Python 구현), v2가 더 빠름 | 성능 |
| Marshmallow | 광범위, 검증 로직 풍부 | FastAPI 통합 약함, JSON Schema 자동 생성 X | 통합 약함 |
| dataclass | 표준 라이브러리, 단순 | 검증 X, JSON Schema 수동 작성 | 검증 부재 |
| attrs | 강력한 검증 | FastAPI 미통합 | 통합 부재 |

### 최종 선택 + 트레이드오프
**Pydantic v2.** FastAPI + Gemini + 성능 3박자.

인정한 약점:
- v1 → v2 마이그레이션 학습 곡선
- 일부 라이브러리 (LangChain) v1 호환만

### 13종 모델 설계 의도
- 응답마다 별도 모델 (재사용보다 명확성 우선)
- BaseModel 상속 + Field description (자동 JSON Schema 생성)
- ValidationError 시 tenacity 재시도

### 면접 답변 한 줄
> *"LLM 응답이 가끔 JSON 깨져서 화면 사고가 났어요. Pydantic v2가 FastAPI 네이티브 + Gemini response_schema 호환 + Rust 기반이라 빠르기까지 해서 선택했어요. 13종 응답 모델 만들어서 Gemini에게 schema 강제했고 ValidationError 발생 시 tenacity로 max 3회 재시도 박았어요. v1 → v2 마이그레이션 학습 곡선이 있었지만 BaseModel 상속 + Field description으로 JSON Schema 자동 생성되는 게 컸어요."*

---

## 7️⃣ JWT HS256 (API 인증)

### 무엇을 원했나
- 인증된 사용자만 API 호출 (운영 진입 가능)
- **Stateless** (DB 조회 없이 검증)
- 다중 서비스 (frontend / llm / portfolio) 공통 인증
- 빠른 검증 (낮은 지연)

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **JWT HS256** ✅ | Stateless, 빠른 검증 (대칭 키), 다중 서비스 공유 쉬움 | 키 노출 시 전체 위험, 토큰 무효화 어려움 | **채택** (프로토타입 단계) |
| JWT RS256 | 비대칭 키 (공개키 검증), 키 분리 | 검증 느림 (RSA), 키 관리 복잡 | 운영 진입 시 검토 |
| OAuth2 + Session | 표준, 토큰 무효화 가능 | DB 조회 (Stateful), 인프라 부담 | 인프라 부담 |
| API Key | 단순 | 사용자 식별 X, 권한 관리 약함 | 다중 사용자 부적합 |

### 최종 선택 + 트레이드오프
**JWT HS256.** 프로토타입 단계 단순함 우선.

인정한 약점:
- 대칭 키 노출 시 전체 위험 (auth-service 키 = llm/portfolio 검증 키 동일)
- 토큰 만료 전 무효화 어려움
- 다중 서비스 = 같은 secret 공유 (보안 위험)

→ **운영 진입 시 RS256 전환** (ADR 0004 트리거 명시).

### 면접 답변 한 줄
> *"개인 프로젝트 + 다중 서비스라 Stateless 인증이 필요했어요. JWT HS256이 대칭 키라 검증 빠르고 frontend / llm / portfolio 서비스가 같은 키로 검증 가능해서 단순했어요. 단점은 키 노출 시 전체 위험 + 토큰 무효화 어려움이라 운영 진입 시점에 RS256 (비대칭 키, 공개키 검증) 전환을 ADR 0004에 트리거 명시했어요. 외부 IDP 연동 시점이나 다중 서비스 키 분리 필요 시 진행할 거예요."*

---

## 8️⃣ FastAPI (백엔드 프레임워크)

### 무엇을 원했나
- 비동기 (LLM 호출 동시 처리)
- Pydantic 네이티브 (Request/Response 모델 자동 검증)
- 자동 OpenAPI 문서 (Swagger UI)
- 빠른 개발 속도

### 후보 비교

| 후보 | 장점 | 단점 | 거절 사유 |
|---|---|---|---|
| **FastAPI** ✅ | 비동기 네이티브, Pydantic 통합, 자동 OpenAPI, 학습 곡선 낮음 | 마이너 버전 호환성 변동 | **채택** |
| Flask | 광범위, 익숙, 가벼움 | 비동기 X (또는 별도 설정), Pydantic 미통합 | 비동기 부재 |
| Django | 풀스택, ORM 통합 | 무거움, 비동기 약함 | 과함 + 비동기 약함 |
| Starlette | FastAPI 베이스, 가벼움 | Pydantic 통합 직접 박아야 함 | 통합 부재 |
| Tornado | 비동기 강 | 학습 곡선, 생태계 약함 | 생태계 |

### 최종 선택 + 트레이드오프
**FastAPI.** 비동기 + Pydantic + 자동 문서 3박자.

인정한 약점:
- 마이너 버전 호환성 변동 (T-2 본격 PR Blocked 사례)
- 0.x 버전대 (1.0 미출시)

### 면접 답변 한 줄
> *"LLM 호출이 비동기여야 했고 Pydantic 응답 모델 13종 강제하려면 네이티브 통합이 필수였어요. FastAPI가 비동기 네이티브 + Pydantic 통합 + 자동 OpenAPI 문서까지 박혀있어서 선택했어요. Flask도 검토했는데 비동기가 별도 설정이라 부담됐고 Django는 LLM 서비스에는 과했어요. 단점은 마이너 버전 호환성이 약하다는 거고 실제로 T-2 본격 PR에서 0.104.1 vs 0.115+ 충돌이 났어요. 그 사례를 WORK_PATTERNS 문제 18로 박아서 다음부터는 pip install --dry-run으로 사전 차단합니다."*

---

## 🎯 종합 — 면접 30초 요약

면접관 *"Aether에서 어떤 기술 썼어요?"* 첫 질문 시:

> *"백엔드는 FastAPI (비동기 + Pydantic 통합), LLM은 Gemini 2.0 Flash (response_schema 네이티브), 에이전트는 LangGraph (ReAct 패턴), 벡터 DB는 ChromaDB (프로토타입 단계, 운영 진입 시 Qdrant 마이그레이션 예정), 외부 도구 노출은 MCP 표준 프로토콜 (Anthropic, Claude Desktop 호환), 인증은 JWT HS256 (운영 진입 시 RS256 전환)이에요. 모든 기술 선택에 후보 비교 + 거절 사유 + 마이그레이션 트리거를 ADR로 박아뒀어요."*

→ 면접관 *"왜 X 썼어요?"* 추가 질문 시 → 본 문서 해당 섹션 그대로 답.

---

## 📋 갱신 이력

| 일자 | 갱신 내용 | 갱신 사유 |
|---|---|---|
| 2026-05-04 | 최초 작성 — 8개 기술 (1순위 5 + 2순위 3) | Top 10 8.5/10 진행 시점 정리 |

**다음 갱신 예정:**
- T-6 머지 후: ChromaDB → Qdrant 마이그레이션 사례 + Qdrant 결정 근거 추가
- T-3 머지 후: Multi-Agent 패턴 (Supervisor / Hierarchical) 결정 근거 추가
- 신규 기술 도입 시마다 즉시 추가

---

## 🔮 6개월 후 본인이 봤을 때

이 문서가 답하는 질문:

- *"왜 ChromaDB 썼지?"* → 1순위 1번
- *"청킹 어떻게 했지?"* → 1순위 1번 청킹 / 임베딩 / 검색 섹션
- *"왜 Gemini?"* → 1순위 2번
- *"왜 LangGraph?"* → 1순위 3번
- *"ReAct vs Plan-and-Execute 차이?"* → 1순위 4번 트레이드오프 명확화
- *"MCP가 뭐야?"* → 1순위 5번
- *"Pydantic v1 v2 왜 v2?"* → 2순위 6번
- *"JWT HS256 vs RS256?"* → 2순위 7번
- *"FastAPI vs Flask?"* → 2순위 8번

→ **모든 기술 결정에 답 가능. *"Claude가 추천해서요"* 답할 일 0.**

---

## 💬 진짜 본질

기술 면접에서 *"왜 X 썼어요?"* 질문은 단순히 기술 자체를 묻는 게 아님.

**실제 묻는 것:**
1. *"이 사람 결정 근거가 있나? 아니면 추천받은 거 그대로?"*
2. *"트레이드오프 인지하나? 약점 알면서도 선택했나?"*
3. *"마이그레이션 계획 있나? 운영 진입 시 어떻게 할 건가?"*

→ 이 3개 답할 수 있는 게 **시니어 시그널.**

본 문서는 8개 기술 모두에 대해 이 3개 답할 수 있도록 박힘.

> *"무엇을 썼나"* 만큼 *"왜 안 썼나 + 트레이드오프 + 마이그레이션"* 답할 수 있는 게 본질.
