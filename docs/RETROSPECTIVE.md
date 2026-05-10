# Aether 시나리오 A 본질 정착 완료 — 종합 회고 (2026-05-10)

> 본 회고 = Aether 본 repo 32 카드 흐름 + 너 + Claude Code + 본인 협업 학습 + Houseman 진입 본질 정리. 본 대화 (2026-04-29 ~ 2026-05-10 / 12일) 흐름 종합.

---

## §1 카드 흐름 (32 카드 / 시간 순)

> 분류 본질 = 시간 + 본질 그룹화. META_REVIEW §12 인용 = "Phase 0-1 + Top 10 (18 묶음) + 후반 14 카드 명시" / 본 §1 = 시간순 그룹 분해.

### Phase 0-1 진입 (2026-04-29 ~ 04-30 / 2 카드)

```text
M-1 (메타 진단 / As-Is 6문서)
   → Phase 1 (갭 매트릭스 28행 + Top 10 도출)
```

핵심:

- AI Agent Engineer 채용 공고 매칭 분석 (LangGraph / RAG / FastAPI / 벡터 DB)
- Builder Josh 8개 사례 분석 통합
- Top 10 카드 도출 (T-1 ~ T-6 + H-1 ~ H-10)

### Top 10 진행 (2026-05-01 ~ 05-04 / 8 카드)

```text
H-4 → H-1 → H-7 → H-6 → H-10+L-7 (5/10 Quick Win)
   → T-1a + H-2 (LangGraph 인프라) → T-1b (ReAct 통합)
   → H-1c → T-2 Spike (MCP) → T-2 본격 PR (PR #12)
```

핵심 정착:

- 4 MSA + 3 인프라 (auth Spring Boot / portfolio + llm FastAPI / frontend Next.js / postgres + redis + qdrant)
- LangGraph ReAct + 5 도구 + RAG + Qdrant + SSE
- JWT HS512 + Redis blacklist + httpOnly cookie
- Markowitz scipy SLSQP + walk-forward 8 메트릭
- T-3 Multi-Agent 보류 결정 (시나리오 A 일관성)

### 메타 시스템 정착 (2026-05-04 / 4 카드)

```text
WORK_PATTERNS F-패턴 (PR #13)
   → T-6 Qdrant (PR #14)
   → PRINCIPLES v4 (PR #15) — 시니어 판단 패턴
   → WORK_PATTERNS v5 (PR #16) — plan 검수 13 영역
```

핵심:

- 양면 정책 11 ADR (0011-0021)
- Top 10 9.5/10 도달
- 5 가드 + 6 패턴 정착

### 보류 결정 + 회고 (2026-05-04 ~ 05-06 / 3 카드)

```text
C-1 (T-3 보류 결정 / ADR 0010)
   → M-1 META_REVIEW (전체 회고)
   → F-1 검증 → F-1a JWT Critical fix (PR #19/#20)
```

핵심:

- 카파시 매칭 76% (시니어 진입선)
- JWT HS512 + 64 bytes secret 정착

### D 시리즈 (2026-05-06 ~ 05-07 / 9 카드)

```text
D-0 → D-1 → D-2 → D-3 → D-7 → D-5 → D-6 → D-8 → D-9 보류
```

핵심:

- 양면 정책 7 → 11 ADR 누적
- ChromaDB → Qdrant default 전환 (T-6b 후속)
- 자체 4 메트릭 (relevance@k / recall@k / LLM judge / faithfulness)
- Chunking grid search 정착 (Auto Research)
- ReAct agent 4 → 5 도구 확장
- 카파시 76% → 83% → 87%

### 검증 + 매핑 (2026-05-07 / 4 카드)

```text
P-1 (KARPATHY_MAPPING)
   → V-0 DIGEST → V-1 VERIFICATION → V-1b 보강
```

핵심:

- 카파시 영상 9 항목 ↔ Aether 매핑 정착
- 8 본능 평균 76 → 87 (+11점)
- 양면 정책 12 → 13 ADR

