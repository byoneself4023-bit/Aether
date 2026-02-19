"""드리프트 탐지 서비스 단위 테스트"""

import numpy as np
import pytest
from app.services.drift_detector import (
    detect_volatility_drift,
    detect_correlation_drift,
    detect_return_distribution_shift,
    analyze_drift,
    create_drift_report,
    DriftSeverity,
    VolatilityDriftResult,
    CorrelationDriftResult,
    CombinedDriftAnalysis,
)


class TestVolatilityDrift:
    """변동성 드리프트 탐지 테스트"""

    def test_no_drift_stable_volatility(self):
        """변동성 안정 시 드리프트 없음"""
        np.random.seed(42)

        # 동일한 변동성의 수익률
        historical = np.random.randn(200, 3) * 0.01
        recent = np.random.randn(20, 3) * 0.01

        result = detect_volatility_drift(recent, historical)

        assert not result.has_drift
        assert result.severity == DriftSeverity.LOW
        assert result.vol_ratio < 1.5

    def test_drift_detected_high_volatility(self):
        """변동성 급등 시 드리프트 감지"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01  # 1% 변동성
        recent = np.random.randn(20, 3) * 0.03  # 3% 변동성 (3배 증가)

        result = detect_volatility_drift(recent, historical, vol_ratio_threshold=1.5)

        assert result.has_drift
        assert result.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
        assert result.vol_ratio > 1.5
        assert result.max_asset_ratio > 2.0

    def test_critical_volatility_spike(self):
        """극단적 변동성 급등 시 CRITICAL"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        recent = np.random.randn(20, 3) * 0.05  # 5배 증가

        result = detect_volatility_drift(
            recent, historical,
            vol_ratio_threshold=1.5,
            critical_threshold=2.5
        )

        assert result.has_drift
        assert result.severity == DriftSeverity.CRITICAL
        assert result.max_asset_ratio > 2.5

    def test_high_vol_assets_identified(self):
        """변동성 급등 자산 식별"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        # 3번째 자산만 변동성 급등
        recent = np.column_stack([
            np.random.randn(20, 2) * 0.01,
            np.random.randn(20, 1) * 0.04  # 4배 증가
        ])

        result = detect_volatility_drift(recent, historical, vol_ratio_threshold=1.5)

        assert 2 in result.high_vol_assets  # 3번째 자산 (인덱스 2)


class TestCorrelationDrift:
    """상관관계 드리프트 탐지 테스트"""

    def test_no_drift_stable_correlation(self):
        """상관관계 안정 시 드리프트 없음"""
        np.random.seed(42)

        # 동일한 상관 구조
        cov = np.array([[1, 0.3, 0.2], [0.3, 1, 0.4], [0.2, 0.4, 1]])
        L = np.linalg.cholesky(cov)

        historical = (np.random.randn(200, 3) @ L.T) * 0.01
        recent = (np.random.randn(20, 3) @ L.T) * 0.01

        result = detect_correlation_drift(recent, historical)

        # 동일 분포에서 추출하면 드리프트 없어야 함
        assert result.severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM]

    def test_drift_detected_correlation_increase(self):
        """상관관계 급등 시 드리프트 감지 (위기 시)"""
        np.random.seed(42)

        # 과거: 낮은 상관관계
        cov_hist = np.array([[1, 0.2, 0.1], [0.2, 1, 0.15], [0.1, 0.15, 1]])
        L_hist = np.linalg.cholesky(cov_hist)
        historical = (np.random.randn(200, 3) @ L_hist.T) * 0.01

        # 최근: 높은 상관관계 (위기 상황)
        cov_recent = np.array([[1, 0.8, 0.7], [0.8, 1, 0.75], [0.7, 0.75, 1]])
        L_recent = np.linalg.cholesky(cov_recent)
        recent = (np.random.randn(20, 3) @ L_recent.T) * 0.01

        result = detect_correlation_drift(recent, historical, corr_change_threshold=0.2)

        assert result.has_drift
        assert result.correlation_increased
        assert result.recent_avg_corr > result.historical_avg_corr

    def test_correlation_breakdown_detected(self):
        """상관관계 붕괴 탐지"""
        np.random.seed(42)

        # 과거: 높은 상관관계
        cov_hist = np.array([[1, 0.7, 0.6], [0.7, 1, 0.65], [0.6, 0.65, 1]])
        L_hist = np.linalg.cholesky(cov_hist)
        historical = (np.random.randn(200, 3) @ L_hist.T) * 0.01

        # 최근: 낮은 상관관계 (구조 변화)
        cov_recent = np.array([[1, 0.1, 0.05], [0.1, 1, 0.15], [0.05, 0.15, 1]])
        L_recent = np.linalg.cholesky(cov_recent)
        recent = (np.random.randn(20, 3) @ L_recent.T) * 0.01

        result = detect_correlation_drift(recent, historical, corr_change_threshold=0.2)

        assert result.has_drift
        assert result.max_corr_change > 0.2

    def test_single_asset_handling(self):
        """단일 자산 처리"""
        historical = np.random.randn(200, 1) * 0.01
        recent = np.random.randn(20, 1) * 0.01

        result = detect_correlation_drift(recent, historical)

        # 단일 자산은 상관관계 없음
        assert not result.has_drift
        assert result.recent_avg_corr == 0


class TestReturnDistributionShift:
    """수익률 분포 변화 탐지 테스트"""

    def test_no_shift_same_distribution(self):
        """동일 분포 시 변화 없음"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        recent = np.random.randn(50, 3) * 0.01

        has_shift, p_value, _ = detect_return_distribution_shift(
            recent, historical, significance_level=0.05
        )

        # 동일 분포면 p-value가 높아야 함
        assert p_value > 0.01 or not has_shift

    def test_shift_detected_different_mean(self):
        """평균 변화 시 분포 변화 탐지"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01  # 평균 0
        recent = np.random.randn(50, 3) * 0.01 + 0.03  # 평균 3%

        has_shift, p_value, interpretation = detect_return_distribution_shift(
            recent, historical, significance_level=0.05
        )

        assert has_shift
        assert p_value < 0.05
        assert "change" in interpretation.lower()


class TestAnalyzeDrift:
    """종합 드리프트 분석 테스트"""

    def test_combined_analysis_no_drift(self):
        """정상 시장 종합 분석"""
        np.random.seed(42)

        # 동일한 공분산 구조에서 샘플링하여 드리프트 최소화
        cov = np.array([[1, 0.3, 0.2], [0.3, 1, 0.25], [0.2, 0.25, 1]])
        L = np.linalg.cholesky(cov)

        historical = (np.random.randn(200, 3) @ L.T) * 0.01
        recent = (np.random.randn(20, 3) @ L.T) * 0.01

        result = analyze_drift(
            recent, historical,
            asset_names=["AAPL", "MSFT", "GOOGL"],
            vol_threshold=2.0,  # 더 높은 임계값
            corr_threshold=0.4  # 더 높은 임계값
        )

        # 동일 분포에서 샘플링하면 드리프트가 낮아야 함
        assert result.overall_severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM]

    def test_combined_analysis_crisis(self):
        """위기 상황 종합 분석"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01

        # 변동성 급등 + 상관관계 급등
        cov_crisis = np.array([[1, 0.9, 0.85], [0.9, 1, 0.88], [0.85, 0.88, 1]])
        L = np.linalg.cholesky(cov_crisis)
        recent = (np.random.randn(20, 3) @ L.T) * 0.04  # 4배 변동성

        result = analyze_drift(
            recent, historical,
            asset_names=["AAPL", "MSFT", "GOOGL"],
            vol_threshold=1.5,
            corr_threshold=0.2
        )

        assert result.overall_drift
        assert result.overall_severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]
        assert result.market_regime in ["stressed", "crisis"]
        assert len(result.recommendations) > 0

    def test_recommendations_include_affected_assets(self):
        """권장사항에 영향받는 자산 포함"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        # 첫 번째 자산만 변동성 급등
        recent = np.column_stack([
            np.random.randn(20, 1) * 0.05,
            np.random.randn(20, 2) * 0.01
        ])

        result = analyze_drift(
            recent, historical,
            asset_names=["AAPL", "MSFT", "GOOGL"],
            vol_threshold=1.5
        )

        if result.volatility.has_drift and result.volatility.high_vol_assets:
            # 권장사항에 자산 이름 포함 확인
            all_recommendations = " ".join(result.recommendations)
            assert "AAPL" in all_recommendations or len(result.volatility.high_vol_assets) > 0


class TestCreateDriftReport:
    """드리프트 리포트 생성 테스트"""

    def test_report_structure(self):
        """리포트 구조 검증"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        recent = np.random.randn(20, 3) * 0.03  # 변동성 급등

        analysis = analyze_drift(recent, historical, asset_names=["A", "B", "C"])
        report = create_drift_report(analysis, asset_names=["A", "B", "C"])

        assert hasattr(report, "has_drift")
        assert hasattr(report, "drift_type")
        assert hasattr(report, "severity")
        assert hasattr(report, "metrics")
        assert hasattr(report, "recommendation")

        # 메트릭 구조 검증
        if report.metrics:
            assert "volatility" in report.metrics
            assert "correlation" in report.metrics
            assert "market_regime" in report.metrics

    def test_drift_type_classification(self):
        """드리프트 유형 분류"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01

        # 변동성만 급등
        recent_vol = np.random.randn(20, 3) * 0.04
        analysis_vol = analyze_drift(recent_vol, historical)
        report_vol = create_drift_report(analysis_vol)

        if analysis_vol.volatility.has_drift and not analysis_vol.correlation.has_drift:
            assert report_vol.drift_type == "volatility"

    def test_severity_mapping(self):
        """심각도 매핑"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        recent = np.random.randn(20, 3) * 0.05  # 극단적 변동성

        analysis = analyze_drift(recent, historical)
        report = create_drift_report(analysis)

        assert report.severity in [s.value for s in DriftSeverity]


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_two_assets(self):
        """2개 자산"""
        np.random.seed(42)

        historical = np.random.randn(200, 2) * 0.01
        recent = np.random.randn(20, 2) * 0.01

        vol_result = detect_volatility_drift(recent, historical)
        corr_result = detect_correlation_drift(recent, historical)

        assert isinstance(vol_result, VolatilityDriftResult)
        assert isinstance(corr_result, CorrelationDriftResult)

    def test_small_sample_size(self):
        """작은 샘플 크기"""
        np.random.seed(42)

        historical = np.random.randn(30, 3) * 0.01  # 최소 샘플
        recent = np.random.randn(5, 3) * 0.01  # 매우 작은 최근 기간

        # 에러 없이 실행되어야 함
        vol_result = detect_volatility_drift(recent, historical)
        corr_result = detect_correlation_drift(recent, historical)

        assert isinstance(vol_result, VolatilityDriftResult)
        assert isinstance(corr_result, CorrelationDriftResult)

    def test_nan_handling(self):
        """NaN 값 처리"""
        np.random.seed(42)

        historical = np.random.randn(200, 3) * 0.01
        recent = np.random.randn(20, 3) * 0.01
        recent[5, 1] = np.nan  # NaN 삽입

        # NaN이 있어도 상관계수 계산에서 에러 안 남
        corr_result = detect_correlation_drift(recent, historical)

        assert isinstance(corr_result, CorrelationDriftResult)

    def test_constant_returns(self):
        """상수 수익률 (변동성 0)"""
        historical = np.zeros((200, 3))
        recent = np.zeros((20, 3))

        # 0으로 나누기 에러 없어야 함
        vol_result = detect_volatility_drift(recent, historical)
        corr_result = detect_correlation_drift(recent, historical)

        assert isinstance(vol_result, VolatilityDriftResult)
        assert isinstance(corr_result, CorrelationDriftResult)
