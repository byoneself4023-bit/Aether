"""Pydantic 요청/응답 스키마"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ============================================================
# Optimize Schemas
# ============================================================

class OptimizeRequest(BaseModel):
    """포트폴리오 최적화 요청"""
    tickers: list[str] = Field(
        ...,
        min_length=2,
        max_length=30,
        description="종목 티커 리스트 (최소 2개)",
        examples=[["AAPL", "GOOGL", "MSFT", "AMZN"]]
    )
    strategy: Literal["min_variance", "max_sharpe"] = Field(
        default="max_sharpe",
        description="최적화 전략"
    )
    period: Optional[Literal["1y", "3y", "5y"]] = Field(
        default="3y",
        description="학습 데이터 기간 (start_date/end_date 미지정 시 사용)"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="시작일 (YYYY-MM-DD). 지정 시 period 대신 사용",
        examples=["2020-01-01"]
    )
    end_date: Optional[str] = Field(
        default=None,
        description="종료일 (YYYY-MM-DD). 지정 시 period 대신 사용",
        examples=["2024-01-01"]
    )
    include_frontier: bool = Field(
        default=False,
        description="효율적 프론티어 포함 여부"
    )
    include_diagnostics: bool = Field(
        default=False,
        description="최적화 진단 정보 포함 여부"
    )
    rf: float = Field(
        default=0.02,
        ge=0,
        le=0.2,
        description="무위험 이자율 (연율)"
    )


class PortfolioMetricsResponse(BaseModel):
    """포트폴리오 메트릭"""
    expected_return: float = Field(..., description="기대 수익률 (연율)")
    volatility: float = Field(..., description="변동성 (연율)")
    sharpe_ratio: float = Field(..., description="샤프 비율")


class FrontierPoint(BaseModel):
    """프론티어 포인트"""
    expected_return: float
    volatility: float
    weights: dict[str, float]


class CovarianceValidationResponse(BaseModel):
    """공분산 행렬 검증 결과"""
    is_valid: bool = Field(..., description="유효성 여부")
    condition_number: float = Field(..., description="조건수")
    is_positive_definite: bool = Field(..., description="양정치 여부")
    min_eigenvalue: float = Field(..., description="최소 고유값")
    max_correlation: float = Field(..., description="최대 상관계수")
    issues: list[str] = Field(default_factory=list, description="발견된 문제 목록")
    regularized: bool = Field(default=False, description="정규화 적용 여부")


class OptimizationDiagnosticsResponse(BaseModel):
    """최적화 진단 정보"""
    converged: bool = Field(..., description="수렴 여부")
    iterations: int = Field(..., description="반복 횟수")
    final_objective: float = Field(..., description="최종 목적함수 값")
    condition_number: float = Field(..., description="공분산 행렬 조건수")
    solver_message: str = Field(default="", description="솔버 메시지")
    gradient_norm: Optional[float] = Field(None, description="최종 gradient norm")
    covariance_validation: CovarianceValidationResponse = Field(
        ..., description="공분산 행렬 검증 결과"
    )


class OptimizeResponse(BaseModel):
    """포트폴리오 최적화 응답"""
    weights: dict[str, float] = Field(
        ...,
        description="종목별 최적 비중"
    )
    metrics: PortfolioMetricsResponse = Field(
        ...,
        description="포트폴리오 성과 지표"
    )
    n_stocks: int = Field(..., description="종목 수")
    strategy: str = Field(..., description="사용된 전략")
    period: str = Field(..., description="학습 기간")
    frontier: Optional[list[FrontierPoint]] = Field(
        default=None,
        description="효율적 프론티어 (요청 시)"
    )
    diagnostics: Optional[OptimizationDiagnosticsResponse] = Field(
        default=None,
        description="최적화 진단 정보 (include_diagnostics=True일 때)"
    )
    # Graceful 실패 관련 필드
    failed_tickers: Optional[list[str]] = Field(
        default=None,
        description="데이터 수집 실패한 티커 리스트 (부분 성공 시)"
    )
    warnings: Optional[list[str]] = Field(
        default=None,
        description="경고 메시지 리스트"
    )


# ============================================================
# Risk Schemas
# ============================================================

class RiskRequest(BaseModel):
    """리스크 분석 요청"""
    tickers: list[str] = Field(
        ...,
        min_length=1,
        description="종목 티커 리스트"
    )
    weights: dict[str, float] = Field(
        ...,
        description="종목별 비중 (합계 1.0)"
    )
    confidence: Literal[0.95, 0.99] = Field(
        default=0.95,
        description="신뢰수준"
    )
    period: Literal["1y", "3y", "5y"] = Field(
        default="1y",
        description="분석 기간"
    )
    n_simulations: int = Field(
        default=10000,
        ge=1000,
        le=100000,
        description="몬테카를로 시뮬레이션 횟수"
    )


class VaRResponse(BaseModel):
    """VaR 결과"""
    value: float = Field(..., description="VaR 값 (손실률)")
    confidence: float = Field(..., description="신뢰수준")
    holding_days: int = Field(default=1, description="보유 기간")
    method: str = Field(..., description="계산 방식")


class RiskSummaryResponse(BaseModel):
    """종합 리스크 요약"""
    volatility: float = Field(..., description="연율화 변동성")
    expected_return: float = Field(..., description="기대 수익률 (연율)")
    var_95_parametric: float
    var_99_parametric: float
    var_95_montecarlo: float
    var_99_montecarlo: float
    cvar_95: float
    cvar_99: float
    max_loss_1d: float = Field(..., description="1일 최대 예상 손실 (99.9%)")


class RiskResponse(BaseModel):
    """리스크 분석 응답"""
    parametric_var: VaRResponse = Field(..., description="Parametric VaR")
    monte_carlo_var: VaRResponse = Field(..., description="Monte Carlo VaR")
    cvar: float = Field(..., description="Conditional VaR (Expected Shortfall)")
    risk_summary: RiskSummaryResponse = Field(..., description="종합 리스크 요약")


# ============================================================
# Backtest Schemas
# ============================================================

class BacktestRequest(BaseModel):
    """백테스트 요청"""
    tickers: list[str] = Field(
        ...,
        min_length=2,
        description="종목 티커 리스트"
    )
    strategy: Literal["min_variance", "max_sharpe", "equal_weight"] = Field(
        default="max_sharpe",
        description="최적화 전략"
    )
    train_window: int = Field(
        default=252,
        ge=60,
        le=756,
        description="학습 기간 (거래일, 기본 1년)"
    )
    rebalance_every: int = Field(
        default=63,
        ge=5,
        le=252,
        description="리밸런싱 주기 (거래일, 기본 분기)"
    )
    transaction_cost: float = Field(
        default=0.001,
        ge=0,
        le=0.01,
        description="편도 거래비용 (0.001 = 0.1%)"
    )
    period: Optional[Literal["3y", "5y", "10y"]] = Field(
        default="5y",
        description="백테스트 기간 (start_date/end_date 미지정 시 사용)"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="시작일 (YYYY-MM-DD). 지정 시 period 대신 사용",
        examples=["2019-01-01"]
    )
    end_date: Optional[str] = Field(
        default=None,
        description="종료일 (YYYY-MM-DD). 지정 시 period 대신 사용",
        examples=["2024-01-01"]
    )
    use_shrinkage: bool = Field(
        default=True,
        description="Shrinkage 공분산 사용"
    )
    window_type: Literal["rolling", "expanding"] = Field(
        default="rolling",
        description="윈도우 타입 (rolling: 고정 크기, expanding: 누적)"
    )


class PerformanceMetricsResponse(BaseModel):
    """성과 메트릭"""
    total_return: float = Field(..., description="누적 수익률")
    annual_return: float = Field(..., description="연환산 수익률 (CAGR)")
    annual_volatility: float = Field(..., description="연환산 변동성")
    sharpe_ratio: float = Field(..., description="샤프 비율")
    max_drawdown: float = Field(..., description="최대 낙폭 (MDD)")
    calmar_ratio: float = Field(..., description="칼마 비율")
    avg_turnover: float = Field(..., description="평균 턴오버")
    win_rate: float = Field(..., description="승률")


class RebalanceRecordResponse(BaseModel):
    """리밸런싱 기록"""
    date: str
    weights: dict[str, float]
    turnover: float


class BacktestResponse(BaseModel):
    """백테스트 응답"""
    metrics: PerformanceMetricsResponse = Field(..., description="성과 메트릭")
    portfolio_values: list[dict] = Field(
        ...,
        description="일별 포트폴리오 가치 [{date, value}, ...]"
    )
    rebalance_count: int = Field(..., description="리밸런싱 횟수")
    rebalance_history: list[RebalanceRecordResponse] = Field(
        ...,
        description="리밸런싱 기록"
    )
    strategy: str = Field(..., description="사용된 전략")
    tickers: list[str] = Field(..., description="종목 리스트")
    final_weights: dict[str, float] = Field(..., description="최종 비중")
    window_type: str = Field(default="rolling", description="윈도우 타입")


# ============================================================
# Common Schemas
# ============================================================

class TickerInfo(BaseModel):
    """종목 정보"""
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency: str = "USD"


class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str
    detail: Optional[str] = None