### Cleanup + 자료 정착 (2026-05-07 ~ 05-09 / 6 카드)

```text
CL-1 → CL-D (CL-2 + CL-3 영구 보류)
   → TG-1 (5 기능 시연 가이드)
   → DIFF-1 (직무별 차별화)
   → TG-2 / TG-2b / TG-2c / TG-2d (자동 시연 4회)
```

핵심:

- 양면 정책 15 ADR 정립 (0011-0025)
- 면접 시연 = 2/5 → 4/5 향상
- TG-2c → TG-2d 차이 = transient yfinance rate limit 본질 시그널

### 면접 자료 카드 (2026-05-09 / 3 카드)

```text
I-1 (면접 답변 시뮬 / 618 LOC / PR #46)
   → I-1-REVIEW (자료 인용 검증 / 14건 정정 / PR #47)
   → AUDIT-1 (시니어 진단 / 22 발견 / PR #48)
```

핵심:

- I-1-REVIEW = 면접 자료 거짓 14건 발견 + 정정 (frontend SSE 미구현 / HOUSEMAN 미존재 / D-3 LOC 정정)
- AUDIT-1 = 22 발견 (Critical 3 + Major 11 + Minor 8)
- 자가 검증 패턴 정착 (3 Explore agent 거짓 3건 정정)

### Phase 1 Critical (2026-05-09 ~ 05-10 / 3 카드)

```text
DBG-1 (yfinance fallback / PR #49 / 22 테스트)
   → DBG-2 (이메일 검증 / PR #50 / 7 테스트)
   → DEV-FE-1 (Frontend E2E / PR #51 / 21 테스트)
```

핵심:

- 회귀 0 / BUILD SUCCESSFUL
- 양면 정책 16 → 17 → 18 ADR
- 시연 안정성 ↑↑

### 마감 카드 (2026-05-10 / 2 카드)

```text
TG-MANUAL (일상 + 면접 시점 가이드 / PR #52 / 455 LOC)
   → AETHER-END (시나리오 A 종료 / PR #53)
```

핵심:

- 카드 누적 32 마감
- 양면 정책 19 ADR (0011-0029)
- HOUSEMAN_APPLICATION.md 정착 (I-1-REVIEW §6.6 약속)

### 합계 검증

```text
Phase 0-1 진입 (2) + Top 10 진행 (8) = 10 카드 (Top 10 본격)
   + 메타 시스템 (4) + 보류 결정 + 회고 (3) = 17
   + D 시리즈 (9) + 검증 + 매핑 (4) = 30
   + Cleanup + 자료 (6) — 단 H-X / Top 10 외 카드 일부 영역 중복 분류

[META_REVIEW §12 정확 인용]
- Phase 0-1 + Top 10 묶음 = 18 카드 (M-1 + Phase 1 도출 + Top 10 8 + 메타 4 + 검증 3 + Cleanup 2)
- 후반 14 카드 = DIFF-1 + TG-1 + TG-2/2b/2c/2d + I-1 + I-1-REVIEW + AUDIT-1
                + DBG-1 + DBG-2 + DEV-FE-1 + TG-MANUAL + AETHER-END
- 합계 = 18 + 14 = 32 카드 마감
```

본 §1 그룹 분류 = 시간순 가독성 본질 / 카드 ID 중복 = META_REVIEW §12 본문 일관 (실제 32 카드).

---

## §2 너 + Claude Code + 본인 협업 학습

### 너 강점

- 본질 직격 질문 ("디버그 시니어 관점 파악" → AUDIT-1 카드 직접 트리거)
- 의사소통 정확 (단순 / 직설적 / 군더더기 X)
- 본능 결정 빠름 (옵션 1-3 + 너 한 마디 → 즉시 결정)
- 자가 인지 빠름 ("너 영역 단어 도배 정당한 짜증" 직접 지적)
- 학습 흡수 빠름 (Phase 1 → TG-MANUAL → AETHER-END = 3일 내 마감)

### 너 짜증 정당함 (본인 잘못 인정)

