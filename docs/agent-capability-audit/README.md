# agent-capability-audit/ 자료 인덱스 (CL-1)

> **본질**: M-1 ~ V-1b 18 카드 작업 자료 + Phase 1-2 사전 분석 자료. audit 폴더 22건 정착 + phase3/ 폴더 11건 카드 본문 = 6개월 후 다른 개발자가 작업 흐름 인지 가능 정착.
> **카드**: CL-1 (자료 인덱스 / ADR 0024)
> **갱신일**: 2026-05-07
> **자료 합산**: 8,101 LOC (정착 14 + pre-existing 8) + phase3/ 11건

---

## §1 audit 자료 본질

3 영역 통합:

1. **작업 회고 + 검증 + 시니어 본질** (정착 14건) — M-1 ~ V-1b 카드 산출물 (META_REVIEW / WORK_PATTERNS / PRINCIPLES / KARPATHY 등)
2. **Phase 1-2 사전 분석** (pre-existing 6건) — 01_architecture ~ 06_api_reliability (Aether 시작 시점 As-Is 진단)
3. **카드 본문** (phase3/ 폴더 11건) — Top 10 카드 마스터 로드맵 + 10 카드 디테일

**인용 흐름 영역** (TG-1 신규 / 본 자료 ↔ root TEST_GUIDE):
- VERIFICATION.md §0 (진단 5 절차) → docs/TEST_GUIDE.md §3 인용
- VERIFICATION.md §11 (검증용 user / id=4) → docs/TEST_GUIDE.md §1.4 인용
- META_REVIEW.md §9 (면접 시연 5분) → docs/TEST_GUIDE.md §4 인용
- AUDIT.md (D-4 / 14 카드 종합) → docs/TEST_GUIDE.md §4.2 차별화 영역 인용

---

## §2 정착 자료 14건 디테일

| # | 자료 | LOC | 카드 | 본질 |
|---|------|-----|------|------|
| 1 | [DIGEST.md](DIGEST.md) | 812 | V-0 | 11 자료 통합 진입 자료 (V-1 / V-1b 진입 source) |
| 2 | [VERIFICATION.md](VERIFICATION.md) | 386 | F-1 | 5 기능 검증 (지배 숫자 / 도구 / 메트릭) |
| 3 | [VERIFICATION_v2.md](VERIFICATION_v2.md) | 413 | V-1 | 의문 7건 검증 (부족 5 / 부분 충분 2 → V-1b 트리거) |
| 4 | [META_REVIEW.md](META_REVIEW.md) | 707 | M-1 | 시니어 회고 (Phase 7-12 학습 적용 / 9 영역 / 11장) |
| 5 | [WORK_PATTERNS.md](WORK_PATTERNS.md) | 885 | M-1 | 18 누적 문제 + 5 가드 + 자기 일관성 5종 + 검수 13 영역 |
| 6 | [PRINCIPLES.md](PRINCIPLES.md) | 612 | P-1 | 시니어 판단 10 패턴 + 5 핵심 원칙 + 본질 결정 추적 |
| 7 | [SCENARIO.md](SCENARIO.md) | 125 | M-1 | 시나리오 A (사용자 0명 / 기술 데모) 결정 |
| 8 | [AUDIT.md](AUDIT.md) | 238 | D-4 | 14 카드 종합 audit (18 누적 문제 17 해소 / WORK_PATTERNS) |
| 9 | [KARPATHY_LECTURE.md](KARPATHY_LECTURE.md) | 604 | V-0 | 카파시 영상 본문 14 영역 (V-1b 단어 위생 정착) |
| 10 | [KARPATHY_MAPPING.md](KARPATHY_MAPPING.md) | 320 | P-1 / V-1b | 영상 9 ↔ Aether 매핑 (V-1b §1 재작성 / §2-§6 영구 보류) |
| 11 | [D9_PRE_CHECK.md](D9_PRE_CHECK.md) | 245 | D-9 | RAG 정제 분기 3 보류 결정 추적 |
| 12 | [D8_PRE_CHECK.md](D8_PRE_CHECK.md) | 306 | D-8 | 자체 4 메트릭 vs ragas 분기 결정 추적 |
| 13 | [EVOLUTION.md](EVOLUTION.md) | 209 | Top 10 | 카드 진행 상황 (9.5/10 / T-3 보류 / Houseman Phase 7-12) |
| 14 | [TECH_DECISIONS.md](TECH_DECISIONS.md) | 384 | Phase 2 | 기술 결정 영역 (사전 분석 결과) |

---

## §3 pre-existing untracked 자료 분류 (CL-1 진단)

본 카드 영역 = **분류 본문만 정착 / 자동 이동 X / 사용자 결정 의무** (별도 시점 / CL-1 의무 X).

### 카테고리 A — 면접 / 이력서

| 자료 | 위치 | LOC / 자료 | Claude Code 추천 | 사유 |
|------|------|-----------|------------------|------|
| INTERVIEW.md | root | (head 30 검토 / Aether 면접 사실집) | **보존 / 커밋** | I-1 카드 진입 자료 / 면접 답변 4종 매핑 / README 정정 3건 |
| resume-analysis/aether-system-review.md | docs/resume-analysis/ | 1 파일 | **보존 / 커밋** | 이력서 영역 / 면접 자료 |

### 카테고리 B — Phase 2 사전 분석 + 카드 본문

