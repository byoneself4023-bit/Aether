# ADR 0009 — ChromaDB → Qdrant 벡터 DB 마이그레이션 (T-6)

**상태**: **Accepted** (T-6 본격 PR 머지 — `llm-service/app/services/vector_store.py` 어댑터 신규, RAG 24 회귀 0, 어댑터 17 신규 통합 통과)
**일자**: 2026-05-05
**관련 카드**: T-6 (`docs/agent-capability-audit/phase3/` 미생성, plan 파일 `~/.claude/plans/t-2-pr-cozy-pearl.md` 참조)
**결정 근거 (면접 답변 일관성)**: `docs/agent-capability-audit/TECH_DECISIONS.md` §1 ChromaDB (라인 28-80, 라인 75 면접 답변)

---

## 컨텍스트

TECH_DECISIONS.md §1 라인 42/54/75에 *"운영 진입 시점에 Qdrant 마이그레이션을 T-6 카드로 분리"* 명시. AGENTS.md §7 라인 124에도 *"수평 확장 제약 → T-6에서 Qdrant 이전 예정"* 박혀있음. 본 ADR은 그 결정의 *실행 기록*.

SCENARIO.md 시나리오 A(기술 데모) 맥락 유지 — 진짜 운영 전환 X. **마이그레이션 패턴 정착 자체가 시니어 시그널** (어댑터 + 환경변수 토글 + 데이터 무결성 검증). 면접 답변에서 *"왜 ChromaDB? 왜 Qdrant로?"* 둘 다 답할 수 있는 근거.

ChromaDB 한계 (TECH_DECISIONS.md §1 라인 49-52):
- 운영 영속성 약함 (in-memory)
- 멀티 인스턴스 동기화 X
- 인증 / 권한 약함

Qdrant 강점:
- Rust 기반, gRPC 지원, 멀티 인스턴스 동기화 가능
- 오픈소스 (락인 위험 X, vs Pinecone)
- 768 차원 / cosine 호환 — 임베딩 모델(Gemini `gemini-embedding-001`) 그대로

---

## 결정

**ChromaDB 1.5.0 + Qdrant v1.12.0 어댑터 토글 채택.**

- 신규 어댑터 모듈: `llm-service/app/services/vector_store.py`
  - 추상 클래스 `VectorStore` — `init / count / add / query / delete / list_all`
  - 백엔드 2종: `ChromaDBStore` (default, legacy 보존), `QdrantStore` (신규)
  - 싱글톤 팩토리: `get_vector_store()` — env 분기 후 모듈 캐시 (자기 일관성 패턴 1)
- 환경변수 `VECTOR_STORE=chromadb|qdrant` 토글 (default: chromadb)
- 호출자(`rag.py`) 0 변경 보장 — `query()` 반환 형식 동일 (`distance` 작을수록 가까움)
- Qdrant cosine score (0~1, 클수록 가까움) → ChromaDB distance(작을수록) 변환: `distance = max(0, 1 - score)` (자기 일관성 패턴 3)
- 마이그레이션 스크립트: `scripts/migrate_chromadb_to_qdrant.py` (dump + upsert + top-k 동등성 검증)

---

## 사전 측정 (문제 18 의존성 베이스라인 — 3차 적용)

`pip install --dry-run 'qdrant-client>=1.7,<2.0'`:
- 다운그레이드 0건
- 충돌 0건
- 신규 5건: `qdrant-client 1.17.1`, `h2 4.3.0`, `hpack 4.1.0`, `hyperframe 6.1.0`, `portalocker 3.2.0`
- 트랜지티브 영향 없음 (httpx/pydantic/anyio 모두 기존 만족)

---

## 4 도구 매핑 표 (어댑터 ↔ 백엔드)

