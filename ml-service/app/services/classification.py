from typing import List, Dict
from app.models.classifier import ComplaintClassifier


class ClassificationService:
    """분류 서비스"""

    def __init__(self):
        self.classifier = ComplaintClassifier()
        self.label_map = {
            "0": "일반문의",
            "1": "불만접수",
            "2": "건의사항",
            "3": "칭찬",
            "4": "기타"
        }

    def classify(self, texts: List[str]) -> List[Dict]:
        """텍스트 분류"""
        predictions = self.classifier.predict(texts)
        results = []

        for text, (label_idx, confidence) in zip(texts, predictions):
            results.append({
                "text": text,
                "category": self.label_map.get(label_idx, "기타"),
                "confidence": confidence
            })

        return results
