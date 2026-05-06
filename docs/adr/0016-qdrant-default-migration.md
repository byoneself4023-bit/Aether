# ADR 0016 — vector_store default chromadb → qdrant 전환 (T-6b)

- **상태**: Accepted
- **일자**: 2026-05-07
- **관련 카드**: T-6b (ADR 0014 부록 해소)
- **결정 근거**: ADR 0009 + ADR 0014 부록 + WORK_PATTERNS 문제 19 + ADR 0011 형식 인용

---

## 컨텍스트

T-6 어댑터 (ChromaDBStore + QdrantStore) 머지 후에도 default `vector_store="chromadb"` 사용 중. ADR 0014 부록에서 sync 미전환 명시. 본 카드는 default 전환 + 실 검증 정착 + 임베딩 차원 sync (실측 발견) 정정.

---

## 결정

1. **`config.py:33` default 변경**: `chromadb` → `qdrant`
2. **`docker-compose.yml`**: llm-service env에 `VECTOR_STORE=${VECTOR_STORE:-qdrant}` + `QDRANT_URL=${QDRANT_URL:-http://qdrant:6333}` 추가 (toggle 보존)
3. **`vector_store.py:_EMBED_DIM` 정정**: `768` → `3072` (Gemini gemini-embedding-001 실측 차원, T-6b G1 본질 트리거 발견)
4. **Qdrant 컬렉션** `aether_knowledge`: 26 chunks / 3072차원 / cosine distance
5. **`seed_qdrant.py` 운영 스크립트** (force_reload + sample query 보고)
6. **chromadb 어댑터 보존** (롤백 / 비교 검증)

---

## eval_rag.py baseline 비교 (실 측정)

| 백엔드 | recall@k | 평균 relevance@k | 비고 |
|---|---|---|---|
| chromadb (D-8 baseline) | 1.0000 | **0.4444** | sqlite distance 자동 차원 감지 |
| **Qdrant (T-6b baseline)** | **1.0000** | **0.7222** | cosine score (`1 - score = distance`) |
| 차이 | 0 (동등) | **+0.2778 향상** | Qdrant 정규화 cosine score 우세 |

**시그널**: recall@k 동등 (검색 정확도 동일) + relevance@k Qdrant 우세 (정규화된 cosine score 본질). RAG 답 품질 측면 Qdrant 우위.

샘플 쿼리 (`샤프 비율이란?` k=3) 결과:
- top-1: `portfolio_theory` / 샤프 비율 (Sharpe Ratio) / relevance 0.7999
- top-2: `investment_strategies` / 성과 평가 지표 / 0.7407
- top-3: `investment_strategies` / 포트폴리오 최적화 전략 / 0.7039

---

## 영향

### 시그널 강화 (+)

- 분산 backend 정착 (시나리오 B 진입 시 즉시 활용)
- ADR 0009 본질 일관성
- **양면 정책 6 ADR 정립**: 0011 / 0012 / 0013 / 0014 / 0015 / **0016**
- Reversibility Type 2 (`VECTOR_STORE=chromadb` 환경변수 토글)
- WORK_PATTERNS 문제 19 (sync 누락 패턴) 직격 해소
- 임베딩 차원 sync (768 → 3072) — 실측 발견 + 정정

### 트레이드오프 (−)

- chromadb 인덱스 sunk cost (재임베딩 26 chunks, 비용 미미 — 26 Gemini API call)
- chromadb 사용 시점에 차원 자동 감지로 stale `_EMBED_DIM=768` 미발견 (Qdrant 명시 의무로 발견)

---

## G1 본질 트리거 발견 (실측 정정)

T-6b Step 5 컨테이너 startup 시 Qdrant upsert 400 Bad Request:
```
"Wrong input: Vector dimension error: expected dim: 768, got 3072"
```

**원인**: `vector_store.py:33 _EMBED_DIM = 768` — Gemini `gemini-embedding-001` 실 차원 3072와 mismatch. chromadb는 차원 자동 감지로 작동했지만 stale 값.

**대응**: `_EMBED_DIM = 3072` 정정 + Qdrant 컬렉션 강제 재생성 (`seed_qdrant.py`). 본 ADR 0016 결정 3에 명시.

---

## 미적용 영역 (시나리오 B 트리거)

| 영역 | 트리거 |
|---|---|
| Qdrant 클러스터 구성 | 스케일아웃 시점 |
| 임베딩 차원 튜닝 (`output_dimensionality`) | D-7 트리거 (Chunking 정책 + 차원 최적화) |
| 메타데이터 필터링 본격 활용 | 실 사용자 필터 발생 |
| Hybrid search (sparse + dense) | 도메인 다양성 ↑ 시점 |
| Qdrant Cloud 마이그레이션 | 시나리오 B 진입 |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **D-7** | T-6b 머지 후 | Chunking 정책 튜닝 (D-8 메트릭 + Qdrant baseline 활용) |
| **D-5** | D-7 후 | ReAct agent에 RAG 도구 추가 (4 → 5) |
| **D-6** | D-5 후 | Streaming 차별화 |
| **F-N (Qdrant 강화)** | 시나리오 B 진입 | 클러스터 / Hybrid / 메타 필터 본격 |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-07 | v1 | 초기 Accepted (default 전환 + 임베딩 차원 sync 768→3072 + Qdrant 26 chunks baseline + ADR 0014 부록 해소). 양면 정책 6 ADR 정립. |
