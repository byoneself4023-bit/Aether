from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class KeywordExtractor:
    """키워드 추출 서비스"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2)
        )

    def extract(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """텍스트에서 주요 키워드 추출"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]

            # 상위 k개 키워드 추출
            top_indices = np.argsort(scores)[-top_k:][::-1]
            keywords = [
                (feature_names[idx], float(scores[idx]))
                for idx in top_indices
                if scores[idx] > 0
            ]

            return keywords
        except Exception:
            return []