| 자료 | 위치 | LOC | Claude Code 추천 | 사유 |
|------|------|-----|------------------|------|
| 01_architecture.md | docs/agent-capability-audit/ | 236 | **보존 / 커밋** | AGENTS §7 인용 위치 (line 132) / Phase 1 As-Is |
| 02_agent_implementation.md | docs/agent-capability-audit/ | 271 | **보존 / 커밋** | Phase 1 As-Is / 02:§3 인용 위치 |
| 03_rag_pipeline.md | docs/agent-capability-audit/ | 222 | **보존 / 커밋** | Phase 1 As-Is / RAG 영역 |
| 04_llmops_observability.md | docs/agent-capability-audit/ | 240 | **보존 / 커밋** | Phase 1 As-Is / LLMOps |
| 05_evaluation_testing.md | docs/agent-capability-audit/ | 206 | **보존 / 커밋** | AGENTS §7 인용 위치 (line 139 / 05:§2) |
| 06_api_reliability.md | docs/agent-capability-audit/ | 282 | **보존 / 커밋** | Phase 1 As-Is / 32 API 분류 |
| MCP_FAIL_DIAGNOSIS.md | docs/agent-capability-audit/ | 163 | **보존 / 커밋** | T-6b PRE-CHECK 자료 / D9_PRE_CHECK / D8_PRE_CHECK 패턴 일관성 |
| phase2_gap_matrix.md | docs/agent-capability-audit/ | 235 | **보존 / 커밋** | Top 10 트리거 자료 / 28행 우선순위 매트릭스 |
| phase3/ (폴더 / 11건) | docs/agent-capability-audit/ | 11 파일 | **보존 / 커밋** | Top 10 카드 마스터 로드맵 + 10 카드 본문 |

### 카테고리 C — PoC / 임시

| 자료 | 위치 | Claude Code 추천 | 사유 |
|------|------|------------------|------|
| llm-service/poc/ | llm-service/ | **archive 후보** | mcp_client_check.py / mcp_server_poc.py — T-2 정착 후 PoC 영역 / 본질 가치 ↓ / docs/archive/ 이동 추천 (사용자 결정 의무) |

### 카테고리 D — 코드 영역 (CL-1 영역 X)

| 자료 | 위치 | Claude Code 추천 | 사유 |
|------|------|------------------|------|
| frontend/src/lib/data/sp500.ts | frontend/ | **보존** | 코드 영역 / S&P 500 데이터 / CL-2 영역 |
| llm-service/app/data/knowledge_base/ | llm-service/ | **보존** | RAG 핵심 자료 / 정착 의무 / 절대 제거 X |

### 종합 추천

- **보존 / 커밋 추천**: 12건 (A 2 + B 9 + D 1 — knowledge_base는 이미 인용 영역) — 다음 사용자 결정 카드 시점에 일괄 git add + commit 추천
- **archive 후보**: 1건 (C / llm-service/poc/) — docs/archive/ 폴더 이동 추천
- **보존 (본인 영역 X)**: 1건 (D / sp500.ts — 코드 영역 / CL-2)

**본 카드 의무 X — 자동 이동 / 자동 커밋 0건**. 사용자 결정 카드 시점에 일괄 처리 가능.

---

## §4 자료 갱신 정책 (D-4 패턴)

D-4 audit 패턴 일관성 — 자료 본문 변경 시 영향 § 같은 PR에 동시 갱신 의무:

1. AGENTS.md §7 지배 숫자 변경 시 — 자료 본문 인용 위치 (META_REVIEW / WORK_PATTERNS / KARPATHY 등) 동시 갱신
2. ADR 결정 변경 시 — 카드 본문 결정 추적 + 자료 본문 인용 위치 동시 갱신
3. 자료 추가 / 제거 시 — 본 README + docs/README.md 갱신 의무
4. 매칭 점수 / 진화 표 변경 시 — KARPATHY_MAPPING.md §2 + AGENTS.md §7 KARPATHY 매칭 행 동시 갱신

---

## §5 다음 카드 진입 자료

| 카드 | 진입 자료 (audit 영역) | 본질 |
|------|------------------------|------|
| **CL-2** | 본 README §3 분류 결과 | 코드 정리 (CL-1과 영역 분리) |
| **CL-3** | TECH_DECISIONS.md / Phase 1-2 자료 | 의존성 정리 (requirements / package) |
| **TG-1** | AUDIT.md (D-4 / 238 LOC) | 시연 가이드 (14 카드 종합 결과) |
| **I-1** | KARPATHY_MAPPING.md §6 + INTERVIEW.md + phase3/ Top 10 | 면접 답변 시뮬 (꼬리 질문 + 9 영상 ↔ Aether 매핑) |

---

## §6 자료 영역 통계

- **정착 자료**: 14건 / 6,786 LOC (DIGEST 812 / WORK_PATTERNS 885 / META_REVIEW 707 / PRINCIPLES 612 / KARPATHY_LECTURE 604 / 외)
- **pre-existing**: 8건 / 1,855 LOC (06_api_reliability 282 / 02_agent_implementation 271 / D8_PRE_CHECK 306 / 01_architecture 236 / phase2_gap_matrix 235 / 04_llmops 240 / 03_rag 222 / 05_evaluation 206 / MCP_FAIL_DIAGNOSIS 163)
- **phase3/ 폴더**: 11건 (Top 10 카드 본문)
- **자료 합산**: 22건 .md + phase3/ 폴더 / 약 8,101 LOC

---

> **한 문장**: audit/ = M-1 ~ V-1b 18 카드 작업 자료 (정착 14 / pre-existing 9) + Phase 1-2 사전 분석 자료. CL-1 = 인덱스 정착 / pre-existing 자동 처리 X / 사용자 결정 의무.
