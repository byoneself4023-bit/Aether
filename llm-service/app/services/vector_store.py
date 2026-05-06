"""벡터 DB 어댑터 — ChromaDB / Qdrant 백엔드 추상화 (T-6).

환경변수 VECTOR_STORE=chromadb(default)|qdrant 토글로 즉시 백엔드 전환.
호출자(rag.py)는 동일 인터페이스 사용, 백엔드 차이는 어댑터 흡수.
"""

from __future__ import annotations

import hashlib
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "aether_knowledge"
# Gemini gemini-embedding-001 default 차원 (T-6b 실측: 3072). chromadb는 자동 감지, Qdrant는 명시 의무.
_EMBED_DIM = 3072


class VectorStore(ABC):
    """벡터 DB 추상 인터페이스. ChromaDB / Qdrant 어느 백엔드든 동일하게 호출."""

    @abstractmethod
    def init(self, *, force_reload: bool = False) -> None: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None: ...

    @abstractmethod
    def query(
        self,
        embedding: list[float],
        k: int,
        where: dict | None = None,
    ) -> list[dict]: ...

    @abstractmethod
    def delete(self, ids: list[str]) -> None: ...

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[dict]: ...


class ChromaDBStore(VectorStore):
    """ChromaDB 백엔드 (default, legacy 보존)."""

    def __init__(self) -> None:
        self._client: chromadb.ClientAPI | None = None
        self._collection: chromadb.Collection | None = None

    def init(self, *, force_reload: bool = False) -> None:
        settings = get_settings()
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        if force_reload:
            try:
                self._client.delete_collection(_COLLECTION_NAME)
                logger.info(f"Deleted existing collection: {_COLLECTION_NAME}")
            except Exception:
                pass
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"description": "Aether financial knowledge base"},
        )

    def count(self) -> int:
        if self._collection is None:
            return 0
        return self._collection.count()

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        if self._collection is None:
            raise RuntimeError("ChromaDBStore not initialized — call init() first")
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        embedding: list[float],
        k: int,
        where: dict | None = None,
    ) -> list[dict]:
        if self._collection is None:
            raise RuntimeError("ChromaDBStore not initialized — call init() first")
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        documents: list[dict] = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                documents.append(
                    {
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0,
                    }
                )
        return documents

    def delete(self, ids: list[str]) -> None:
        if self._collection is None:
            raise RuntimeError("ChromaDBStore not initialized — call init() first")
        self._collection.delete(ids=ids)

    def list_all(self, limit: int = 100) -> list[dict]:
        if self._collection is None:
            return []
        results = self._collection.get(limit=limit, include=["metadatas"])
        documents: list[dict] = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append(
                {
                    "id": doc_id,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {},
                }
            )
        return documents


class QdrantStore(VectorStore):
    """Qdrant 백엔드 (신규).

    Qdrant cosine score(0~1, 클수록 가까움) → ChromaDB distance(작을수록 가까움)
    변환: ``distance = 1 - score``. 호출자(rag.py) 인터페이스 0 변경.
    """

    def __init__(self) -> None:
        self._client: QdrantClient | None = None
        self._collection_name: str = _COLLECTION_NAME

    def init(self, *, force_reload: bool = False) -> None:
        settings = get_settings()
        url = settings.qdrant_url
        if url.startswith(("http://", "https://")):
            self._client = QdrantClient(url=url)
        elif url == ":memory:":
            self._client = QdrantClient(":memory:")
        else:
            self._client = QdrantClient(path=url)
        self._collection_name = settings.qdrant_collection

        existing = {c.name for c in self._client.get_collections().collections}
        if force_reload and self._collection_name in existing:
            self._client.delete_collection(self._collection_name)
            existing.discard(self._collection_name)

        if self._collection_name not in existing:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=_EMBED_DIM, distance=Distance.COSINE),
            )

    def count(self) -> int:
        if self._client is None:
            return 0
        info = self._client.get_collection(self._collection_name)
        return int(info.points_count or 0)

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        if self._client is None:
            raise RuntimeError("QdrantStore not initialized — call init() first")
        points = [
            PointStruct(
                id=_string_to_qdrant_id(doc_id),
                vector=emb,
                payload={"doc_id": doc_id, "content": content, **meta},
            )
            for doc_id, emb, content, meta in zip(ids, embeddings, documents, metadatas)
        ]
        self._client.upsert(collection_name=self._collection_name, points=points)

    def query(
        self,
        embedding: list[float],
        k: int,
        where: dict | None = None,
    ) -> list[dict]:
        if self._client is None:
            raise RuntimeError("QdrantStore not initialized — call init() first")
        query_filter = _build_filter(where) if where else None
        response = self._client.query_points(
            collection_name=self._collection_name,
            query=embedding,
            limit=k,
            query_filter=query_filter,
            with_payload=True,
        )
        hits = response.points
        documents: list[dict] = []
        for hit in hits:
            payload = dict(hit.payload or {})
            doc_id = payload.pop("doc_id", str(hit.id))
            content = payload.pop("content", "")
            documents.append(
                {
                    "id": doc_id,
                    "content": content,
                    "metadata": payload,
                    "distance": max(0.0, 1.0 - float(hit.score)),
                }
            )
        return documents

    def delete(self, ids: list[str]) -> None:
        if self._client is None:
            raise RuntimeError("QdrantStore not initialized — call init() first")
        qids = [_string_to_qdrant_id(i) for i in ids]
        self._client.delete(
            collection_name=self._collection_name,
            points_selector=PointIdsList(points=qids),
        )

    def list_all(self, limit: int = 100) -> list[dict]:
        if self._client is None:
            return []
        points, _ = self._client.scroll(
            collection_name=self._collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        documents: list[dict] = []
        for p in points:
            payload = dict(p.payload or {})
            doc_id = payload.pop("doc_id", str(p.id))
            payload.pop("content", None)
            documents.append({"id": doc_id, "metadata": payload})
        return documents


def _string_to_qdrant_id(doc_id: str) -> int:
    """문자열 ID → 안정적인 64bit unsigned int (Qdrant point ID 규격).

    ChromaDB는 임의 문자열 ID, Qdrant는 unsigned int 또는 UUID.
    동일 doc_id → 동일 int 보장 (md5 8byte big-endian).
    """
    return int.from_bytes(hashlib.md5(doc_id.encode("utf-8")).digest()[:8], "big")


def _build_filter(where: dict) -> Filter:
    """ChromaDB where dict({"source": "..."}) → Qdrant Filter."""
    return Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in where.items()])


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """환경변수/설정 기반 lazy init singleton (자기 일관성 패턴 1)."""
    global _store
    if _store is None:
        backend = os.getenv("VECTOR_STORE", get_settings().vector_store).lower()
        if backend == "qdrant":
            _store = QdrantStore()
        else:
            _store = ChromaDBStore()
        logger.info(f"VectorStore initialized: backend={backend}")
    return _store


def reset_vector_store() -> None:
    """테스트용: 싱글톤 캐시 리셋."""
    global _store
    _store = None
