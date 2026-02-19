"""시장 데이터 드리프트 탐지 서비스

변동성 레짐 변화, 상관관계 붕괴 등 시장 구조 변화를 탐지.
위기 시(COVID 폭락 등) 과거 데이터 기반 모델의 신뢰도 경고.
"""

import numpy as np
from numpy.typing import NDArray
from scipy import stats
from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum

from app.middleware.logging import logger


class DriftSeverity(str, Enum):
    """드리프트 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DriftReport:
    """드리프트 탐지 결과"""
    has_drift: bool
    drift_type: Optional[str]  # "volatility", "correlation", "return", "combined"
    severity: DriftSeverity
    metrics: dict  # 상세 수치
    recommendation: str
    affected_assets: Optional[list[str]] = None


@dataclass
class VolatilityDriftResult:
    """변동성 드리프트 결과"""
    has_drift: bool
    severity: DriftSeverity
    recent_vol: float  # 최근 변동성 (연율화)
    historical_vol: float  # 과거 변동성 (연율화)
    vol_ratio: float  # recent / historical
    max_asset_ratio: float  # 가장 큰 변동성 비율
    high_vol_assets: list[int]  # 변동성 급등 자산 인덱스


@dataclass
class CorrelationDriftResult:
    """상관관계 드리프트 결과"""
    has_drift: bool
    severity: DriftSeverity
    recent_avg_corr: float  # 최근 평균 상관계수
    historical_avg_corr: float  # 과거 평균 상관계수
    max_corr_change: float  # 최대 상관계수 변화
    correlation_increased: bool  # 상관관계 증가 여부 (위기 시 typical)


@dataclass
class CombinedDriftAnalysis:
    """종합 드리프트 분석"""
    volatility: VolatilityDriftResult
    correlation: CorrelationDriftResult
    overall_drift: bool
    overall_severity: DriftSeverity
    market_regime: str  # "normal", "stressed", "crisis"
    recommendations: list[str]


def detect_volatility_drift(
    recent_returns: NDArray[np.float64],
    historical_returns: NDArray[np.float64],
    vol_ratio_threshold: float = 1.5,
    critical_threshold: float = 2.5,
    trading_days: int = 252
) -> VolatilityDriftResult:
    """
    변동성 레짐 변화 탐지

    최근 N일의 변동성이 과거 대비 급등했는지 확인.
    COVID(2020.3), VIX spike 같은 상황 탐지.

    Args:
        recent_returns: 최근 수익률 (T_recent x N)
        historical_returns: 과거 수익률 (T_hist x N)
        vol_ratio_threshold: 변동성 비율 임계값 (1.5 = 50% 증가)
        critical_threshold: 위험 임계값 (2.5 = 150% 증가)
        trading_days: 연간 거래일

    Returns:
        VolatilityDriftResult
    """
    # 개별 자산 변동성
    recent_vol = np.std(recent_returns, axis=0, ddof=1)
    hist_vol = np.std(historical_returns, axis=0, ddof=1)

    # 0으로 나누기 방지
    hist_vol_safe = np.where(hist_vol > 1e-10, hist_vol, 1e-10)
    vol_ratios = recent_vol / hist_vol_safe

    # 포트폴리오 전체 변동성 (동일 비중 가정)
    recent_port_vol = np.std(recent_returns.mean(axis=1)) * np.sqrt(trading_days)
    hist_port_vol = np.std(historical_returns.mean(axis=1)) * np.sqrt(trading_days)

    max_ratio = float(vol_ratios.max())
    avg_ratio = float(vol_ratios.mean())

    # 변동성 급등 자산 찾기
    high_vol_assets = np.where(vol_ratios > vol_ratio_threshold)[0].tolist()

    # 심각도 판단
    if max_ratio > critical_threshold or avg_ratio > 2.0:
        severity = DriftSeverity.CRITICAL
        has_drift = True
    elif max_ratio > vol_ratio_threshold * 1.3 or avg_ratio > 1.5:
        severity = DriftSeverity.HIGH
        has_drift = True
    elif max_ratio > vol_ratio_threshold:
        severity = DriftSeverity.MEDIUM
        has_drift = True
    else:
        severity = DriftSeverity.LOW
        has_drift = False

    if has_drift:
        logger.warning(
            "volatility_drift_detected",
            severity=severity.value,
            max_ratio=max_ratio,
            avg_ratio=avg_ratio,
            n_high_vol_assets=len(high_vol_assets)
        )

    return VolatilityDriftResult(
        has_drift=has_drift,
        severity=severity,
        recent_vol=float(recent_port_vol),
        historical_vol=float(hist_port_vol),
        vol_ratio=avg_ratio,
        max_asset_ratio=max_ratio,
        high_vol_assets=high_vol_assets
    )


def detect_correlation_drift(
    recent_returns: NDArray[np.float64],
    historical_returns: NDArray[np.float64],
    corr_change_threshold: float = 0.2,
    critical_threshold: float = 0.4
) -> CorrelationDriftResult:
    """
    상관관계 구조 변화 탐지

    위기 시 상관관계가 급등(diversification breakdown)하는 현상 탐지.
    "모든 자산이 함께 하락" 상황 경고.

    Args:
        recent_returns: 최근 수익률 (T_recent x N)
        historical_returns: 과거 수익률 (T_hist x N)
        corr_change_threshold: 상관계수 변화 임계값
        critical_threshold: 위험 임계값

    Returns:
        CorrelationDriftResult
    """
    # 단일 자산 처리
    n_assets = recent_returns.shape[1] if recent_returns.ndim > 1 else 1
    if n_assets < 2:
        return CorrelationDriftResult(
            has_drift=False,
            severity=DriftSeverity.LOW,
            recent_avg_corr=0,
            historical_avg_corr=0,
            max_corr_change=0,
            correlation_increased=False
        )

    # 상관 행렬 계산
    recent_corr = np.corrcoef(recent_returns, rowvar=False)
    hist_corr = np.corrcoef(historical_returns, rowvar=False)

    # NaN 처리
    if np.any(np.isnan(recent_corr)):
        recent_corr = np.nan_to_num(recent_corr, nan=0)
    if np.any(np.isnan(hist_corr)):
        hist_corr = np.nan_to_num(hist_corr, nan=0)

    # 상삼각 행렬만 추출 (중복 제거)
    n = recent_corr.shape[0] if recent_corr.ndim > 1 else 1
    if n < 2:
        return CorrelationDriftResult(
            has_drift=False,
            severity=DriftSeverity.LOW,
            recent_avg_corr=0,
            historical_avg_corr=0,
            max_corr_change=0,
            correlation_increased=False
        )

    triu_idx = np.triu_indices(n, k=1)
    recent_corrs = recent_corr[triu_idx]
    hist_corrs = hist_corr[triu_idx]

    # 평균 상관계수
    recent_avg = float(np.mean(recent_corrs))
    hist_avg = float(np.mean(hist_corrs))

    # 상관계수 변화
    corr_diff = recent_corr - hist_corr
    np.fill_diagonal(corr_diff, 0)
    max_change = float(np.abs(corr_diff).max())
    mean_change = float(np.abs(corr_diff[triu_idx]).mean())

    # 상관관계 증가 여부 (위기 시 typical)
    correlation_increased = recent_avg > hist_avg + 0.1

    # 심각도 판단
    if max_change > critical_threshold or (correlation_increased and recent_avg > 0.7):
        severity = DriftSeverity.CRITICAL
        has_drift = True
    elif max_change > corr_change_threshold * 1.5 or (correlation_increased and recent_avg > 0.5):
        severity = DriftSeverity.HIGH
        has_drift = True
    elif max_change > corr_change_threshold:
        severity = DriftSeverity.MEDIUM
        has_drift = True
    else:
        severity = DriftSeverity.LOW
        has_drift = False

    if has_drift:
        logger.warning(
            "correlation_drift_detected",
            severity=severity.value,
            recent_avg_corr=recent_avg,
            hist_avg_corr=hist_avg,
            max_change=max_change,
            correlation_increased=correlation_increased
        )

    return CorrelationDriftResult(
        has_drift=has_drift,
        severity=severity,
        recent_avg_corr=recent_avg,
        historical_avg_corr=hist_avg,
        max_corr_change=max_change,
        correlation_increased=correlation_increased
    )


def detect_return_distribution_shift(
    recent_returns: NDArray[np.float64],
    historical_returns: NDArray[np.float64],
    significance_level: float = 0.05
) -> tuple[bool, float, str]:
    """
    수익률 분포 변화 탐지 (Kolmogorov-Smirnov test)

    Args:
        recent_returns: 최근 수익률
        historical_returns: 과거 수익률
        significance_level: 유의수준

    Returns:
        (has_shift, p_value, interpretation)
    """
    # 포트폴리오 수익률 (동일 비중)
    recent_port = recent_returns.mean(axis=1)
    hist_port = historical_returns.mean(axis=1)

    # KS test
    statistic, p_value = stats.ks_2samp(recent_port, hist_port)

    has_shift = p_value < significance_level

    if has_shift:
        if p_value < 0.001:
            interpretation = "Strong evidence of distribution change"
        elif p_value < 0.01:
            interpretation = "Significant distribution change"
        else:
            interpretation = "Moderate distribution change"
    else:
        interpretation = "No significant distribution change"

    return has_shift, float(p_value), interpretation


def analyze_drift(
    recent_returns: NDArray[np.float64],
    historical_returns: NDArray[np.float64],
    asset_names: Optional[list[str]] = None,
    vol_threshold: float = 1.5,
    corr_threshold: float = 0.2
) -> CombinedDriftAnalysis:
    """
    종합 드리프트 분석

    변동성, 상관관계, 분포 변화를 종합 분석하여
    시장 레짐과 권장 조치 제공.

    Args:
        recent_returns: 최근 수익률 (T_recent x N)
        historical_returns: 과거 수익률 (T_hist x N)
        asset_names: 자산 이름 리스트 (로깅용)
        vol_threshold: 변동성 드리프트 임계값
        corr_threshold: 상관관계 드리프트 임계값

    Returns:
        CombinedDriftAnalysis
    """
    # 개별 드리프트 탐지
    vol_drift = detect_volatility_drift(
        recent_returns, historical_returns,
        vol_ratio_threshold=vol_threshold
    )
    corr_drift = detect_correlation_drift(
        recent_returns, historical_returns,
        corr_change_threshold=corr_threshold
    )

    # 종합 심각도 결정
    severities = [vol_drift.severity, corr_drift.severity]
    if DriftSeverity.CRITICAL in severities:
        overall_severity = DriftSeverity.CRITICAL
    elif DriftSeverity.HIGH in severities:
        overall_severity = DriftSeverity.HIGH
    elif DriftSeverity.MEDIUM in severities:
        overall_severity = DriftSeverity.MEDIUM
    else:
        overall_severity = DriftSeverity.LOW

    overall_drift = vol_drift.has_drift or corr_drift.has_drift

    # 시장 레짐 판단
    if overall_severity == DriftSeverity.CRITICAL:
        market_regime = "crisis"
    elif overall_severity == DriftSeverity.HIGH:
        market_regime = "stressed"
    else:
        market_regime = "normal"

    # 권장 조치 생성
    recommendations = []

    if vol_drift.has_drift:
        if vol_drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            recommendations.append(
                f"VOLATILITY: Reduce position sizes by {min(50, int(vol_drift.vol_ratio * 20))}%"
            )
            recommendations.append(
                "VOLATILITY: Consider shorter lookback window for optimization"
            )
        else:
            recommendations.append(
                "VOLATILITY: Monitor closely, volatility elevated"
            )

        if vol_drift.high_vol_assets and asset_names:
            high_vol_names = [
                asset_names[i] for i in vol_drift.high_vol_assets
                if i < len(asset_names)
            ]
            if high_vol_names:
                recommendations.append(
                    f"VOLATILITY: High-vol assets: {', '.join(high_vol_names[:5])}"
                )

    if corr_drift.has_drift:
        if corr_drift.correlation_increased:
            recommendations.append(
                "CORRELATION: Diversification benefit reduced - "
                "portfolio may be riskier than expected"
            )
        if corr_drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            recommendations.append(
                "CORRELATION: Consider hedging or reducing exposure"
            )

    if not recommendations:
        recommendations.append("No action needed - market conditions stable")

    # 로깅
    logger.info(
        "drift_analysis_completed",
        overall_drift=overall_drift,
        overall_severity=overall_severity.value,
        market_regime=market_regime,
        vol_ratio=vol_drift.vol_ratio,
        corr_change=corr_drift.max_corr_change
    )

    return CombinedDriftAnalysis(
        volatility=vol_drift,
        correlation=corr_drift,
        overall_drift=overall_drift,
        overall_severity=overall_severity,
        market_regime=market_regime,
        recommendations=recommendations
    )


def create_drift_report(
    analysis: CombinedDriftAnalysis,
    asset_names: Optional[list[str]] = None
) -> DriftReport:
    """
    드리프트 분석 결과를 API 응답용 리포트로 변환

    Args:
        analysis: 종합 드리프트 분석 결과
        asset_names: 자산 이름 리스트

    Returns:
        DriftReport
    """
    # 드리프트 타입 결정
    if analysis.volatility.has_drift and analysis.correlation.has_drift:
        drift_type = "combined"
    elif analysis.volatility.has_drift:
        drift_type = "volatility"
    elif analysis.correlation.has_drift:
        drift_type = "correlation"
    else:
        drift_type = None

    # 영향받는 자산
    affected_assets = None
    if analysis.volatility.high_vol_assets and asset_names:
        affected_assets = [
            asset_names[i] for i in analysis.volatility.high_vol_assets
            if i < len(asset_names)
        ]

    # 메트릭 수집
    metrics = {
        "volatility": {
            "recent": analysis.volatility.recent_vol,
            "historical": analysis.volatility.historical_vol,
            "ratio": analysis.volatility.vol_ratio,
            "max_asset_ratio": analysis.volatility.max_asset_ratio
        },
        "correlation": {
            "recent_avg": analysis.correlation.recent_avg_corr,
            "historical_avg": analysis.correlation.historical_avg_corr,
            "max_change": analysis.correlation.max_corr_change,
            "increased": analysis.correlation.correlation_increased
        },
        "market_regime": analysis.market_regime
    }

    # 주요 권장사항
    main_recommendation = analysis.recommendations[0] if analysis.recommendations else ""

    return DriftReport(
        has_drift=analysis.overall_drift,
        drift_type=drift_type,
        severity=analysis.overall_severity,
        metrics=metrics,
        recommendation=main_recommendation,
        affected_assets=affected_assets
    )
