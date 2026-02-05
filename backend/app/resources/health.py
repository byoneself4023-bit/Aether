"""
상세 헬스체크 엔드포인트
"""
from fastapi import APIRouter

from app.resources.registry import registry

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """리소스별 상세 헬스 상태"""
    resources = registry.health_check()

    # 핵심 리소스가 로드됐는지 (mock 포함)
    domain_ok = resources["domain_classifier"]["loaded"]
    faiss_ok = resources["faiss_store"]["loaded"] or not resources["faiss_store"]["mock"]

    # mock 모드 여부
    any_mock = any(
        v.get("mock", False) for v in resources.values() if isinstance(v, dict)
    )

    if domain_ok and not any_mock:
        status = "healthy"
    elif domain_ok:
        status = "degraded"  # mock mode 운영 중
    else:
        status = "unhealthy"

    mock_resources = [k for k, v in resources.items() if isinstance(v, dict) and v.get("mock")]

    return {
        "status": status,
        "service": "claro-backend",
        "mock_mode": bool(mock_resources),
        "mock_resources": mock_resources,
        "resources": resources,
    }
