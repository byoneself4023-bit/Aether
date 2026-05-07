# docs/ 자료 인덱스 (CL-1)

> **본질**: Aether 자료 폴더 영역 한 눈에 보기. 어디에 뭐가 있는지 / 어떤 카드 영역인지 / 6개월 후 다른 개발자 인지 가능 정착.
> **카드**: CL-1 (자료 인덱스 + pre-existing 14건 분류) / ADR 0024
> **갱신일**: 2026-05-07
> **다음 카드 진입**: CL-2 (코드 정리) / CL-3 (의존성 정리) / TG-1 (시연 가이드) / I-1 (면접 답변 시뮬)

---

## §1 Aether 자료 영역 한 눈에 보기

| 영역 | 위치 | 자료 수 | 본질 |
|------|------|---------|------|
| ADR (결정 추적) | [docs/adr/](adr/) | 23건 + README | 양면 정책 14 ADR (정착 / 보류 / 메타) |
| 작업 자료 (audit) | [docs/agent-capability-audit/](agent-capability-audit/) | 14건 정착 + 9건 pre-existing + README | M-1 ~ V-1b 18 카드 작업 자료 + Phase 2 사전 분석 |
| 기존 자료 (Phase 1-2 / git tracked) | docs/{Design,Differentiation,Guide,Integration,Interview,Phase,Review}/ | 분리 보존 | Aether 시작 시점 자료 (CL-1 영역 X) |
| 이력서 영역 | [docs/resume-analysis/](resume-analysis/) | 1건 (untracked) | aether-system-review.md |

Root 자료 (참고 / docs/ 영역 X):
- `AGENTS.md` — 코드 사실 (What). §7 지배 숫자 / §8 작업 시작 체크리스트.
- `CLAUDE.md` — 작업 방식 (How). 브랜치 / PR 게이트 / 위험 작업 / WORK_PATTERNS 의무.
- `README.md` — 프로젝트 진입 자료.
- `INTERVIEW.md` — pre-existing untracked / 면접 사실집 (CL-1 분류 영역).

---

## §2 핵심 자료 4건 (어디서 시작?)

| 자료 | 위치 | 본질 | 진입 시점 |
|------|------|------|-----------|
| AGENTS.md | root | 코드 사실 / §7 지배 숫자 / 카드 §8 체크리스트 | 매 카드 시작 의무 |
| CLAUDE.md | root | 작업 방식 / §1 브랜치 / §2 PR 게이트 / §6 1책임 / §7 WORK_PATTERNS 의무 | 매 카드 시작 의무 |
| PRINCIPLES.md | docs/agent-capability-audit/ | 시니어 판단 10 패턴 (P-1) | 본질 결정 시점 |
| WORK_PATTERNS.md | docs/agent-capability-audit/ | 18 누적 문제 + 5 가드 + 자기 일관성 5종 + 검수 13 영역 | 매 카드 plan 의무 (CLAUDE.md §7) |

---

## §3 자료 폴더 구조

```
Aether/
├── README.md                          (프로젝트 진입)
├── AGENTS.md                          (코드 사실 / §7 지배 숫자)
├── CLAUDE.md                          (작업 방식 / PR 게이트)
├── INTERVIEW.md                       (pre-existing / 면접 사실집)
└── docs/
    ├── README.md                      (본 자료 / docs 인덱스)
    ├── TEST_GUIDE.md                  (TG-1 / 5 기능 시연 가이드 + 면접 5분)
    ├── adr/                           (ADR 23건 + README)
    │   ├── README.md                  (ADR 카테고리 인덱스)
    │   ├── 0001-...                   (Top 10 카드 ADR)
    │   └── 0023-...                   (V-1b ADR)
    ├── agent-capability-audit/        (작업 자료)
    │   ├── README.md                  (audit 인덱스)
    │   ├── DIGEST.md                  (V-0 / 11 자료 통합)
    │   ├── META_REVIEW.md             (M-1 / 시니어 회고)
    │   ├── PRINCIPLES.md              (P-1 / 시니어 판단 10 패턴)
    │   ├── WORK_PATTERNS.md           (M-1 / 18 누적 문제)
    │   ├── KARPATHY_LECTURE.md        (V-0 / 영상 본문)
    │   ├── KARPATHY_MAPPING.md        (P-1 / V-1b / 영상 ↔ Aether)
    │   └── ... (총 14건 정착 + 9건 pre-existing — README 디테일 인용)
    ├── resume-analysis/               (pre-existing / 이력서 영역)
    │   └── aether-system-review.md
    ├── Design/                        (기존 / git tracked)
    ├── Differentiation/               (기존 / git tracked)
    ├── Guide/                         (기존 / git tracked)
    ├── Integration/                   (기존 / git tracked)
    ├── Interview/                     (기존 / git tracked)
    ├── Phase/                         (기존 / git tracked)
    └── Review/                        (기존 / git tracked)
```

---

## §4 카드 ID 인덱스 (M-1 ~ V-1b 18 카드)

