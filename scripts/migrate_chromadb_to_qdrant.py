"""ChromaDB → Qdrant 데이터 마이그레이션 스크립트 (T-6).

운영 진입 시점 1회 실행. ChromaDB 컬렉션의 모든 포인트를 Qdrant로 이전 후
무작위 쿼리 5건의 top-3 동등성을 비교해 데이터 무결성을 검증한다.

사용:
    cd llm-service
    PYTHONPATH=. .venv/bin/python ../scripts/migrate_chromadb_to_qdrant.py [--dry-run]

환경변수:
    CHROMA_PERSIST_DIR  ChromaDB persist 경로 (default: ./data/chroma)
    QDRANT_URL          Qdrant URL (default: http://localhost:6333)
    QDRANT_COLLECTION   대상 컬렉션 이름 (default: aether_knowledge)
"""

from __future__ import annotations

import argparse
import logging
import random
import sys

import chromadb
from app.config import get_settings
from app.services.vector_store import (
    QdrantStore,
    reset_vector_store,
)
from chromadb.config import Settings as ChromaSettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrate")

CHROMA_COLLECTION = "aether_knowledge"


def main() -> int:
    parser = argparse.ArgumentParser(description="ChromaDB → Qdrant 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="검증만 (Qdrant upsert 없이)")
    parser.add_argument("--top-k", type=int, default=3, help="동등성 검증 top-k (default: 3)")
    args = parser.parse_args()

    settings = get_settings()

    logger.info(f"ChromaDB persist dir: {settings.chroma_persist_dir}")
    chroma_client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    try:
        chroma_collection = chroma_client.get_collection(CHROMA_COLLECTION)
    except Exception:
        logger.error(f"ChromaDB collection '{CHROMA_COLLECTION}' not found — RAG 미초기화 상태")
        return 1

    chroma_count = chroma_collection.count()
    logger.info(f"ChromaDB 포인트 수: {chroma_count}")
    if chroma_count == 0:
        logger.warning("ChromaDB 비어있음 — 마이그레이션 스킵")
        return 0

    dump = chroma_collection.get(include=["embeddings", "documents", "metadatas"])
    ids: list[str] = list(dump["ids"])
    embeddings = [list(e) for e in dump["embeddings"]]
    documents: list[str] = list(dump["documents"]) if dump["documents"] else [""] * len(ids)
    metadatas: list[dict] = [dict(m) if m else {} for m in dump["metadatas"]] if dump["metadatas"] else [{}] * len(ids)

    if args.dry_run:
        logger.info(f"[dry-run] {len(ids)}건 dump 완료. Qdrant upsert 스킵.")
        return 0

    reset_vector_store()
    qdrant = QdrantStore()
    qdrant.init(force_reload=True)
    qdrant.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    logger.info(f"Qdrant upsert 완료: {qdrant.count()}건")

    logger.info("동등성 검증 — 무작위 5건 쿼리 top-{}".format(args.top_k))
    sample_indices = random.sample(range(len(ids)), min(5, len(ids)))
    mismatches = 0
    for idx in sample_indices:
        q_emb = embeddings[idx]
        chroma_results = chroma_collection.query(
            query_embeddings=[q_emb],
            n_results=args.top_k,
            include=["distances"],
        )
        chroma_top = list(chroma_results["ids"][0]) if chroma_results["ids"] else []

        qdrant_results = qdrant.query(embedding=q_emb, k=args.top_k)
        qdrant_top = [r["id"] for r in qdrant_results]

        if set(chroma_top) == set(qdrant_top):
            logger.info(f"  [OK] {ids[idx]}: top-{args.top_k} 동일")
        else:
            mismatches += 1
            logger.warning(f"  [DIFF] {ids[idx]}: chroma={chroma_top} qdrant={qdrant_top}")

    logger.info(f"검증 결과: 5건 중 {5 - mismatches}건 동일, {mismatches}건 차이")
    return 0 if mismatches == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
