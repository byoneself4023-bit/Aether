# AUDIT — D-4 종합 자가 점검 (카드 14건 머지 후)

> **카드**: D-4 (Audit 종합 / 코드 변경 0 — 미세 정리 영역만 예외)
> **작성일**: 2026-05-07
> **본질**: WORK_PATTERNS 18 검증 + 메트릭 측정 + 미세 정리 + P-1 / I-1 진입 자료
> **결론 한 줄**: 카드 14건 누적 학습 정착 / WORK_PATTERNS 18 모두 해소 또는 부분 해소 / 미세 정리 4 라인 적용 / P-1 진입 베이스라인 확보.

---

## §1 카드 14건 종합

| # | 카드 | PR | commit | ADR | 본질 |
|---|---|---|---|---|---|
| 1 | C-1 | #18 | c8700cc | 0010 | T-3 보류 + PRINCIPLES 6/7 + SCENARIO v3 |
| 2 | M-1 | #19 | 70888b6 | - | META_REVIEW.md 신규 (707 라인) |
| 3 | F-1 | #20 | 2fceede | - | VERIFICATION.md (5 기능 검증 / Critical 발견) |
| 4 | F-1a | #21 | b3294c7 | 0004 v2 | JWT 알고리즘 HS512 통일 |
| 5 | D-1 | #22 | 03de438 | 0011 | 본질 X 기능 보류 (MLflow / drift / weight) |
| 6 | D-2 | #23 | 841b914 | 0012 | 운영급 결정 정착 (cache LRU / CORS / API 키) |
| 7 | D-0 | #24 | 492d68c | - | pre-existing frontend + README 정리 |
| 8 | D-3 | #25 | 901bc41 | 0013 | optimize 344 LOC + backtest 217 LOC 분리 |
| 9 | D-9 (보류) | #26 | 360801a | 0014 | RAG 데이터 정제 보류 + chromadb sync 부록 |
| 10 | D-8 | #27 | afe3ac2 | 0015 | RAG 평가 메트릭 (4 메트릭 + ragas 미도입) |
| 11 | T-2c | #28 | b5c2e26 | - | MCP 테스트 호스트 절대경로 → 동적 경로 |
| 12 | T-6b | #29 | f76df2e | 0016 | chromadb → Qdrant default 전환 |
| 13 | D-7 | #30 | c58b580 | 0017 | Chunking 자동 grid search (chunk_size=500/overlap=300) |
| 14 | D-5 | #31 | 6982e6f | 0018 | ReAct agent 4 → 5 도구 (RAG 통합) |
| 15 | D-6 | #32 | 532c946 | 0019 | Streaming SSE (우대 요건 4 직격) |

**머지 PR 합계**: 15건 (C-1 / M-1 / F-1 / F-1a / D-0 / D-1 / D-2 / D-3 / D-5 / D-6 / D-7 / D-8 / D-9 / T-2c / T-6b)

---

## §2 WORK_PATTERNS 18 누적 검증

### 카테고리 A — 작업 트리 위생 (문제 1·2·14)

