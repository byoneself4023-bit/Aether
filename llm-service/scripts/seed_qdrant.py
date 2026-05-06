"""T-6b Qdrant seed 스크립트 — knowledge_base 4 md → Qdrant aether_knowledge 컬렉션.

ADR 0016: vector_store default chromadb → qdrant 전환 후 운영 자료.
lifespan startup 자동 init과 별개 — force_reload + 결과 보고용.
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="T-6b Qdrant seed (knowledge_base → aether_knowledge)")
    parser.add_argument("--no-force-reload", action="store_true", help="기존 컬렉션 유지 (default: force_reload=True)")
    parser.add_argument("--sample-query", default="샤프 비율이란?", help="시드 후 샘플 쿼리 (검증용)")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    os.environ.setdefault("VECTOR_STORE", "qdrant")

    from app.services.rag import (
        get_vectorstore_status,
        init_vectorstore,
        query,
    )
    from app.services.vector_store import reset_vector_store
    import app.services.rag as rag_mod

    reset_vector_store()
    rag_mod._initialized = False

    force = not args.no_force_reload
    print(f"[seed] backend=qdrant force_reload={force}", file=sys.stderr)
    success = init_vectorstore(force_reload=force)
    if not success:
        print("[seed] init_vectorstore failed", file=sys.stderr)
        return 2

    status = get_vectorstore_status()
    count = status.get("document_count", 0)
    print(f"[seed] collection count: {count}")
    if count == 0:
        print("[seed] WARNING: collection is empty after seed", file=sys.stderr)
        return 3

    print(f"\n[seed] sample query: {args.sample_query!r} (k={args.top_k})")
    docs = query(args.sample_query, k=args.top_k)
    for i, doc in enumerate(docs, start=1):
        title = doc.get("metadata", {}).get("title", "Unknown")
        source = doc.get("metadata", {}).get("source", "Unknown")
        distance = doc.get("distance", 0.0)
        relevance = max(0.0, 1.0 - distance)
        print(f"  [{i}] source={source} title={title} relevance={relevance:.4f}")

    print(f"\n[seed] DONE — Qdrant aether_knowledge ready ({count} chunks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