| VectorStore 메서드 | ChromaDBStore | QdrantStore |
|---|---|---|
| `init(force_reload)` | `PersistentClient(path) + get_or_create_collection` | `QdrantClient(url) + create_collection(VectorParams(768, COSINE))` |
| `count()` | `collection.count()` | `client.get_collection().points_count` |
| `add(ids, embs, docs, metas)` | `collection.add(...)` | `client.upsert(points=[PointStruct(id=hash, vector, payload)])` |
| `query(emb, k, where)` | `collection.query(query_embeddings, n_results, where, include)` → 변환 | `client.query_points(query, limit, query_filter)` → distance=1-score 변환 |
| `delete(ids)` | `collection.delete(ids=...)` | `client.delete(PointIdsList(points=[hash(id)]))` |
| `list_all(limit)` | `collection.get(limit, include=["metadatas"])` | `client.scroll(limit, with_payload=True)` |

**ID 변환**: ChromaDB는 임의 문자열, Qdrant는 unsigned int. `_string_to_qdrant_id()`가 md5 8byte big-endian으로 안정적인 매핑 제공.

**Filter 변환**: ChromaDB `{"source": "..."}` → Qdrant `Filter(must=[FieldCondition(key, match=MatchValue(value))])`.

---

## docker-compose.yml

`qdrant/qdrant:v1.12.0` 컨테이너 추가:
- 포트 6333 (HTTP) / 6334 (gRPC)
- 볼륨 `qdrant_storage` (영속성)
- `llm_chroma_data` 볼륨 보존 (롤백 가능)
- llm-service `depends_on` 갱신 X (env=qdrant 시 외부 healthcheck로 충분, 기본 모드는 의존 없음)

테스트는 `QdrantClient(":memory:")` in-memory 모드로 실행 — Docker 의존 0.

---

## 트레이드오프

**+ 채택:**
- 운영급 (Rust + gRPC, 멀티 인스턴스 동기화)
- 오픈소스 (Apache 2.0, 락인 위험 X)
- 768/cosine 호환 (Gemini embedding 그대로)
- 어댑터 패턴 → 호출자 0 변경 → G2 가역
- env 토글 → 운영 사고 시 즉시 복원

**− 비용:**
- Docker 컨테이너 추가 (~500MB 메모리)
- 학습 곡선 (Rust 컬렉션 / 페이로드 인덱싱)
- ID 변환 레이어 (string → int hash)

---

## 롤백

1단계 (즉시): `unset VECTOR_STORE` 또는 `export VECTOR_STORE=chromadb`
2단계 (영구): `git revert <T-6 커밋>` — 어댑터 모듈 + qdrant-client 의존 제거. ChromaDB 직접 호출 코드는 어댑터 안에 보존되어 있어 추가 작업 없음.

데이터 손실 없음 (`llm_chroma_data` 볼륨 + ChromaDB persist dir 그대로).

---

## L-7 X-Request-ID 통합

벡터 DB 호출은 `rag.py` 안에서만 발생 → 기존 `RequestLoggingMiddleware`의 `request_id_ctx`가 자동 적용됨. 어댑터는 ContextVar에 손대지 않음 (분리 책임 = §6 1책임).

---

## 후속 카드

- **T-6b** (선택): 마이그레이션 데이터 본격 검증 (top-k 동등성 광범위 샘플)
- **T-6c** (보류): Pinecone 옵션 추가 — 본 어댑터에 `PineconeStore` 추가하면 됨
- **T-6d** (보류): 멀티 컬렉션 분리 (도메인별 인덱스 — portfolio_theory / risk_management / strategy)

---

## 참조

- `llm-service/app/services/vector_store.py` — 어댑터 본체
- `llm-service/app/services/rag.py` — 어댑터 호출자
- `llm-service/tests/test_vector_store.py` — 17 통합 테스트
- `scripts/migrate_chromadb_to_qdrant.py` — 데이터 이전 스크립트
- `docs/agent-capability-audit/TECH_DECISIONS.md` §1 (라인 28-80) — 결정 근거
- `docs/adr/0008-mcp-server-adoption.md` — 어댑터 + env 토글 패턴 (T-2에서 학습)