| 문제 | 상태 | 근거 |
|---|---|---|
| 1. config.py pre-existing 변경 혼재 | **해소** | F-1a 이후 모든 카드 staging 명시 + pre-existing 분리 보존 |
| 2. 작업 트리 변경이 머지 cleanup 방해 | **해소** | D-0 (#24) 별도 PR로 정리 패턴 정립 |
| 14. gh pr create uncommitted changes 경고 | **해소** | git add 명시 + git status 확인 절차 정착 |

### 카테고리 E — 커밋 위생 (문제 3·15)

| 문제 | 상태 | 근거 |
|---|---|---|
| 3. Co-Authored-By 트레일러 | **해소** | F-1a 이후 모든 카드 트레일러 제외 |
| 15. gh pr merge --delete-branch 동작 | **해소** | F-1 이후 매 머지 검증 + main 동기화 패턴 |

### 카테고리 B — 사용자 prompt 검증 (문제 4·5·6)

| 문제 | 상태 | 근거 |
|---|---|---|
| 4. 응답 키 명칭 부정확 | **해소** | D-8/T-6b/D-7 baseline 실측 (recall@k / relevance@k 본격 검증) |
| 5. ADR 번호 부정확 | **해소** | 매 카드 plan에서 ADR 번호 명시 + 사전 측정 |
| 6. 변경 대상 누락 | **해소** | grep 사용처 실측 의무 정착 (D-5 / D-6 등) |

### 카테고리 C — 외부 라이브러리 (문제 7·11·12·13·18)

| 문제 | 상태 | 근거 |
|---|---|---|
| 7. ToolMessage.content 직렬화 형식 | **해소** | T-1b ReAct agent _extract_tool_results 정착 |
| 11. FutureWarning 무시 | 부분 해소 | 일부 deprecation warning 잔존 (asyncio / Pydantic) |
| 12. 외부 SDK 단위 변환 | **해소** | T-6b _EMBED_DIM 768 → 3072 G1 본질 트리거 정정 |
| 13. 응답 구조 변경 어댑터 | **해소** | T-6 어댑터 패턴 + T-6b 정착 |
| 18. 신규 패키지 의존성 베이스라인 | **해소** | D-2 / D-8 / D-7 모두 의존성 추가 0 본능 정착 (PyYAML / ragas 미도입) |

### 카테고리 G — 문서 갱신 (문제 8·10·16·17)

| 문제 | 상태 | 근거 |
|---|---|---|
| 8. 측정 추정값 vs 실측 | **해소** | F-1 / VERIFICATION.md 실측 패턴 정착 |
| 10. AGENTS.md §7 지배 숫자 중복 | **해소** | H-1c (`e7dc1ea`) 정리 + 매 카드 §7 검증 |
| 16. ADR 번호 관리 | **해소** | ADR 0011-0020 (10건 신규) 일관 번호 부여 |
| 17. 후속 카드 누적 | **해소** | 매 카드 plan에 후속 카드 트리거 명시 본능 |

### 카테고리 D — 5 가드 (문제 9)

| 문제 | 상태 | 근거 |
|---|---|---|
| 9. 의사결정 무한 루프 | **해소** | 매 카드 5 가드 (G1-G5) 적용 + Round Cap 1 의무 |

### 종합

- **해소**: 17 / 18 (94.4%)
- **부분 해소**: 1 / 18 (5.6%, 문제 11 FutureWarning)
- **미해소**: 0 / 18 (0%)

---

## §3 코드 메트릭 측정

### 3.1 LOC (services별)

| service | 언어 | LOC |
|---|---|---|
| auth-service | Java (Spring Boot) | 1,349 |
| portfolio-service | Python (FastAPI) | 4,731 |
| llm-service | Python (FastAPI) | 5,158 |
| frontend | TypeScript / TSX (Next.js) | 3,176 |
| **합계** | — | **14,414** |

### 3.2 테스트 누적

| service | passed | 비고 |
|---|---|---|
| llm-service | **357** | D-6 머지 시점 + 신규 10 추가 |
| portfolio-service | **203** | T-2c (#28) 이후 회복 베이스라인 |
| frontend (vitest) | 5 | Dashboard / Optimize / Backtest / Chat / Header |
| auth-service (gradle) | 70 | AGENTS.md §6 인용 |
| **합계** | **635** | M-1 시점 514 + 누적 +121 |

### 3.3 의존성

| service | 본격 의존성 추가 (D-1 → D-6) |
|---|---|
| llm-service | **0건** (PyYAML / ragas 미도입 / 자체 구현 본능) |
| portfolio-service | **−1건** (D-1 mlflow 제거) |
| auth-service | 0건 |
| frontend | 0건 |

### 3.4 ADR 19건 (0001-0019)

| 영역 | ADR | 카드 |
|---|---|---|
| 인프라 / 아키텍처 | 0001-0009 | 초기 정착 |
| 본질 X 기능 보류 | 0010 (T-3) / 0011 (D-1) / 0014 (D-9) | 보류 결정 패턴 |
| 운영급 결정 | 0012 (D-2) / 0013 (D-3) / 0016 (T-6b) / 0017 (D-7) / 0018 (D-5) / 0019 (D-6) | 정착 결정 패턴 |
| 평가 메트릭 | 0015 (D-8) | 자체 4 메트릭 |

**양면 정책 9 ADR 정립** (0011-0019 / D-4 후 10 ADR로 진화).

### 3.5 누적 자료 (docs/agent-capability-audit/)

| 자료 | LOC | 본질 |
|---|---|---|
| WORK_PATTERNS.md | 885 | 누적 문제 18건 + 체크리스트 A-G + plan 검수 13 영역 |
| META_REVIEW.md | 707 | Aether 시니어 메타 회고 + Houseman Phase 7-12 |
| PRINCIPLES.md | 537 | 시니어 판단 패턴 7건 |
| SCENARIO.md | 125 | 시나리오 A vs B 정의 + v3 |
| VERIFICATION.md | 386 | F-1 5 기능 검증 자료 |
| D8_PRE_CHECK.md | 306 | D-8 진입 본질 진단 |
| D9_PRE_CHECK.md | 245 | D-9 보류 결정 진단 |
| MCP_FAIL_DIAGNOSIS.md | 163 | T-2c 진단 자료 |
| **합계** | **3,354** | 누적 학습 자료 |

### 3.6 baseline 진화 (eval_rag.py)

| 단계 | chunk/overlap | recall@k | relevance@k |
|---|---|---|---|
| D-8 chromadb | 1000/200 | 1.0000 | 0.4444 |
| T-6b Qdrant | 1000/200 | 1.0000 | 0.7222 (+0.2778) |
| **D-7 Qdrant** | **500/300** | 1.0000 | **0.7413** (+0.0191) |

**누적 향상**: D-8 → D-7 = **+0.2969** (cosine 유사도 0.44 → 0.74).

---

## §4 발견된 미세 영역

### 4.1 HS256 주석 stale (2 위치)

F-1a (#21)에서 코드는 HS512로 통일됐으나 docstring 주석 미동기화:

| 파일 | 라인 | 본문 (Before) |
|---|---|---|
| `portfolio-service/app/config.py` | 37 | `# 인증 (auth-service와 동일 HS256 비밀키 - 256bit 이상)` |
| `llm-service/app/config.py` | 45 | `# 인증 (auth-service와 동일 HS256 비밀키 - 256bit 이상)` |

**정리 (After)**: `# 인증 (auth-service와 동일 HS512 비밀키 - F-1a / ADR 0004 v2)`

### 4.2 mlflow 잔재 (2 라인)

D-1 (#22)에서 MLflow experiment 모듈 제거됐으나 config.py field 잔존:

| 파일 | 라인 | 본문 |
|---|---|---|
| `portfolio-service/app/config.py` | 26 | `mlflow_tracking_uri: str = "./mlruns"` |
| `portfolio-service/app/config.py` | 27 | `mlflow_experiment_name: str = "aether-portfolio-optimization"` |

**검증**: 사용처 0 (grep `mlflow_tracking_uri\|mlflow_experiment_name` 결과 config.py 정의만). 정리 안전.

### 4.3 기타 영역 (보류)

- 의존성 cleanup (사용 X 패키지 제거): 시나리오 B 트리거
- 미사용 import 본격 정리: 비용 ↑ / 시나리오 A 영역 X
- deprecation warning 본격 처리 (asyncio.get_event_loop): 본격 audit 영역

---

## §5 정리 영역 vs 보류 영역 (ADR 0020 인용)

### 정리 영역 (본 카드 commit)

| 영역 | 라인 | 본질 |
|---|---|---|
| HS256 주석 동기화 | 2 라인 | F-1a 미동기화 sync |
| mlflow_tracking_uri / mlflow_experiment_name field 제거 | 2 라인 | D-1 잔재 정리 |
| **합계** | **4 라인** | 회귀 0 |

### 보류 영역 (ADR 0020 본문)

| 영역 | 트리거 |
|---|---|
| 본격 코드 audit (security / dead code) | 시나리오 B 진입 |
| 의존성 cleanup | 본격 production |
| 테스트 커버리지 90%+ | 시나리오 B 의무 |
| deprecation warning 본격 처리 | 비용 ↑ / 시나리오 A 영역 X |

---

## §6 P-1 / I-1 진입 가능성 검증

### P-1 (PRINCIPLES 8/9/10 신규 패턴) 진입 자료

- 카드 14건 머지 = 신규 패턴 발굴 영역
- 발굴 후보 (1-3건):
  - 패턴 8: "신규 endpoint 분리 = 점진 전환 본능" (D-5 / D-6 일관성)
  - 패턴 9: "Auto Research 본능 = 인간 결정 최소화" (D-7 grid search)
  - 패턴 10: "G1 본질 트리거 발견 시 정정 본능" (T-6b _EMBED_DIM 768 → 3072)

### I-1 (면접 답변 시뮬레이션) 진입 자료

- 객관 메트릭: 14,414 LOC / 635 테스트 / 19 ADR / 3,354 누적 자료 LOC
- 4 분기 결정 추적 (D-6 SSE / D-7 Auto Research / D-5 5 도구 / T-6b dim sync)
- 양면 정책 10 ADR 정립 (D-4 머지 후) — 시니어 시그널 누적
- 우대 요건 매칭: SSE (D-6) / RAG 평가 (D-8) / Chunking 튜닝 (D-7) / Multi-Agent 보류 (T-3 / 0010)

---

## §갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-07 | 초기 작성 — 카드 14건 종합 + WORK_PATTERNS 18/18 검증 + 메트릭 4 영역 + 미세 정리 4 라인 + P-1/I-1 진입 자료 |

**한 문장**: 카드 14건 누적 학습 본격 정착 — WORK_PATTERNS 18 모두 해소(17) 또는 부분 해소(1) / baseline relevance@k 0.44 → 0.74 (+67%) / 양면 정책 9 ADR / 누적 자료 3,354 LOC. P-1 진입 베이스라인 확보.
