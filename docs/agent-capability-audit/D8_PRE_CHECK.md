# D8_PRE_CHECK — RAG 평가 메트릭 진단 (D-8 진입 본질 명확화)

> **카드**: D-8 진단 전용 (코드 변경 0 / git 작업 0)
> **작성일**: 2026-05-07
> **본질**: 시나리오 A에서 D-8 (RAG 평가 메트릭) 카드의 본질 적합도 검증 + 분기 결정
> **결론 한 줄**: **분기 2 확정** — ragas 표준 미도입 + 자체 간소화 메트릭 정착이 시나리오 A 본질 적합. D-8 본능 재정의 사용자 보고 의무.

---

## §1 RAG 출력 분석

### §1.1 query_with_llm() 응답 구조

`llm-service/app/services/rag.py:486-532` 정독 결과:

```python
def query_with_llm(question, k=3, include_sources=True) -> dict:
    relevant_docs = query(question, k=k)  # 유사 문서 검색
    context, sources = build_optimized_context(relevant_docs, question)
    answer = call_llm(prompt, system_prompt=...)
    return {"answer": str, "sources": list[dict]}  # 2 필드
```

**`sources` 구조** (rag.py:474-481):
```python
{
  "title": str,           # 문서 제목 (## 헤더)
  "source": str,          # 파일명 (e.g. "portfolio_theory")
  "relevance": float,     # 1 - distance (cosine 유사도, 0~1)
}
```

### §1.2 /api/chat 응답 사용 (RAG fallback)

`routers/chat.py:191-214` (D-9 PRE-CHECK §1.3 인용):
- 티커 < 2 → RAG 호출 → `ChatResponse(answer + sources + portfolio_data=None)`
- `ChatResponse.sources`: `list[SourceInfo]` (title / source / relevance 3 필드)

### §1.3 /api/rag/query 응답 (RAGQueryResponse)

`schemas/chat.py:142-151` 정독:
```python
class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[SourceInfo]
    confidence: float  # 0~1, 평균 relevance
```

`routers/rag.py:71-75` confidence 계산:
```python
confidence = sum(s.relevance for s in sources) / len(sources)
```

### §1.4 ReAct 4 도구 응답 (참조 — RAG 미포함)

`agents/react_agent.py:19-24` `_TOOL_NAME_TO_FIELD`:
- `analyze_portfolio_tool` → `portfolio_analysis`
- `explain_risk_tool` → `risk_analysis`
- `summarize_backtest_tool` → `backtest_analysis`
- `get_recommendation_tool` → `recommendation`

**RAG 도구 0건 확정** (D-9 PRE-CHECK §1.2 재확인). 본 평가 카드 = `query_with_llm()` + `/api/rag/*` 한정.

---

## §2 평가 대상 명확화

### §2.1 knowledge_base 4 md 평가 가능 데이터 양

| 파일 | LOC |
|---|---|
| investment_strategies.md | 185 |
| portfolio_theory.md | 82 |
| risk_management.md | 130 |
| sector_analysis.md | 157 |
| **합계** | **554** |

이미 ## 헤더 분할 + 명확한 정의 (예: portfolio_theory.md "샤프 비율 = (Rp - Rf) / σp"). **평가 ground truth 작성 친화적**.

### §2.2 평가 케이스 작성 가능성

**Yes — 5-10건 즉시 작성 가능**:

| 질문 | 기대 source | 기대 title |
|---|---|---|
| "샤프 비율이란?" | portfolio_theory | 샤프 비율 (Sharpe Ratio) |
| "효율적 프론티어란?" | portfolio_theory | 효율적 프론티어 |
| "최소분산 포트폴리오란?" | portfolio_theory | 최소분산 포트폴리오 (MVP) |
| "VaR 계산 방법?" | risk_management | (예상) |
| "동일 비중 전략?" | investment_strategies | (예상) |
| "섹터 분산 효과?" | sector_analysis | (예상) |
| "상관관계의 중요성?" | portfolio_theory | 상관관계의 중요성 |

