"""Portfolio Client 테스트 - Mock으로 API 호출 없이 테스트"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from app.services.portfolio_client import (
    get_optimization,
    get_risk_analysis,
    get_backtest,
    get_full_analysis,
    check_health,
    is_available,
    get_service_url,
    PortfolioServiceError,
    PortfolioServiceUnavailable,
    _make_request,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def sample_tickers():
    return ["AAPL", "GOOGL", "MSFT", "NVDA"]


@pytest.fixture
def sample_weights():
    return {
        "AAPL": 0.25,
        "GOOGL": 0.25,
        "MSFT": 0.25,
        "NVDA": 0.25,
    }


@pytest.fixture
def mock_optimization_response():
    return {
        "weights": {
            "AAPL": 0.30,
            "GOOGL": 0.25,
            "MSFT": 0.25,
            "NVDA": 0.20,
        },
        "metrics": {
            "expected_return": 0.326,
            "volatility": 0.224,
            "sharpe_ratio": 2.09,
        },
        "n_stocks": 4,
        "strategy": "max_sharpe",
        "period": "3y",
        "frontier": None,
    }


@pytest.fixture
def mock_risk_response():
    return {
        "parametric_var": {
            "value": 0.018,
            "confidence": 0.95,
            "holding_days": 1,
            "method": "parametric",
        },
        "monte_carlo_var": {
            "value": 0.019,
            "confidence": 0.95,
            "holding_days": 1,
            "method": "monte_carlo",
        },
        "cvar": 0.024,
        "risk_summary": {
            "volatility": 0.224,
            "expected_return": 0.326,
            "var_95_parametric": 0.018,
            "var_99_parametric": 0.026,
            "var_95_montecarlo": 0.019,
            "var_99_montecarlo": 0.027,
            "cvar_95": 0.024,
            "cvar_99": 0.035,
            "max_loss_1d": 0.045,
        },
    }


@pytest.fixture
def mock_backtest_response():
    return {
        "metrics": {
            "total_return": 1.28,
            "annual_return": 0.426,
            "annual_volatility": 0.22,
            "sharpe_ratio": 1.94,
            "max_drawdown": 0.136,
            "calmar_ratio": 3.13,
            "avg_turnover": 0.15,
            "win_rate": 0.54,
        },
        "portfolio_values": [
            {"date": "2022-01-03", "value": 1.0},
            {"date": "2022-01-04", "value": 1.01},
        ],
        "rebalance_count": 12,
        "rebalance_history": [],
        "strategy": "max_sharpe",
        "tickers": ["AAPL", "GOOGL", "MSFT", "NVDA"],
        "final_weights": {
            "AAPL": 0.30,
            "GOOGL": 0.25,
            "MSFT": 0.25,
            "NVDA": 0.20,
        },
    }


@pytest.fixture
def mock_health_response():
    return {
        "status": "healthy",
        "service": "portfolio-service",
        "version": "1.0.0",
    }


# ============================================================
# _make_request 테스트
# ============================================================

class TestMakeRequest:
    @pytest.mark.asyncio
    async def test_successful_request(self, mock_optimization_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_optimization_response

        with patch("app.services.portfolio_client._get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_get_client.return_value = mock_client

            result = await _make_request("POST", "/api/optimize", {"tickers": ["AAPL"]})

            assert result == mock_optimization_response

    @pytest.mark.asyncio
    async def test_api_error_response(self):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid tickers"}

        with patch("app.services.portfolio_client._get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_get_client.return_value = mock_client

            with pytest.raises(PortfolioServiceError) as exc_info:
                await _make_request("POST", "/api/optimize", {})

            assert exc_info.value.status_code == 400
            assert "Invalid tickers" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_connection_error(self):
        with patch("app.services.portfolio_client._get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.request.side_effect = httpx.ConnectError("Connection refused")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_get_client.return_value = mock_client

            with pytest.raises(PortfolioServiceUnavailable) as exc_info:
                await _make_request("POST", "/api/optimize", {})

            assert "unavailable" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        with patch("app.services.portfolio_client._get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.request.side_effect = httpx.TimeoutException("Timeout")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_get_client.return_value = mock_client

            with pytest.raises(PortfolioServiceError) as exc_info:
                await _make_request("POST", "/api/backtest", {})

            assert "timeout" in str(exc_info.value).lower()


# ============================================================
# get_optimization 테스트
# ============================================================

class TestGetOptimization:
    @pytest.mark.asyncio
    async def test_optimization_success(
        self,
        sample_tickers,
        mock_optimization_response,
    ):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_optimization_response

            result = await get_optimization(
                tickers=sample_tickers,
                strategy="max_sharpe",
                period="3y",
            )

            assert "weights" in result
            assert "metrics" in result
            assert result["strategy"] == "max_sharpe"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_optimization_with_frontier(
        self,
        sample_tickers,
        mock_optimization_response,
    ):
        mock_optimization_response["frontier"] = [{"return": 0.1, "volatility": 0.15}]

        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_optimization_response

            result = await get_optimization(
                tickers=sample_tickers,
                strategy="min_variance",
                include_frontier=True,
            )

            call_args = mock_request.call_args
            assert call_args[1]["json_data"]["include_frontier"] is True

    @pytest.mark.asyncio
    async def test_optimization_min_variance(
        self,
        sample_tickers,
        mock_optimization_response,
    ):
        mock_optimization_response["strategy"] = "min_variance"

        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_optimization_response

            result = await get_optimization(
                tickers=sample_tickers,
                strategy="min_variance",
            )

            call_args = mock_request.call_args
            assert call_args[1]["json_data"]["strategy"] == "min_variance"


# ============================================================
# get_risk_analysis 테스트
# ============================================================

class TestGetRiskAnalysis:
    @pytest.mark.asyncio
    async def test_risk_analysis_success(
        self,
        sample_tickers,
        sample_weights,
        mock_risk_response,
    ):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_risk_response

            result = await get_risk_analysis(
                tickers=sample_tickers,
                weights=sample_weights,
                confidence=0.95,
            )

            assert "parametric_var" in result
            assert "monte_carlo_var" in result
            assert "cvar" in result
            assert "risk_summary" in result

    @pytest.mark.asyncio
    async def test_risk_analysis_custom_confidence(
        self,
        sample_tickers,
        sample_weights,
        mock_risk_response,
    ):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_risk_response

            await get_risk_analysis(
                tickers=sample_tickers,
                weights=sample_weights,
                confidence=0.99,
                n_simulations=5000,
            )

            call_args = mock_request.call_args
            assert call_args[1]["json_data"]["confidence"] == 0.99
            assert call_args[1]["json_data"]["n_simulations"] == 5000


# ============================================================
# get_backtest 테스트
# ============================================================

class TestGetBacktest:
    @pytest.mark.asyncio
    async def test_backtest_success(
        self,
        sample_tickers,
        mock_backtest_response,
    ):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_backtest_response

            result = await get_backtest(
                tickers=sample_tickers,
                strategy="max_sharpe",
                period="5y",
            )

            assert "metrics" in result
            assert "portfolio_values" in result
            assert "rebalance_count" in result
            assert result["metrics"]["total_return"] == 1.28

    @pytest.mark.asyncio
    async def test_backtest_custom_params(
        self,
        sample_tickers,
        mock_backtest_response,
    ):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.return_value = mock_backtest_response

            await get_backtest(
                tickers=sample_tickers,
                strategy="min_variance",
                period="10y",
                train_window=504,
                rebalance_every=126,
                transaction_cost=0.002,
                use_shrinkage=False,
            )

            call_args = mock_request.call_args
            json_data = call_args[1]["json_data"]
            assert json_data["train_window"] == 504
            assert json_data["rebalance_every"] == 126
            assert json_data["transaction_cost"] == 0.002
            assert json_data["use_shrinkage"] is False


# ============================================================
# get_full_analysis 테스트
# ============================================================

class TestGetFullAnalysis:
    @pytest.mark.asyncio
    async def test_full_analysis_success(
        self,
        sample_tickers,
        mock_optimization_response,
        mock_risk_response,
        mock_backtest_response,
    ):
        with patch("app.services.portfolio_client.get_optimization") as mock_opt, \
             patch("app.services.portfolio_client.get_risk_analysis") as mock_risk, \
             patch("app.services.portfolio_client.get_backtest") as mock_bt:

            mock_opt.return_value = mock_optimization_response
            mock_risk.return_value = mock_risk_response
            mock_bt.return_value = mock_backtest_response

            result = await get_full_analysis(
                tickers=sample_tickers,
                strategy="max_sharpe",
            )

            assert "optimization" in result
            assert "risk" in result
            assert "backtest" in result
            assert "summary" in result

            # summary 검증
            summary = result["summary"]
            assert summary["tickers"] == sample_tickers
            assert summary["strategy"] == "max_sharpe"
            assert "weights" in summary
            assert "expected_return" in summary
            assert "sharpe_ratio" in summary
            assert "var_95" in summary
            assert "max_drawdown" in summary

    @pytest.mark.asyncio
    async def test_full_analysis_calls_all_apis(
        self,
        sample_tickers,
        mock_optimization_response,
        mock_risk_response,
        mock_backtest_response,
    ):
        with patch("app.services.portfolio_client.get_optimization") as mock_opt, \
             patch("app.services.portfolio_client.get_risk_analysis") as mock_risk, \
             patch("app.services.portfolio_client.get_backtest") as mock_bt:

            mock_opt.return_value = mock_optimization_response
            mock_risk.return_value = mock_risk_response
            mock_bt.return_value = mock_backtest_response

            await get_full_analysis(
                tickers=sample_tickers,
                strategy="min_variance",
                period="1y",
                backtest_period="3y",
            )

            # 모든 API가 호출되었는지 확인
            mock_opt.assert_called_once()
            mock_risk.assert_called_once()
            mock_bt.assert_called_once()

            # 최적화 결과의 비중이 리스크 분석에 전달되었는지 확인
            risk_call_args = mock_risk.call_args
            assert risk_call_args[1]["weights"] == mock_optimization_response["weights"]


# ============================================================
# 헬스체크 및 유틸리티 테스트
# ============================================================

class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_health_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_health_response

        with patch("app.services.portfolio_client._get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_get_client.return_value = mock_client

            result = await check_health()

            assert result["status"] == "healthy"
            assert result["service"] == "portfolio-service"

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        with patch("app.services.portfolio_client._get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_get_client.return_value = mock_client

            result = await check_health()

            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_is_available_true(self, mock_health_response):
        with patch("app.services.portfolio_client.check_health") as mock_health:
            mock_health.return_value = mock_health_response

            result = await is_available()

            assert result is True

    @pytest.mark.asyncio
    async def test_is_available_false(self):
        with patch("app.services.portfolio_client.check_health") as mock_health:
            mock_health.return_value = {"status": "unhealthy", "error": "Connection refused"}

            result = await is_available()

            assert result is False


class TestGetServiceUrl:
    def test_get_service_url(self):
        with patch("app.services.portfolio_client.settings") as mock_settings:
            mock_settings.portfolio_service_url = "http://localhost:8001"

            url = get_service_url()

            assert url == "http://localhost:8001"


# ============================================================
# 에러 케이스 테스트
# ============================================================

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_service_unavailable_error(self, sample_tickers):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.side_effect = PortfolioServiceUnavailable(
                "Portfolio service unavailable"
            )

            with pytest.raises(PortfolioServiceUnavailable):
                await get_optimization(tickers=sample_tickers)

    @pytest.mark.asyncio
    async def test_service_error_propagation(self, sample_tickers, sample_weights):
        with patch("app.services.portfolio_client._make_request") as mock_request:
            mock_request.side_effect = PortfolioServiceError(
                "Weights must sum to 1.0",
                status_code=400,
            )

            with pytest.raises(PortfolioServiceError) as exc_info:
                await get_risk_analysis(
                    tickers=sample_tickers,
                    weights=sample_weights,
                )

            assert exc_info.value.status_code == 400
