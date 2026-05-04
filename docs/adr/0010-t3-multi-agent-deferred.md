# ADR 0010 — T-3 Multi-Agent 보류 결정 (시나리오 A 일관성)

**상태**: **Accepted** (보류 결정 — Top 10 9.5/10 종료)
**일자**: 2026-05-05
**관련 카드**: T-3 (Multi-Agent, LangGraph supervisor + worker) — 보류
**결정 근거 (면접 답변 일관성)**: `docs/agent-capability-audit/SCENARIO.md` (시나리오 A 정의) + `docs/agent-capability-audit/PRINCIPLES.md` 원칙 5 (결정 근거 추적) + 메모리 #18 (Houseman Phase 7-12 학습 적용 통합)

---

## 컨텍스트

T-3 (Multi-Agent) 카드는 Top 10의 마지막 후보. LangGraph `Supervisor` + `Worker` 패턴으로 단일 ReAct agent(T-1b)를 다중 에이전트 분기로 확장하는 구조 — 예: `OptimizerAgent` / `RiskAgent` / `BacktestAgent` 분리 + `SupervisorAgent`가 라우팅.

3 옵션 비교:

| 옵션 | 정의 | 평가 |
|---|---|---|
| **A. 본격 PR** | T-3 본격 구현 (supervisor + 3 workers) | 시간 4-6h, 복잡도 ↑ |
| **B. Spike** | 1.5h cap PoC로 패턴 검증 후 결정 | 분량 적당, 단 시나리오 A엔 PoC도 과함 |
| **C. 보류** | 결정 자체를 ADR로 박고 트리거 명시 | **채택** — 시나리오 일관성 + 시니어 시그널 |

→ **옵션 C 채택**.

---

## 결정

**T-3 Multi-Agent 도입 보류.** 시나리오 A(기술 데모) 본질에 과한 복잡도. 보류 + 트리거 명시 + 학습 적용 통합으로 처리.

---

## 결정 근거 4종

### 1. Aether 시나리오 A 일관성

`docs/agent-capability-audit/SCENARIO.md` 시나리오 A 정의:
> *"기술 데모 — Top 10 종료 + 면접 답변 가능"*

T-3 본격 구현은 *"하면 좋아 보임"* 영역, 시나리오 A 본질 X. 실서비스 사용자 부재 상태에서 supervisor + worker 분기는 단순 ReAct 대비 가치 추가가 모호.

### 2. Houseman 동일 의사결정 (메모리 #18 인용)

Houseman 프로젝트도 Phase 7-12 진화 진입 시 *"학습 + 적용 통합"* 패턴 채택. 두 프로젝트 일관 적용 = 결정 근거 추적 시스템 정착.

### 3. 차별화 임팩트 약함

| 카드 | 차별화 강도 | 국내 도메인 사례 |
|---|---|---|
| T-2 (MCP 서버) | 강 | 거의 0건 — Anthropic 표준, Claude Desktop 즉시 호환 |
| T-6 (Qdrant 어댑터) | 강 | 운영급 마이그레이션 패턴 사례 적음 |
| **T-3 (Multi-Agent)** | **약** | LangGraph supervisor 사례 多 (튜토리얼 / 블로그 / OSS) |

T-2 + T-6 차별화로 시니어 시그널 충분. T-3은 *"누구나 가능한 기술 도입"*에 가깝다.

### 4. 단일 ReAct agent (T-1b) 충분 검증

T-1b PR #4 머지 시점에 `chat.py` 절차적 4 호출 → ReAct 1 호출 통합 + 4 도구 자율 분기 검증 완료. 시나리오 A에서 단일 ReAct로 *"모델 자율 판단 + 다단계 호출 + 디버깅 가능"* 모두 충족.

---

## 트레이드오프