작성 시간 추정: **30분-1시간** (질문 5-10건 + 기대 sources YAML/JSON).

### §2.3 ground truth 작성 비용

- 사용자 시간: 30분-1시간 (5-10건)
- 자동 생성 가능성: Gemini로 self-instruct 가능 (md → 질문/답 자동 생성, 단 ground truth 신뢰도 검증 필요)
- 비용 vs 시그널: **시그널 강도 우위** (시연 시 평가 결과 노출 = 시니어 시그널)

### §2.4 평가 빈도 (권고)

| 빈도 | 적합도 | 본질 |
|---|---|---|
| **시연 1회 (ad-hoc)** | **★★★** | 시나리오 A 본질 적합 — 자동화 의무 X |
| CI 자동화 (PR 게이트) | ★ | 시나리오 B (실 사용자) 진입 시점 트리거 |
| 주기 자동화 (cron) | ★ | 동일 (시나리오 B 트리거) |

**권고**: 시연 1회 ad-hoc 실행. CI / 주기 자동화는 ADR 0014 형식으로 시나리오 B 트리거 명시.

---

## §3 평가 메트릭 본질 진단

### §3.1 relevance@k (검색 정확도)

- **이미 구현됨** (rag.py:474-481 `relevance = 1 - distance`)
- 평가 = ground truth 기대 sources와 검색 결과 source 일치율
- 자체 구현 즉시 가능 — ragas 의존성 X

### §3.2 answer quality

| 방식 | 시나리오 A 적합도 |
|---|---|
| LLM-as-judge (Gemini 직접 호출) | **★★★** — 이미 google-genai 의존성 / 추가 비용 0 |
| 정적 ground truth (string match) | ★ — knowledge_base 답이 자연어라 string match 부적합 |
| BLEU / ROUGE | ★ — 자연어 답 평가 부적합 |

**권고**: LLM-as-judge (Gemini) 직접 호출.

### §3.3 hallucination (sources 인용 검증)

- 답변에 sources의 title / 본문 키워드 포함 여부 검증
- 자체 구현 가능 (regex / token overlap)
- 또는 LLM-as-judge로 통합 (faithfulness 평가)

### §3.4 ragas 표준 (context precision / recall / faithfulness)

| 항목 | 결과 |
|---|---|
| 라이브러리 의존성 | **부재** (`requirements.txt`에 ragas 없음) |
| 도입 비용 | 의존성 추가 + langchain 통합 + 학습 곡선 |
| 시나리오 A 적합도 | **★** (자동화 의무 X 상황에서 표준 도입 = 과잉 비용) |
| 시그널 강도 | 중간 (표준 도입 시그널은 있지만 비용 정당화 약함) |

### §3.5 자체 구현 vs ragas 비용 비교

| 영역 | 자체 구현 | ragas |
|---|---|---|
| 의존성 추가 | 0 (이미 google-genai / Pydantic) | ragas + langchain.evaluation |
| 코드 작성 | 1 스크립트 (~100 LOC) | 통합 코드 (~50 LOC) + 의존성 학습 |
| 메트릭 종류 | relevance@k / recall@k / LLM-judge / faithfulness 4건 | context precision / recall / faithfulness / answer relevancy 4건 |
| 시나리오 A 적합 | **★★★** (간소 + 비용 0) | ★ (표준화 의무 X) |
| 면접 시그널 | "ragas 안 쓴 이유" 답 가능 = 시니어 본능 | "ragas 도입" 답 가능 = junior 본능 |

**결론**: **자체 구현 우위** — 시나리오 A에서 비용 ↓ + 시그널 ↑.

---

## §4 시나리오 A 본질 적합도

### §4.1 사용자 0명 = 평가 자동화 본능 적합도

- 자동화 의무 X (시연 1회 ad-hoc 적합)
- CI / 주기 자동화 = 시나리오 B 진입 시점 트리거 (ADR 0011 / 0014 형식)
- 본 카드 결정: **자동화 미도입 + 트리거 명시**

### §4.2 시연 노출 방식

