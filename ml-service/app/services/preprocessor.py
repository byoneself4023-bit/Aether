import re
from typing import List


class Preprocessor:
    """텍스트 전처리 서비스"""

    def __init__(self):
        self.patterns = [
            (r'[^\w\s가-힣]', ' '),  # 특수문자 제거
            (r'\s+', ' '),  # 연속 공백 제거
        ]

    def process(self, text: str) -> str:
        """텍스트 전처리"""
        processed = text.strip()

        for pattern, replacement in self.patterns:
            processed = re.sub(pattern, replacement, processed)

        return processed.strip()

    def batch_process(self, texts: List[str]) -> List[str]:
        """배치 전처리"""
        return [self.process(text) for text in texts]
