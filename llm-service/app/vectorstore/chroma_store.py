import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional


class ChromaStore:
    """Chroma 벡터 스토어"""

    def __init__(self, persist_directory: Optional[str] = None):
        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name="complaints",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[Dict]) -> None:
        """문서 추가"""
        ids = [str(i) for i in range(len(documents))]
        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """유사 문서 검색"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        documents = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "score": 1 - results["distances"][0][i] if results["distances"] else 0,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                })

        return documents

    def delete_collection(self) -> None:
        """컬렉션 삭제"""
        self.client.delete_collection("complaints")
