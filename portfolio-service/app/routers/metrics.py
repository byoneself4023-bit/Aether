"""Prometheus 메트릭 엔드포인트"""

from fastapi import APIRouter
from fastapi.responses import Response

from app.metrics import get_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus 메트릭 엔드포인트

    Prometheus scraper가 이 엔드포인트를 폴링하여 메트릭을 수집합니다.
    Grafana와 연동하여 대시보드를 구성할 수 있습니다.

    Returns:
        Prometheus exposition format의 메트릭 데이터
    """
    metrics_output = get_metrics()
    return Response(
        content=metrics_output,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
