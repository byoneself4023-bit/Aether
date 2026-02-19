"""비중 변화 모니터링 서비스"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class WeightChangeAlert:
    """개별 자산 비중 변화 알림"""
    asset: str
    old_weight: float
    new_weight: float
    change_pct: float  # 절대값 변화 퍼센트 포인트
    change_direction: str  # "increase" or "decrease"


@dataclass
class WeightComparisonResult:
    """비중 비교 결과"""
    total_turnover: float  # 총 턴오버 (sum of |changes| / 2)
    alerts: list[WeightChangeAlert]  # 임계값 초과 변화 목록
    max_change_asset: Optional[str]  # 가장 큰 변화 자산
    max_change_pct: float  # 가장 큰 변화 퍼센트


def compare_weights(
    old_weights: dict[str, float],
    new_weights: dict[str, float],
    threshold: float = 0.1,
    include_removed: bool = True,
    include_added: bool = True
) -> WeightComparisonResult:
    """
    기존 비중과 새 비중을 비교하여 변화 분석

    Args:
        old_weights: 기존 비중 딕셔너리 {ticker: weight}
        new_weights: 새 비중 딕셔너리 {ticker: weight}
        threshold: 알림 임계값 (퍼센트 포인트, 기본 10%)
        include_removed: 제거된 자산 포함 여부
        include_added: 새로 추가된 자산 포함 여부

    Returns:
        WeightComparisonResult: 비교 결과
    """
    alerts = []
    all_changes = []

    # 모든 자산 수집
    all_assets = set(old_weights.keys()) | set(new_weights.keys())

    for asset in all_assets:
        old_w = old_weights.get(asset, 0.0)
        new_w = new_weights.get(asset, 0.0)

        change = new_w - old_w
        change_pct = abs(change)
        all_changes.append((asset, change_pct))

        # 제거된 자산
        if asset not in new_weights:
            if include_removed and old_w >= threshold:
                alerts.append(WeightChangeAlert(
                    asset=asset,
                    old_weight=round(old_w, 6),
                    new_weight=0.0,
                    change_pct=round(old_w * 100, 2),  # 퍼센트로 표시
                    change_direction="removed"
                ))
            continue

        # 새로 추가된 자산
        if asset not in old_weights:
            if include_added and new_w >= threshold:
                alerts.append(WeightChangeAlert(
                    asset=asset,
                    old_weight=0.0,
                    new_weight=round(new_w, 6),
                    change_pct=round(new_w * 100, 2),
                    change_direction="added"
                ))
            continue

        # 기존 자산의 변화
        if change_pct >= threshold:
            direction = "increase" if change > 0 else "decrease"
            alerts.append(WeightChangeAlert(
                asset=asset,
                old_weight=round(old_w, 6),
                new_weight=round(new_w, 6),
                change_pct=round(change_pct * 100, 2),  # 퍼센트로 표시
                change_direction=direction
            ))

    # 턴오버 계산: sum(|new - old|) / 2
    total_turnover = sum(
        abs(new_weights.get(asset, 0) - old_weights.get(asset, 0))
        for asset in all_assets
    ) / 2

    # 가장 큰 변화 찾기
    if all_changes:
        max_change = max(all_changes, key=lambda x: x[1])
        max_change_asset = max_change[0]
        max_change_pct = max_change[1]
    else:
        max_change_asset = None
        max_change_pct = 0.0

    # 알림을 변화 크기순으로 정렬
    alerts.sort(key=lambda x: x.change_pct, reverse=True)

    return WeightComparisonResult(
        total_turnover=round(total_turnover, 6),
        alerts=alerts,
        max_change_asset=max_change_asset,
        max_change_pct=round(max_change_pct * 100, 2)
    )


def calculate_turnover(
    old_weights: dict[str, float],
    new_weights: dict[str, float]
) -> float:
    """
    턴오버 계산

    턴오버 = sum(|new_weight - old_weight|) / 2

    Args:
        old_weights: 기존 비중
        new_weights: 새 비중

    Returns:
        턴오버 (0~1 사이 값)
    """
    all_assets = set(old_weights.keys()) | set(new_weights.keys())

    total_change = sum(
        abs(new_weights.get(asset, 0) - old_weights.get(asset, 0))
        for asset in all_assets
    )

    return total_change / 2


def needs_rebalancing(
    old_weights: dict[str, float],
    new_weights: dict[str, float],
    drift_threshold: float = 0.05,
    turnover_threshold: float = 0.10
) -> tuple[bool, str]:
    """
    리밸런싱 필요 여부 판단

    Args:
        old_weights: 현재 비중
        new_weights: 목표 비중
        drift_threshold: 개별 자산 드리프트 임계값 (5%)
        turnover_threshold: 전체 턴오버 임계값 (10%)

    Returns:
        (필요 여부, 사유)
    """
    comparison = compare_weights(
        old_weights, new_weights,
        threshold=drift_threshold
    )

    # 턴오버 기준
    if comparison.total_turnover >= turnover_threshold:
        return True, f"Total turnover ({comparison.total_turnover:.1%}) exceeds threshold ({turnover_threshold:.1%})"

    # 개별 자산 기준
    if comparison.alerts:
        max_alert = comparison.alerts[0]
        return True, f"Asset {max_alert.asset} changed by {max_alert.change_pct}%"

    return False, "No significant drift detected"
