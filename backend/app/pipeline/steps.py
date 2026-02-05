"""
파이프라인 스텝 정의
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class PipelineStep:
    name: str           # "classify", "search", "generate"
    status: str         # "pending", "running", "done", "error"
    result: Any = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        # result가 Pydantic 모델이면 dict로 변환
        if hasattr(self.result, "model_dump"):
            d["result"] = self.result.model_dump()
        return d