| 방식 | 시나리오 A 적합도 |
|---|---|
| **CLI 출력 + markdown report** | **★★★** — 시연 시 1회 실행 + 결과 노출 |
| frontend 대시보드 | ★ — 사용자 0명 = UI 통합 의무 X |
| PDF 보고서 | ★ — 자동화 의무 X |
| Jenkins CI 통합 | ★ — 시나리오 B 트리거 |

**권고**: CLI 스크립트 (`llm-service/scripts/eval_rag.py`) + markdown report 출력.

### §4.3 면접 답변 가능성

| 질문 | 답변 가능성 |
|---|---|
| "RAG 평가 메트릭은?" | ✓ — relevance@k / recall@k / LLM-as-judge / faithfulness 4건 |
| "ragas 도입 안 한 이유?" | ✓ — 시나리오 A 자동화 의무 X + 자체 구현 비용 ↓ + 시그널 ↑ |
| "평가 자동화는?" | ✓ — 시나리오 B 진입 시점 트리거 명시 (ADR 형식) |
| "ground truth 작성 비용?" | ✓ — 30분-1시간 (5-10건 yaml) |

**Yes — 시니어 시그널 강함** (간소화 + 트리거 명시 = PRINCIPLES 6번 직격).

---

## §5 D-8 진입 결정 분기

### §5.1 분기 1 (D-8 진행 — ragas 도입)

**X** — 시나리오 A 부적합:
- ragas 의존성 비용 ≫ 시그널 강도
- 자동화 의무 X
- 표준 도입 = junior 본능

### §5.2 분기 2 (D-8 재정의 — 간소화 메트릭) ✓

**채택**:
- 자체 구현 4 메트릭 (relevance@k / recall@k / LLM-as-judge / faithfulness)
- ground truth 5-10건 YAML
- CLI 스크립트 (`scripts/eval_rag.py`) + markdown report
- 시연 시 ad-hoc 실행
- 자동화는 시나리오 B 트리거 (ADR 형식)

### §5.3 분기 3 (D-8 보류 — T-6b 우선)

**X** — chromadb 사용 중에도 평가 가능 (chromadb / Qdrant 결과 차이 검증 X 필요). T-6b는 별도 카드 (ADR 0014 부록 인용).

### §5.4 결정

**분기 2 확정 — D-8 본능 재정의**:

D-8 카드 새 본질:
1. **자체 구현 메트릭 4건** (relevance@k / recall@k / LLM-as-judge / faithfulness)
2. **ground truth YAML** (5-10건 질문 + 기대 sources)
3. **CLI 스크립트** (`llm-service/scripts/eval_rag.py`)
4. **markdown report 출력** (CLI / 시연 1회)
5. **자동화 트리거 명시** (시나리오 B 진입 시 CI 통합 — ADR 형식)
6. **ADR 0015** 신규 작성 (D-8 평가 정착 + ragas 미도입 결정 + 자동화 트리거)

**사용자 보고 의무** (G3 Done Definition): D-8 본능 재정의 = ragas 미도입 + 간소화 4 메트릭 + CLI 1회 실행 본질로 수정.

---

## §6 면접 답변 시나리오 (Why → How → What)

### §6.1 Why (왜 평가)

> "Aether는 ReAct agent 4 도구 + RAG fallback (티커 < 2) 구조입니다. RAG 답 품질을 측정 자료 없이는 '왜 이 chunk_size? 왜 k=3?' 답변 불가능합니다. 평가 메트릭은 **튜닝 결정 근거**를 추적하는 시니어 도구입니다."

### §6.2 How (어떻게 평가)

> "자체 구현 4 메트릭:
> 1. **relevance@k**: 검색 결과의 평균 cosine 유사도 (이미 rag.py에 distance → relevance 계산 적용)
> 2. **recall@k**: ground truth 기대 sources가 top-k 검색 결과에 포함된 비율
> 3. **LLM-as-judge** (Gemini): 답변 품질 점수 (1-5 척도)
> 4. **faithfulness**: 답변이 sources에 근거한 비율 (LLM-as-judge로 통합)
> 
> CLI 스크립트 1회 실행 + markdown report — 시나리오 A 자동화 의무 X."

