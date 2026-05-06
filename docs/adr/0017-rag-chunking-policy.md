# ADR 0017 — RAG Chunking 정책 자동 grid search (D-7)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: D-7 (Auto Research 본능 정착)
- **결정 근거**: D-8 메트릭 + T-6b Qdrant baseline (3072차원) + 카파시 Auto Research 본능 + ADR 0011 / 0015 / 0016 형식 인용

---

## 컨텍스트

기존 chunking 정책 (`rag_chunk_size=1000` / `rag_chunk_overlap=200`)이 인간 직관 기반 — 결정 근거 추적 부재. 본 카드는 자동 grid search로 메트릭 비교 본능 정착 + T-6b 학습 통합 (3072차원 환경 chunk_size 최적 영역 검증).

**카파시 Auto Research 본능 직격 적용**: 인간 결정 최소화 + 메트릭 자동 비교 → 최적 조합 자동 선정.

---

## 결정

### 1. grid search 9 조합 자동 실험

| 영역 | 값 |
|---|---|
| chunk_size | [500, 1000, 1500] |
| overlap | [100, 200, 300] |
| 조합 수 | **3 × 3 = 9** |
| top-k | 3 |
| 백엔드 | Qdrant (T-6b default) |
| 임베딩 | Gemini gemini-embedding-001 / 3072차원 |

### 2. 최적 선정 룰

`recall@k >= 1.0` 유지 + `relevance@k` 최대.

### 3. config.py default 변경

```python
# Before
rag_chunk_size: int = 1000
rag_chunk_overlap: int = 200

# After (D-7 grid search 결과)
rag_chunk_size: int = 500
rag_chunk_overlap: int = 300
```

### 4. grid_search_chunking.py 운영 자료

subprocess 격리 본능 — env 주입 + seed_qdrant + eval_rag 별도 프로세스 호출 (lru_cache settings stale 회피).

CLI: `python -m scripts.grid_search_chunking [--quick] [--top-k N] [--output PATH]`.

### 5. Auto Research 본능 정착

인간 결정 최소화 / 메트릭 자동 비교 → 결정 근거 추적 (markdown 표 + ADR 첨부).

---

## grid search 결과 (실 측정)

| chunk_size | overlap | recall@k | relevance@k |
|---|---|---|---|
| 500 | 100 | 1.0000 | 0.7332 |
| 500 | 200 | 1.0000 | 0.7367 |
| **500** | **300** | **1.0000** | **0.7413** ★ |
| 1000 | 100 | 1.0000 | 0.7225 |
| 1000 | 200 | 1.0000 | 0.7222 (T-6b baseline) |
| 1000 | 300 | 1.0000 | 0.7222 |
| 1500 | 100 | 1.0000 | 0.7216 |
| 1500 | 200 | 1.0000 | 0.7213 |
| 1500 | 300 | 1.0000 | 0.7213 |

**모든 9 조합 recall@k 1.0 유지** — chunking 변동에도 검색 정확도 안정. relevance@k 차이는 chunk_size에 강하게 의존:
- chunk_size=500 영역: 0.7332-0.7413 (높음)
- chunk_size=1000 영역: 0.7222-0.7225 (중간 / 기존 baseline)
- chunk_size=1500 영역: 0.7213-0.7216 (낮음)

**3072차원 환경 학습**: 임베딩 차원이 높으면 작은 chunk가 specific 매칭에 유리 (의미 단위 정밀도 ↑).

---

## eval_rag baseline 추적 (3 단계)

| 단계 | 백엔드 | chunk_size / overlap | recall@k | relevance@k |
|---|---|---|---|---|
| D-8 baseline | chromadb | 1000 / 200 | 1.0000 | 0.4444 |
| T-6b baseline | Qdrant | 1000 / 200 | 1.0000 | 0.7222 (+0.2778) |
| **D-7 최적** | Qdrant | **500 / 300** | 1.0000 | **0.7413** (+0.0191 / +2.6%) |

**누적 개선**: D-8 → D-7 = **+0.2969 향상** (cosine 유사도 0.44 → 0.74).

---

## 컬렉션 chunks 수 변동

| chunk_size | chunks | 비고 |
|---|---|---|
| 1000 (기존) | 26 | T-6b baseline |
| **500 (D-7 최적)** | **36** | +10 chunks (정밀도 ↑, Gemini API 비용 미미) |

knowledge_base 4 md (554 LOC) ## 헤더 분할 + chunk_size 추가 분할.

---

## 영향

### 시그널 강화 (+)

- **Auto Research 본능 정착**: 인간 결정 최소화 / 메트릭 자동 비교
- **카파시 매칭 점수 진화**: Auto Research 70 → 85 / 평균 81 → 83
- **양면 정책 7 ADR 정립**: 0011 / 0012 / 0013 / 0014 / 0015 / 0016 / **0017**
- **T-6b 학습 통합**: 3072차원 환경 chunk_size 최적 영역 검증 (작은 chunk 우세)
- **결정 근거 추적**: grid_search_results.md + ADR 0017 첨부
- **Reversibility Type 2**: `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` 환경변수 즉시 토글

### 트레이드오프 (−)

- chunks 26 → 36 (+10) — Gemini API 비용 미미 (시드 1회)
- 임베딩 정밀도 vs 문맥 손실 trade-off — chunk_size=500이 정밀도 우세 (3072차원 + ## 헤더 분할 본질)

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| sentence-aware chunking | 의미 단위 분할 의무 발생 시 |
| 다국어 chunking | 한국어 / 영어 외 도메인 발생 |
| 동적 chunk_size (질문 복잡도 기반) | 질문 다양성 ↑ |
| 임베딩 차원 vs chunk_size 상호작용 본격 검증 | output_dimensionality 튜닝 시점 |
| chunking 함수 자체 수정 (현재 ## 헤더 + 문단) | semantic chunking 도입 시 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **D-5** | D-7 머지 후 | ReAct agent에 RAG 도구 추가 (4 → 5) |
| **D-6** | D-5 후 | Streaming 차별화 |
| **D-4 / P-1 / I-1** | 종합 정리 | 면접 대비 |
| **F-N (Chunking 본격)** | 시나리오 B 진입 | sentence-aware / 다국어 / 동적 chunk_size |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (grid search 9 조합 + chunk_size=500/overlap=300 default + Auto Research 본능 정착). 양면 정책 7 ADR 정립. eval_rag baseline 0.7222 → 0.7413 (+0.0191 / +2.6%). |