| 카드 | 본질 | 산출물 |
|------|------|--------|
| M-1 | 시니어 회고 / META_REVIEW + WORK_PATTERNS + SCENARIO 작성 | META_REVIEW.md / WORK_PATTERNS.md / SCENARIO.md |
| F-1 | 5 기능 검증 (지배 숫자 / 도구 / 메트릭) | VERIFICATION.md |
| F-1a | HS512 알고리즘 통일 (auth-service ↔ python) | ADR 0004 v2 |
| D-1 | 본질 X 4건 보류 (MLflow / drift / weight / RAG 정제) | ADR 0011 |
| D-2 | 운영급 결정 (CORS / API 키 / cache) | ADR 0012 |
| D-0 | Frontend 정리 | (코드 변경 / ADR X) |
| D-3 | Frontend 페이지 분리 (200 LOC 임계) | ADR 0013 |
| D-9 | RAG 정제 보류 (분기 3) | ADR 0014 / D9_PRE_CHECK.md |
| D-8 | RAG 평가 자체 4 메트릭 (ragas 미도입) | ADR 0015 / D8_PRE_CHECK.md |
| T-2c | MCP fix (portfolio-service) | (코드 변경) |
| T-6b | Qdrant default + chromadb fallback (_EMBED_DIM 768→3072 정정) | ADR 0016 |
| D-7 | RAG Chunking grid search (9 조합 / chunk_size=500 / overlap=300) | ADR 0017 |
| D-5 | ReAct + RAG (5번째 도구 search_knowledge_base) | ADR 0018 |
| D-6 | Streaming SSE (POST /api/chat/stream) | ADR 0019 |
| D-4 | Audit 종합 (14 카드 / 18 누적 문제 정리) | ADR 0020 / AUDIT.md |
| P-1 | PRINCIPLES 8/9/10 (귀납) + KARPATHY 매핑 (연역) | ADR 0021 / PRINCIPLES.md / KARPATHY_MAPPING.md |
| V-1 | 의문 7건 검증 (V-0 진입 자료) | ADR 0022 / VERIFICATION_v2.md |
| V-1b | KARPATHY_MAPPING §1 재작성 (영상 9 ↔ Aether) + LECTURE 단어 위생 | ADR 0023 |
| **CL-1** | **자료 인덱스 (본 카드)** | **ADR 0024 / docs/README.md / docs/agent-capability-audit/README.md / docs/adr/README.md** |

---

## §5 자료 갱신 정책

D-4 패턴 일관성 — 자료 본문 변경 시 영향 § 같은 PR에 동시 갱신 의무:

1. AGENTS.md §7 지배 숫자 변경 시 — 인용 위치 (자료 본문 / ADR) 동시 갱신
2. ADR 결정 변경 시 — v2 / v3 / git log 추적 (영역 분리 X)
3. 자료 추가 / 제거 시 — docs/README.md / docs/agent-capability-audit/README.md / docs/adr/README.md 갱신
4. 카드 머지 시 — 카드 ID 인덱스 (§4) + AGENTS.md §7 baseline 행 갱신

---

## §6 면접 자료 영역

| 자료 | 영역 | 본질 |
|------|------|------|
| INTERVIEW.md (root) | 면접 사실집 | README 정정 3건 + 면접 답변 4종 매핑 표 + 운영 답변 14 장애 |
| KARPATHY_MAPPING.md §6 | I-1 카드 영역 | 면접 답변 5 영역 + 꼬리 질문 시뮬 (V-1b 시점 보류 / I-1 시점 재작성) |
| Top 10 카드 자료 | docs/agent-capability-audit/phase3/ | 11 카드 본문 (00 master_roadmap + 10 카드) |
| 시니어 본질 | PRINCIPLES.md (10 패턴) + META_REVIEW.md | 본질 결정 + 회고 |

---

## §7 다음 카드 진입 자료

> **TG-1 정착** (docs/TEST_GUIDE.md / 5 기능 시연 + 면접 5분). **CL-2 / CL-3 영구 보류** (CL-D / ADR 0025). 다음 진입 = I-1 (면접 답변 시뮬).

| 카드 | 진입 자료 | 본질 |
|------|-----------|------|
| **I-1** | docs/TEST_GUIDE.md + KARPATHY_MAPPING.md §6 + INTERVIEW.md + Top 10 자료 | 면접 답변 시뮬 (꼬리 질문 영역) |
| Aether 종료 | 모든 자료 / 양면 정책 15 ADR | 시나리오 A 종료 — Houseman 진입 시점에 CL-2 / CL-3 검토 |
| **CL-2 / CL-3** | (영구 보류 / ADR 0025) | 시나리오 B 진입 시점 트리거 — 코드 / 의존성 cleanup |

---

> **한 문장**: docs/ 자료 영역 = ADR 23건 + audit 14건 정착 자료 + 9건 pre-existing + 기존 영역 7 폴더 + resume-analysis. 본 자료 = docs/ 진입점 / audit + adr README는 영역별 디테일 정착.