### §6.3 What (무엇을 평가)

> "ground truth YAML 5-10건:
> - 질문 (예: '샤프 비율이란?')
> - 기대 source (예: portfolio_theory)
> - 기대 title (예: '샤프 비율 (Sharpe Ratio)')
> 
> knowledge_base 4 md (554 LOC, 정형 작성)에서 ## 헤더 기반 작성 — 30분-1시간 비용."

### §6.4 Aether 시나리오 A 답변 가능 여부

**Yes — 시니어 시그널 강함**:
- "ragas 안 쓴 이유" 답 가능 = 비용 인식 + 본질 판단 시그널
- "자동화 안 한 이유" 답 가능 = 시나리오 B 트리거 명시 (PRINCIPLES 6번)
- "평가 메트릭 4건" 답 가능 = 도메인 본능 (RAG 평가 표준 4 영역 인지)
- 양면 정책 패턴 일관성: ADR 0011 (D-1 보류) + 0012 (D-2 정착) + 0013 (D-3 정착) + 0014 (D-9 보류) + **0015 (D-8 정착 + ragas 미도입)**

---

## §7 후속 카드 권고 (D-8 본능 재정의)

| 카드 | 본질 | 우선순위 |
|---|---|---|
| **D-8 (재정의)** | 자체 구현 4 메트릭 + ground truth YAML + CLI 스크립트 + markdown report + ADR 0015 | **즉시 진입** |
| **ADR 0015** (신규) | D-8 정착 결정 + ragas 미도입 + 자동화 시나리오 B 트리거 명시 | D-8 카드 산출물 |
| **T-6b** (chromadb → Qdrant) | D-8 진입 시점 또는 별도 (ADR 0014 부록) | 조건부 |
| **D-7** (Chunking 정책) | D-8 결과 기반 튜닝 (chunk_size / overlap) | D-8 후 |
| **D-5** (RAG 도구 추가) | D-7 후 차별화 | 후속 |

---

## §8 검증 메타 (5 가드 + WORK_PATTERNS)

### §8.1 5 가드 적용

- **G1 본질 트리거**: 진단 중 "ragas 의존성 추가 비용 ≫ 시그널" 발견 → 즉시 분기 2 강제 ✓
- **G2 Reversibility**: Type 1 (산출 1 파일 / git 작업 0) ✓
- **G3 Done Definition**: §1-§7 모두 채움 + 분기 2 결정 + D-8 본능 재정의 사용자 보고 ✓
- **G4 Round Cap**: 1 라운드 완료 ✓
- **G5 First Principle**: "정착된 메트릭 ≠ 본질 적합 메트릭" 직격 증명 ✓

### §8.2 WORK_PATTERNS 누적 문제 매칭

| 문제 | 본 진단 매칭 |
|---|---|
| 문제 4 (응답 schema 키 가설) | RAGQueryResponse 3 필드 (answer / sources / confidence) 실측 (chat.py:142-151) |
| 문제 6 (호출 위치 가설) | confidence 계산 위치 (rag.py:71-75) + ChatResponse / RAGQueryResponse 분리 grep |
| 문제 12 (단위 가정) | relevance@k 단위 (0~1, cosine 유사도) 명시 |
| 문제 13 (외부 SDK) | ragas 의존성 부재 실측 (`grep ragas requirements.txt` 0건) |
| 문제 19 (sync 누락) | chromadb sync 미전환 (ADR 0014 부록 인용) — D-8 평가 환경 영향 0 (chromadb로 평가 가능) |

---

## §갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-07 | 초기 작성 — 분기 2 확정 (D-8 본능 재정의) + ragas 미도입 + 자체 4 메트릭 + ADR 0015 후속 권고 |

**한 문장**: D-8 진입 본질 진단 결과 ragas 표준 미도입 + 자체 간소화 메트릭 (relevance@k / recall@k / LLM-as-judge / faithfulness) + CLI 1회 실행 + 자동화 시나리오 B 트리거 명시 = 시나리오 A 본질 적합 시니어 결정.
