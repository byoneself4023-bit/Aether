"""비중 모니터링 서비스 테스트"""

import pytest
from app.services.weight_monitor import (
    compare_weights,
    calculate_turnover,
    needs_rebalancing,
    WeightChangeAlert,
    WeightComparisonResult,
)


class TestCompareWeights:
    """compare_weights 함수 테스트"""

    def test_no_change(self):
        """변화 없는 경우"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.5, "GOOGL": 0.5}

        result = compare_weights(old, new, threshold=0.1)

        assert result.total_turnover == 0.0
        assert len(result.alerts) == 0
        assert result.max_change_pct == 0.0

    def test_small_change_below_threshold(self):
        """임계값 이하의 작은 변화"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.55, "GOOGL": 0.45}  # 5% 변화

        result = compare_weights(old, new, threshold=0.1)  # 10% 임계값

        assert result.total_turnover == 0.05
        assert len(result.alerts) == 0  # 임계값 이하이므로 알림 없음

    def test_large_change_above_threshold(self):
        """임계값 초과 변화"""
        old = {"AAPL": 0.3, "GOOGL": 0.7}
        new = {"AAPL": 0.6, "GOOGL": 0.4}  # AAPL +30%, GOOGL -30%

        result = compare_weights(old, new, threshold=0.1)

        assert len(result.alerts) == 2
        # 변화 크기순으로 정렬됨
        assert result.alerts[0].change_pct == 30.0  # 30% 변화
        assert result.max_change_pct == 30.0

    def test_asset_added(self):
        """새 자산 추가"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.4, "GOOGL": 0.4, "MSFT": 0.2}

        result = compare_weights(old, new, threshold=0.1)

        # MSFT 추가 (20% > 10% 임계값)
        added_alerts = [a for a in result.alerts if a.change_direction == "added"]
        assert len(added_alerts) == 1
        assert added_alerts[0].asset == "MSFT"
        assert added_alerts[0].new_weight == 0.2

    def test_asset_removed(self):
        """자산 제거"""
        old = {"AAPL": 0.4, "GOOGL": 0.4, "MSFT": 0.2}
        new = {"AAPL": 0.5, "GOOGL": 0.5}

        result = compare_weights(old, new, threshold=0.1)

        # MSFT 제거 (20% > 10% 임계값)
        removed_alerts = [a for a in result.alerts if a.change_direction == "removed"]
        assert len(removed_alerts) == 1
        assert removed_alerts[0].asset == "MSFT"
        assert removed_alerts[0].old_weight == 0.2

    def test_turnover_calculation(self):
        """턴오버 계산"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.7, "GOOGL": 0.3}  # 각 0.2 변화

        result = compare_weights(old, new, threshold=0.1)

        # 턴오버 = sum(|changes|) / 2 = (0.2 + 0.2) / 2 = 0.2
        assert result.total_turnover == 0.2

    def test_max_change_asset(self):
        """가장 큰 변화 자산 식별"""
        old = {"AAPL": 0.3, "GOOGL": 0.3, "MSFT": 0.4}
        new = {"AAPL": 0.5, "GOOGL": 0.35, "MSFT": 0.15}  # MSFT 가장 큰 변화

        result = compare_weights(old, new, threshold=0.1)

        assert result.max_change_asset == "MSFT"
        assert result.max_change_pct == 25.0  # 40% -> 15% = 25% 변화

    def test_custom_threshold(self):
        """커스텀 임계값"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.55, "GOOGL": 0.45}  # 5% 변화

        # 3% 임계값 -> 알림 발생
        result_low = compare_weights(old, new, threshold=0.03)
        assert len(result_low.alerts) == 2

        # 10% 임계값 -> 알림 없음
        result_high = compare_weights(old, new, threshold=0.10)
        assert len(result_high.alerts) == 0

    def test_direction_increase(self):
        """증가 방향 표시"""
        old = {"AAPL": 0.3}
        new = {"AAPL": 0.6}

        result = compare_weights(old, new, threshold=0.1)

        assert result.alerts[0].change_direction == "increase"

    def test_direction_decrease(self):
        """감소 방향 표시"""
        old = {"AAPL": 0.6}
        new = {"AAPL": 0.3}

        result = compare_weights(old, new, threshold=0.1)

        assert result.alerts[0].change_direction == "decrease"


class TestCalculateTurnover:
    """calculate_turnover 함수 테스트"""

    def test_zero_turnover(self):
        """동일 비중 -> 턴오버 0"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.5, "GOOGL": 0.5}

        assert calculate_turnover(old, new) == 0.0

    def test_full_turnover(self):
        """완전 교체 -> 턴오버 1"""
        old = {"AAPL": 1.0}
        new = {"GOOGL": 1.0}

        assert calculate_turnover(old, new) == 1.0

    def test_partial_turnover(self):
        """부분 턴오버"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.8, "GOOGL": 0.2}

        # |0.8-0.5| + |0.2-0.5| = 0.3 + 0.3 = 0.6 / 2 = 0.3
        assert calculate_turnover(old, new) == pytest.approx(0.3)


class TestNeedsRebalancing:
    """needs_rebalancing 함수 테스트"""

    def test_no_rebalancing_needed(self):
        """리밸런싱 불필요"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.51, "GOOGL": 0.49}

        needs, reason = needs_rebalancing(old, new)

        assert needs is False
        assert "No significant drift" in reason

    def test_rebalancing_by_turnover(self):
        """턴오버 기준 리밸런싱 필요"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.7, "GOOGL": 0.3}  # 턴오버 0.2

        needs, reason = needs_rebalancing(
            old, new,
            drift_threshold=0.3,  # 높은 드리프트 임계값
            turnover_threshold=0.1  # 낮은 턴오버 임계값
        )

        assert needs is True
        assert "turnover" in reason.lower()

    def test_rebalancing_by_asset_drift(self):
        """개별 자산 드리프트 기준 리밸런싱 필요"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {"AAPL": 0.6, "GOOGL": 0.4}  # 10% 드리프트

        needs, reason = needs_rebalancing(
            old, new,
            drift_threshold=0.08,  # 8% 드리프트 임계값
            turnover_threshold=0.5  # 높은 턴오버 임계값
        )

        assert needs is True
        assert "AAPL" in reason or "GOOGL" in reason


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_empty_old_weights(self):
        """빈 기존 비중 (신규 포트폴리오)"""
        old = {}
        new = {"AAPL": 0.5, "GOOGL": 0.5}

        result = compare_weights(old, new, threshold=0.1)

        assert result.total_turnover == 0.5  # 전체 추가
        assert len(result.alerts) == 2  # 모두 added

    def test_empty_new_weights(self):
        """빈 새 비중 (청산)"""
        old = {"AAPL": 0.5, "GOOGL": 0.5}
        new = {}

        result = compare_weights(old, new, threshold=0.1)

        assert result.total_turnover == 0.5  # 전체 제거
        assert len(result.alerts) == 2  # 모두 removed

    def test_single_asset(self):
        """단일 자산"""
        old = {"AAPL": 1.0}
        new = {"AAPL": 1.0}

        result = compare_weights(old, new, threshold=0.1)

        assert result.total_turnover == 0.0
        assert len(result.alerts) == 0

    def test_very_small_weights(self):
        """매우 작은 비중"""
        old = {"AAPL": 0.001, "GOOGL": 0.999}
        new = {"AAPL": 0.002, "GOOGL": 0.998}

        result = compare_weights(old, new, threshold=0.001)

        # 0.1% 변화는 0.1% 임계값 이상
        assert len(result.alerts) == 2

    def test_rounding(self):
        """반올림 정확성"""
        old = {"AAPL": 0.333333333}
        new = {"AAPL": 0.666666666}

        result = compare_weights(old, new, threshold=0.1)

        # 비중이 적절히 반올림되어야 함
        assert result.alerts[0].old_weight == 0.333333
        assert result.alerts[0].new_weight == 0.666667
