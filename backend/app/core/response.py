"""
표준 응답 포맷
"""
from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """표준 API 응답"""
    success: bool = True
    data: Any = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: Any = None) -> "ApiResponse":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "ApiResponse":
        return cls(success=False, error=error)
