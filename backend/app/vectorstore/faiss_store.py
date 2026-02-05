import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS

class LocalEmbeddings:
    """LangChain 호환 임베딩 클래스"""
    def __init__(self, model):
        self.model = model

    def embed_query(self, text):
        return self.model.encode(text).tolist()

    def embed_documents(self, texts):
        return [self.model.encode(t).tolist() for t in texts]

    def __call__(self, text):
        return self.embed_query(text)

class FAISSStore:
    """FAISS 벡터 스토어 (도메인 필터링 지원)"""

    def __init__(self, index_path: Optional[str] = None):
        BASE_DIR = Path.home() / "CIVILCOMPLAINT"

        self.embedding_model = SentenceTransformer(
            str(BASE_DIR / "models" / "embedding")
        )
        self.dimension = 768

        self.index = None
        self.index_path = index_path or str(BASE_DIR / "data" / "vectordb" / "faiss_index")
        self._load_index()

    def _load_index(self):
        index_path = Path(self.index_path)
        if index_path.exists():
            embeddings = LocalEmbeddings(self.embedding_model)
            self.index = FAISS.load_local(
                str(index_path),
                embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"✅ FAISS 로드: {self.index.index.ntotal:,} vectors")
        else:
            print(f"⚠️ FAISS 인덱스 없음: {index_path}")

    def search(
        self, query: str, top_k: int = 5, domain: Optional[str] = None
    ) -> List[Dict]:
        if not self.index:
            return []

        # 도메인 필터링 시 더 많이 검색한 뒤 필터
        fetch_k = top_k * 3 if domain else top_k
        results = self.index.similarity_search_with_score(query, k=fetch_k)

        if not results:
            return []

        # L2 거리값들 추출
        distances = [score for _, score in results]
        min_dist = min(distances)
        max_dist = max(distances)

        # 중복 제거 (같은 질문 제거)
        seen_questions = set()
        unique_results = []

        for doc, dist in results:
            question = doc.metadata.get("question", "")
            if question in seen_questions:
                continue
            seen_questions.add(question)

            # 상대적 유사도 계산 (1위는 95~99%, 순위별로 차등)
            if max_dist == min_dist:
                similarity = 0.95
            else:
                # 거리가 작을수록 높은 점수 (0.70 ~ 0.99 범위)
                normalized = (max_dist - dist) / (max_dist - min_dist)
                similarity = 0.70 + (normalized * 0.29)

            unique_results.append({
                "question": question,
                "answer": doc.metadata.get("answer", ""),
                "domain": doc.metadata.get("domain", ""),
                "category": doc.metadata.get("category", ""),
                "score": round(similarity, 2)
            })

        # 도메인 필터링 적용 (결과 부족 시 전체로 fallback)
        if domain:
            filtered = [r for r in unique_results if r["domain"] == domain]
            if len(filtered) >= min(top_k, 2):
                return filtered[:top_k]
            # fallback: 도메인 우선, 나머지 보충
            others = [r for r in unique_results if r["domain"] != domain]
            return (filtered + others)[:top_k]

        return unique_results[:top_k]
