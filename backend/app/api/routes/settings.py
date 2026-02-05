"""설정 라우트"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings

router = APIRouter()

# 런타임 설정 (메모리 저장 — 재시작 시 초기화)
_runtime_settings = {
    "llm_provider": "ollama",
    "ollama_model": settings.OLLAMA_MODEL,
    "top_k": 5,
    "min_similarity": 0.5,
    "max_tokens": 1024,
}


class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    ollama_model: Optional[str] = None
    top_k: Optional[int] = None
    min_similarity: Optional[float] = None
    max_tokens: Optional[int] = None


@router.get("")
async def get_settings():
    """현재 설정 조회"""
    return {
        **_runtime_settings,
        "backend_version": settings.APP_VERSION,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "google_api_configured": bool(settings.GOOGLE_API_KEY),
    }


@router.put("")
async def update_settings(update: SettingsUpdate):
    """설정 변경"""
    for key, value in update.model_dump(exclude_none=True).items():
        if key in _runtime_settings:
            _runtime_settings[key] = value

    return {"success": True, "settings": _runtime_settings}
