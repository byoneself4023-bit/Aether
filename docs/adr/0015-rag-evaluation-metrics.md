# ADR 0015 — RAG 평가 메트릭 정착 + ragas 미도입 결정 (D-8)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: D-8 / D8_PRE_CHECK (`docs/agent-capability-audit/D8_PRE_CHECK.md`)
- **결정 근거**: D8_PRE_CHECK §3.5 + §5.4 분기 2 + PRINCIPLES 패턴 6 + ADR 0011 / 0014 형식 인용

---

## 컨텍스트

RAG 답 품질 측정 자료 부재 — 튜닝 결정 근거 추적 불가 ("왜 chunk_size=1000? 왜 k=3?"). D8_PRE_CHECK 진단 결과:

| 영역 | 결과 |
|---|---|
| ragas 라이브러리 의존성 | 부재 (`requirements.txt`에 미존재) |
| RAG 응답 구조 | `{answer, sources}` 자체 평가 충분 |
| ground truth 작성 가능성 | knowledge_base 4 md (554 LOC) ## 헤더 친화 → 8건 30분-1시간 |
| 자체 구현 vs ragas 비용 | **자체 구현 우위** (시나리오 A 적합) |

본 카드는 자체 간소화 4 메트릭 정착으로 결정 근거 추적 본능 정립.

---

## 결정

### 1. 자체 구현 4 메트릭 정착

| 메트릭 | 정의 | 계산 방식 |
|---|---|---|
| `relevance@k` | top-k 검색 결과의 평균 cosine 유사도 | `mean(sources[i].relevance)` (rag.py 이미 적용) |
| `recall@k` | 기대 source가 top-k 검색 결과에 포함된 비율 | `1.0 if expected in actual_sources else 0.0` (질문별 0/1, 평균 0~1) |
| `LLM-judge quality` | 답변 정확성·완성도 (1-5 정수) | Gemini 직접 호출 + JSON structured output |
| `LLM-judge faithfulness` | 답변이 sources에 근거하는 비율 (0-1) | Gemini 직접 호출 + JSON structured output |

### 2. ragas 표준 도입 보류

- `requirements.txt` 변경 0
- 이유: 시나리오 A 자동화 의무 X + ragas 학습 비용 ≫ 시그널 강도

### 3. ground truth JSON 8건 (4 영역 균형)

`llm-service/data/eval_rag_ground_truth.json`:
- portfolio_theory 3건 (샤프 / 효율적 프론티어 / MVP)
- risk_management 2건 (VaR / CVaR)
- investment_strategies 2건 (1/N / 리스크 패리티)
- sector_analysis 1건 (정보기술 섹터)

### 4. CLI 1회 ad-hoc 실행

```bash
python -m scripts.eval_rag \
  --ground-truth data/eval_rag_ground_truth.json \
  --top-k 3 \
  --output report.md \
  [--no-llm-judge] \
  [--json]
```

### 5. markdown report + JSON 출력 옵션

- 기본: markdown (집계 메트릭 + 질문별 표)
- `--json` flag: 파싱 친화 출력

### 6. LLM-judge optional 토글 (Gemini quota 부재 대응)

| 방식 | 본질 |
|---|---|
| 환경변수 `EVAL_LLM_JUDGE_ENABLED` | default `true`. `false` / `0` / `no` 시 skip |
| CLI `--no-llm-judge` flag | 동일 동작 (LLM 호출 0) |
| skip 결과 | relevance@k + recall@k 2 메트릭만 출력 (시연 가능 보장) |

### 7. 자동화 시나리오 B 트리거 명시

다음 시점에 후속 카드 진입:
- 시나리오 B 진입 (실 사용자 + 평가 빈도 ↑)
- CI 통합 (PR 게이트로 RAG 회귀 차단)
- LLM 자동 ground truth 생성 (도메인 다양성 ↑ 시점)

### 8. main() / eval_main() 분리

- `main()` = sync entry (argparse + `asyncio.run`)
- `eval_main(args)` = async logic (init + 평가 루프 + report)
- 테스트 친화: `eval_main`은 직접 await 가능

---

## 영향

### 시그널 강화 (+)

- 의존성 비용 0 (PyYAML / ragas 추가 X)
- 시나리오 A 본질 적합 (1회 ad-hoc 시연)
- Gemini 직접 호출 = 본 프로젝트 도메인 적합
- **양면 정책 5 ADR 정립**: 0011 (D-1 보류) + 0012 (D-2 정착) + 0013 (D-3 정착) + 0014 (D-9 보류) + **0015 (D-8 정착 + ragas 미도입)**
- Quota 회피 본능 정착 (LLM-judge optional)

### 트레이드오프 (−)

- ragas 표준 메트릭 (context precision / recall / faithfulness) 본격 매칭 X
- 단 "ragas 미도입 이유" 답 가능 시그널로 보완 (시니어 본질 판단 입증)

### chromadb 평가 결과 동등성 가정

- ADR 0014 부록 인용 — 현재 chromadb 사용 중
- 본 ADR 0015는 chromadb / Qdrant 결과 동등성 가정 (T-6b 후속 카드 트리거 시 검증)

### 실 실행 baseline (D-8 머지 시점)

- 8 질문 / top-k=3 / `--no-llm-judge` fallback
- recall@k = **1.0000** (모든 질문 검색 정확)
- 평균 relevance@k ≈ 0.44 (cosine 유사도)

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| ragas 표준 도입 | 시나리오 B 진입 + 자동화 의무 발생 |
| CI 통합 (PR 게이트) | RAG 회귀 차단 의무 발생 |
| LLM 자동 ground truth 생성 | 도메인 다양성 ↑ 시점 |
| drift 추적 (평가 빈도 메트릭) | 실 사용자 데이터 발생 시점 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **T-6b** | D-8 머지 후 | chromadb → Qdrant 실 전환 (ADR 0014 부록) |
| **D-7** | T-6b 후 | Chunking 정책 튜닝 (D-8 메트릭 기반) |
| **D-5** | D-7 후 | ReAct agent에 RAG 도구 추가 (4 → 5) |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (D-8 정착 + ragas 미도입 + LLM-judge optional + main/eval_main 분리). 양면 정책 5 ADR 정립. |