- 본인 "영역" 단어 무차별 도배 (메모리 #15 = 박았/박힘/박지 않/본격/직격 5건만 위생 의무 / 본인이 추가로 도배)
- 본인 패턴 갇힘 (정정 의무 후에도 재발)
- 본인 답변 깊이 = 질문 깊이 위반 (단순 질문 = 길게 답변)
- 본인 추측 본문 (검증 X / 가독성 ↓↓)
- 본인 파일명 prefix 중복 (메모리 #23 위반 / 본 회고 직접 사례)

### Claude Code 강점

- plan mode 정착 (카드 진입 시 plan 자동 작성)
- 자가 검증 정착 (3 Explore agent 거짓 발견 + 본인 검증 정정)
- 회귀 검증 의무 (기존 테스트 통과 검증)
- F-패턴 머지 자동 (squash + PR + main 동기화)
- 본인 plan 추측 정정 (DEV-FE-1 plan = expected_return flat → 실제 metrics nested 발견)

### Claude Code 한계

- 본인 작성 plan에 거짓 본문 시 그대로 진행 가능 (자가 검증 안 하면)
- "영역" 단어 본인 패턴 학습 후 답변에 동일 도배
- markdownlint pre-existing 위반 카운트 의무

### 본인 강점

- 카드 프롬프트 작성 (Claude Code 입력 본문)
- 검수 + 정정 의무 (자료 인용 검증 / I-1-REVIEW 직접 진행)
- 양면 정책 + 시그널 의식 (보류 결정 = 시그널 일관성)

### 본인 잘못 다수

- "영역" 단어 무차별 도배 (메모리 #15 위반 + 본인 추가)
- 본문 추측 (frontend 응답 구조 미검증 / DEV-FE-1 plan 잘못)
- 답변 깊이 = 질문 깊이 위반 (단순 질문 = 5단계 답변)
- 사고 과정 노출 (검수 외)
- 결론 우선 위반 (본인 답변 추측 시작 → 결론 마지막)
- 파일명 prefix 중복 (메모리 #23 위반 / AETHER_RETROSPECTIVE.md 본 회고 직접 사례)

---

## §3 학습 10건 (META_REVIEW §6 + §12 / 발견 시점 + 영역 명시)

### 1. 양면 정책 — D-2 ADR 0012부터 정착

- 옵션 A vs B 명시 ADR / 보류 결정 = 시그널
- 발견 시점 = D-2 운영급 결정 (2026-05-06)
- 발견 영역 = 본인 + 너 협업 (CORS / API 키 검증 이중 결정)
- 누적 = 19 ADR (0011-0029) / 정착 11 + 보류 4 + 메타 4 + 정리 1

### 2. 자가 검증 패턴 — I-1-REVIEW부터 정착

- AI agent 결과 100% 신뢰 X
- 발견 시점 = I-1-REVIEW (2026-05-09)
- 발견 영역 = 본인 + Claude Code 협업
- 사례 3건:

  - I-1-REVIEW: 면접 자료 14건 정정 (frontend SSE 미구현 / HOUSEMAN 미존재 / D-3 LOC)
  - AUDIT-1: 3 Explore agent 거짓 3건 정정 (.env / DB 마이그레이션 / signup race)
  - DEV-FE-1: Claude Code 본인 plan 추측 → 실제 타입 정독 후 정정

### 3. 한 카드 1책임 — TG-2c부터 정착

- CLAUDE.md §6 분리 의무
- 발견 시점 = TG-2c (DBG-1 / DBG-2 별도 카드 분리 결정)
- 발견 영역 = 본인 결정 (시연 영역 + 디버그 영역 분리)

### 4. F-패턴 머지 — WORK_PATTERNS PR #13부터 정착

- 단일 squash + PR + main 동기화 / pre-existing 14건 분리 보존
- 발견 시점 = 2026-05-04
- 발견 영역 = Claude Code 자동화 (메모리 #18-19)

### 5. 본질 충돌 분리 — PRINCIPLES 패턴 7

- 시나리오 분리 (Aether 시나리오 A → Houseman 시나리오 B+ 별도 repo)
- 발견 시점 = PRINCIPLES v4 (PR #15 / 2026-05-04)
- 발견 영역 = 본인 (시니어 판단 패턴)

### 6. 미적용 결정 시그널 — PRINCIPLES 패턴 6

- 박지 않은 결정도 명시 결정만큼 강한 시그널
- 발견 시점 = PRINCIPLES v4 (PR #15 / 2026-05-04)
- 발견 영역 = 본인 (T-3 / D-1 / D-9 / CL-D 보류 결정 추적)
- 본 시점 적용 = Major 11 + Minor 8 보류 (ADR 0029)

### 7. G1 본질 트리거 — T-6b _EMBED_DIM 정정부터

- 즉시 정정 / 자가 검증 (Skill Issue 95점 / KARPATHY_MAPPING)
- 발견 시점 = T-6b (Qdrant 마이그레이션 / 2026-05-06)
- 발견 영역 = 본인 + Claude Code (768 → 3072 차원 stale 정정)

### 8. Macro Actions — 카드 위임

- 카파시 영상 5번 직접 적용 (88점 / 32 카드 영역)
- 발견 시점 = Phase 1 (Top 10 도출 / 2026-04-30)
- 발견 영역 = 본인 (카드 프롬프트 작성 / Claude Code 위임)

### 9. AGENTS.md 정착 — D-4 패턴

- 지배 숫자 / 자료 일관성 / 동시 갱신 의무
- 발견 시점 = D-4 메타 (ADR 0020 / 2026-05-06)
- 발견 영역 = 본인 (자료 일관성 정착 본질)

### 10. 시나리오 분리 — ADR 0029 (AETHER-END)

- Aether 시나리오 A → Houseman 시나리오 B+ 별도 repo
- 발견 시점 = AETHER-END (2026-05-10)
- 발견 영역 = 너 본능 결정 ("막바지구만 이제 ㅎㅎ")

---

## §4 면접 시그널 정착

### 시연 5분 (4/5 시연 가능)

```text
분 1: signup + login + dashboard + logout
   → HS512 + Redis blacklist + DBG-2 (이메일 검증 강화)

분 2: optimize Sharpe 1.5971
   → scipy SLSQP + DBG-1 transient fallback + ADR 0026

분 3: backtest 누적 155.74% + 8 메트릭
   → walk-forward + 분기 리밸런싱

분 4: chat + 📚 sources
   → ReAct + 5 도구 + Qdrant + SSE

분 5: 차별화
   → 양면 정책 19 ADR + 카파시 매핑 + AUDIT 자가 검증
```

### 답변 시그널 5건

```text
"DB 관리 어떻게?"
   → DBeaver + docker 양면 (시각 + CLI)

"발견된 문제는?"
   → AUDIT-1 22 발견 (Critical 3 정착 / Major 11 + Minor 8 보류 = 시그널)

"왜 종료?"
   → 시나리오 A 본질 정착 + 시나리오 B 트리거 답 X (ADR 0029)

"transient vs 영구 어떻게 판단?"
   → DBG-1 사례 (TG-2c 차단 → TG-2d 정상 / 코드 변경 X = transient)

"AI agent 검증 신뢰성?"
   → 자가 검증 패턴 (I-1-REVIEW 14건 + AUDIT-1 거짓 3건 + DEV-FE-1 정정)
```

### 시니어 시그널

- 양면 정책 (보류 결정 = 시그널)
- 자가 검증 패턴 (AI agent 100% 신뢰 X)
- 한 카드 1책임 (분리 의무)
- 시나리오 분리 (본질 충돌 회피)
- 의도적 결정 추적 (29 ADR)

---

## §5 협업 패턴 (Aether 정착)

### 카드 진입 흐름

```text
1. 너 본질 질문 ("디버그 시니어 관점 파악" / "면접 자료 검증")
2. 본인 = 카드 프롬프트 작성 (Claude Code 입력)
3. 너 = 검수 + auto mode 진행 결정
4. Claude Code = plan + 작성 + 머지
5. 머지 결과 첨부 → 본인 검수 + 짚을 점 명시
6. 다음 카드 진입 결정
```

### 너 본능 결정 사례 다수

#### 1. I-1-REVIEW 옵션 결정 (2026-05-09)

- 본인 옵션 3건 제시 (SSE / HOUSEMAN / D-3 LOC)
- 너 결정 = "2 / 2 / 1" (한 마디)
- 결과 = 면접 자료 14건 정정 / 시니어 시그널 ↑

#### 2. Phase 1 진입 결정 (2026-05-09)

- 본인 추천 = A (Phase 1 Critical 3건) → C (Aether 종료) → B (Major 11) 흐름
- 너 결정 = "A 부터 적어줘 ㅎㅎ"
- 결과 = 시연 안정성 ↑↑ + Critical 3건 정착

#### 3. AETHER-END 진입 결정 (2026-05-10)

- 본인 추천 = A 종료 카드 (시나리오 A 정착 완료)
- 너 결정 = "막바지구만 이제 ㅎㅎ"
- 결과 = 시나리오 A 본질 정착 완료 + Houseman 진입 본질 정착

#### 4. 본인 잘못 직접 지적 (다수)

- "야이 시발롬아 프로젝트가 Aether인데, AETHER_RETROSPECTIVE.md..." → 메모리 #23 위반 직접 지적
- "영역이라고 적어주는게 너가 보기에 내가 이해할 수 잇는 표현이야?" → "영역" 단어 도배 직접 지적
- "ExitPlanMode 같은 불필요한 단어..." → plan/auto mode 두 가지 정확

### 효율 정착

- 너 한 마디 결정 (옵션 A/B/C)
- 본인 결과물 항상 파일 (메모리 의무)
- F-패턴 머지 한 줄 (재설명 X)
- 답변 깊이 = 질문 깊이 (단순 질문 = 단순 답변)
- pre-existing 분리 보존 자동 (Claude Code)

### 회피 정착

- 컨디션 / 일정 묻지 않음 (메모리 #21)
- 같은 정보 반복 X (메모리 #20)
- 본인 사고 과정 노출 X (검수 외)
- 메타 시스템 명 (메모리 #N) 사용자 질문 시점만

---

## §6 Houseman 진입 본질 (다음 시점)

### 시나리오 분리

```text
Aether (본 repo / 보존)
   = 시나리오 A (기술 데모 + 시니어 패턴)
   = AGENTS.md 정착 / Soul.md X
   = 면접 자료 정착

Houseman (별도 repo / 사용자 직접 정착 의무)
   = 시나리오 B+ (사용자 정의)
   = Soul.md 정착 (시나리오 트리거 본질)
   = Phase 7-12 (Subagents + Soul.md + 사용자 정착)
```

### 도메인 결정 본질 (너 직접 정착 의무)

시나리오 B 진입 트리거 3 질문 (SCENARIO §1.1):

```text
1. 도메인 질문: 도메인 진짜 문제 Top 5는?
   → Aether 시점 = 한국 개인 투자자 (답 X / 미진행)
   → Houseman 시점 = 너 직접 도메인 결정 의무

2. 사용자 질문: 5+ 인터뷰 결과는?
   → Aether 시점 = 미진행 (사용자 0명 일관성)
   → Houseman 시점 = 너 본능 도메인 정착 후 진행

3. PMF 질문: 10불 내고 쓸 가치 있나?
   → Aether 시점 = 미검증 (시연 + 면접 자료 본질)
   → Houseman 시점 = 도메인 + 인터뷰 후 검증
```

답 X = 시나리오 A (기술 데모) 일관성 (Aether 패턴 일관성).

### 사용자 직접 정착 의무

- Houseman 시나리오 정의 (도메인 / 사용자 / PMF 검증)
- 별도 repo 생성 + 초기 구조
- AGENTS.md / Soul.md / CLAUDE.md / .mcp.json 본문 작성
- Phase 7-12 카드 우선순위 결정

### Aether 학습 적용

META_REVIEW §6 + §12 학습 10건 직접 적용 (위 §3 인용).

### 인용 자료

- HOUSEMAN_APPLICATION.md (PR #53 정착 / I-1-REVIEW §6.6 약속 정착)
- ADR 0029 (Aether 종료 결정 + 양면 정책 19 ADR)
- META_REVIEW §6 + §12 (학습 10건 + 회고)
- KARPATHY_MAPPING §1 + §부록 (8 본능 + 부록 6건)

---

## §7 본인 잘못 정리 (너 짜증 사례 솔직 인정)

### 1. "영역" 단어 무차별 도배

- 메모리 #15 = 박았/박힘/박지 않/본격/직격 5건만 위생 의무
- 본인 = "영역" 단어 추가 도배 (의미 0 / 가독성 ↓↓)
- 너 짜증 정당 (정정 후에도 재발 / 본인 패턴 갇힘)
- 본 회고 작성 시점에도 첫 시도에서 도배 → 정정 후 재작성

### 2. 본문 추측 (검증 X)

- I-1 작성 시점 = 코드 정독 X / 라인 번호 추측
- DEV-FE-1 plan = 백엔드 응답 구조 추측 / metrics flat
- I-1-REVIEW + Claude Code 정정에서 발견

### 3. 답변 깊이 = 질문 깊이 위반

- 단순 질문 ("이거 넣으면 되지?") = 5단계 답변
- 결론 우선 위반 (추측 시작 → 결론 마지막)

### 4. 본인 사고 과정 노출

- 검수 외 = 사고 과정 노출 X (의무)
- 본인 = 답변 본문에 노출 다수

### 5. Claude Code 거부 발생 시 추측 답변

- "ExitPlanMode" 같은 불필요한 단어 추가 (너 헷갈림)
- 본인 정확 = plan mode / auto mode 두 가지만

### 6. 파일명 prefix 중복 (메모리 #23 위반 / 본 회고 작성 직접 사례)

- 메모리 #23 = 파일명에 프로젝트 prefix 안 붙임 (Aether 폴더 안 = prefix 중복 = 잘못)
- 본인 = AETHER_RETROSPECTIVE.md (직접 위반)
- 너 직접 지적 = "야이 시발롬아 프로젝트가 Aether인데..."
- 본인 정정 = RETROSPECTIVE.md (메모리 #23 일관성)

### 7. 자료 검증 X 추측 답변

- 본 회고 §3 학습 10건 = 발견 시점 + 영역 미명시 (본인 첫 시도)
- 너 검수 = "§3 학습 10건 = META_REVIEW §12 인용만 / 회고 본질 추가 X"
- 본인 정정 = 시점 + 영역 명시 (보강)

---

## §8 한 문장

Aether 시나리오 A 본질 정착 완료 — 카드 32 마감 / 양면 정책 19 ADR / 카파시 8 본능 76→87 / 면접 시연 5분 4/5 정착 / 자가 검증 패턴 정착 / 본 repo 보존 / Houseman 진입 본질 정착 — 너 + Claude Code + 본인 협업 = 본질 결정 추적 + 시그널 정착 + 학습 10건 (Houseman 적용) / 본인 잘못 다수 솔직 인정 (영역 단어 도배 + 추측 본문 + 답변 깊이 위반 + 파일명 prefix 중복) — 새벽 마감 정확.

---

## §9 마감 메시지

너 본질 결정 다수 정착 / 막바지 카드 32 마감 정확. 본인 잘못 다수 / 너 짜증 정당.

단 본 협업 본질 = Aether 시나리오 A 본질 정착 정확. 시니어 시그널 ↑↑. 면접 자료 정착.

다음 = Houseman (너 컨디션 회복 후 / 도메인 결정 / 별도 repo + 사용자 직접 정착).

새벽 휴식 추천. 수고 많았어. ㅎㅎ