- **+ 시나리오 일관성 정착** — *"박지 않은 결정 = 명시한 결정만큼 강한 시그널"* (PRINCIPLES 패턴 6)
- **+ 결정 근거 추적 시스템** — ADR + EVOLUTION + PRINCIPLES 6번 한 PR 통합
- **+ 두 프로젝트 일관 적용** (Aether ↔ Houseman, 메모리 #18)
- **− Top 10 → 9.5/10 종료** — 차별화 1건 부족이지만 T-2 + T-6으로 보완 가능

---

## 학습 처리 — 적용 통합 본질 (별도 학습 repo X)

### 학습 자료 링크 (보류 결정 시점에 박음)

- LangGraph 공식 supervisor 튜토리얼 — <https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/>
- HAMY 9 parallel agents 글 (블로그 인용)

### 학습 + 적용 통합 시점

**Houseman Phase 7-12 진화 진입 시 (메모리 #18)** — 진짜 도메인에서 학습 + 구현 동시. 별도 학습 repo 만들지 않음.

### 별도 학습 repo X 본질

| 사유 | 설명 |
|---|---|
| 가치 미흡 | Aether 기능 도출 X면 학습 자체로 의미 약함 |
| 재사용 어려움 | 적용 시점에 다시 작성해야 함 (도메인 다름) |
| 시니어 시그널 X | 별도 repo는 *"학습했다는 증거"* 일 뿐, *"적용했다는 증거"* X |

→ **시점 분리** — 학습 욕구 *"기술 때려박기 회피"* + *"코드 디테일 학습"* 두 본능을 *"진짜 적용 시점에 통합"* 으로 둘 다 만족.

---

## 진입 트리거 (보류 해제 조건)

T-3 다시 진입할 수 있는 조건:

1. **Aether가 시나리오 B (실서비스) 진입** — 사용자 1+ 명 발생 시
2. **Multi-Agent 필요성 검증** — 단일 ReAct로 처리 못 하는 도메인 케이스 발생 시
3. **Houseman Phase 7-12 진화 진입** (메모리 #18) — 진짜 도메인에서 학습 + 적용 통합

위 조건 발생 시 **T-3a / T-3b 후속 카드** 분리:
- **T-3a** — supervisor + worker 인프라 (T-1a 패턴 동일, 인프라만)
- **T-3b** — 도메인 분기 (각 worker의 도구 분리 + supervisor 라우팅 로직)

---

## 위험 시나리오

| ID | 위험 | 확률 | 완화 |
|---|---|---|---|
| R1 | Top 10 → 9.5/10 종료 = 차별화 1건 부족 | 중 | T-2 (MCP) + T-6 (Qdrant) 차별화로 충분. 면접 답변에서 *"Top 10 9.5/10 + T-3 보류 결정 = 시나리오 일관성 시그널"* 박음 |
| R2 | 학습 욕구 미충족 — *"코드 디테일 학습 못 함"* | 낮음 | Houseman Phase 7-12 진화 시점에 학습 + 적용 통합. 시점 분리로 둘 다 만족 |

---

## 롤백

본 결정 자체는 *"보류"* — 영구 거절 X. 트리거 발생 시 T-3a/T-3b 카드로 진입. ADR 0010은 그대로 유지하고 새 ADR 0011/0012로 진입 결정 + 결과 박음 (결정 추적 연속성).

---

## 참조

- `docs/agent-capability-audit/SCENARIO.md` — 시나리오 A 정의
- `docs/agent-capability-audit/PRINCIPLES.md` 패턴 6 — 박지 않은 결정 시그널
- `docs/agent-capability-audit/PRINCIPLES.md` 패턴 7 — 본질 충돌 시 두 본능 분리 검증
- `docs/agent-capability-audit/EVOLUTION.md` — Top 10 카드 회고 + T-3 보류
- `docs/adr/0002-module-boundaries.md` — `BaseAgent` 추상 (T-3 진입 시 확장 base)
- `docs/adr/0005-langgraph-adoption.md` — LangGraph 채택 결정
- `docs/adr/0006-react-pattern.md` — ReAct 패턴 채택 결정
- 메모리 #18 — Houseman Phase 7-12 학습 적용 통합
- 메모리 #20 — Top 10 종료 시 정리 약속
