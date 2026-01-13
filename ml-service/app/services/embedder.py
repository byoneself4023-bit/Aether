from typing import List
from app.models.embeddings import EmbeddingModel


class Embedder:
    """임베딩 서비스"""

    def __init__(self):
        self.model = EmbeddingModel()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """텍스트 임베딩"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def get_similarity(self, text1: str, text2: str) -> float:
        """유사도 계산"""
        return self.model.similarity(text1, text2)
