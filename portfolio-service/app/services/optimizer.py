"""Markowitz 포트폴리오 최적화 서비스"""

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize, OptimizeResult
from dataclasses import dataclass
from typing import Optional

from app.middleware.logging import logger


@dataclass
class PortfolioMetrics:
    """포트폴리오 성과 지표"""
    weights: NDArray[np.float64]
    expected_return: float
    volatility: float
    sharpe_ratio: float


@dataclass
class EfficientFrontier:
    """효율적 프론티어 결과"""
    returns: NDArray[np.float64]
    volatilities: NDArray[np.float64]
    weights: NDArray[np.float64]  # (n_points, n_assets)


@dataclass
class CovarianceValidation:
    """공분산 행렬 검증 결과"""
    is_valid: bool
    issues: list[str]
    condition_number: float
    min_eigenvalue: float
    max_correlation: float
    was_regularized: bool = False
    regularization_amount: float = 0.0


@dataclass
class OptimizationDiagnostics:
    """최적화 진단 정보"""
    converged: bool
    iterations: int
    final_objective: float
    condition_number: float
    covariance_validation: CovarianceValidation
    solver_message: str = ""
    gradient_norm: Optional[float] = None


@dataclass
class OptimizationResult:
    """최적화 결과 + 진단 정보"""
    metrics: PortfolioMetrics
    diagnostics: OptimizationDiagnostics


def validate_covariance_matrix(
    cov: NDArray[np.float64],
    max_condition_number: float = 1e12,
    max_correlation: float = 0.999
) -> CovarianceValidation:
    """
    공분산 행렬 건전성 검사

    완전 상관 자산(ρ=1), 특이행렬 등 엣지 케이스 탐지.

    Args:
        cov: 공분산 행렬 (N x N)
        max_condition_number: 조건수 임계값 (초과 시 ill-conditioned)
        max_correlation: 상관계수 임계값 (초과 시 near-perfect correlation)

    Returns:
        CovarianceValidation 결과
    """
    n = cov.shape[0]
    issues = []

    # 1. 대칭성 검사
    if not np.allclose(cov, cov.T, rtol=1e-10):
        issues.append("Matrix is not symmetric")

    # 2. 양정치성 검사 (positive semi-definite)
    try:
        eigenvalues = np.linalg.eigvalsh(cov)
        min_eigenvalue = float(eigenvalues.min())

        if min_eigenvalue < -1e-10:
            issues.append(
                f"Matrix is not positive semi-definite "
                f"(min eigenvalue: {min_eigenvalue:.2e})"
            )
    except np.linalg.LinAlgError:
        min_eigenvalue = float("-inf")
        issues.append("Eigenvalue computation failed - matrix may be singular")

    # 3. 조건수 검사
    try:
        cond_number = float(np.linalg.cond(cov))
        if cond_number > max_condition_number:
            issues.append(
                f"Matrix is ill-conditioned "
                f"(condition number: {cond_number:.2e} > {max_condition_number:.2e})"
            )
    except np.linalg.LinAlgError:
        cond_number = float("inf")
        issues.append("Condition number computation failed")

    # 4. 완전 상관 검사 (correlation matrix 변환)
    diag = np.diag(cov)
    # 0으로 나누기 방지
    diag_safe = np.where(diag > 0, diag, 1e-10)
    corr = cov / np.sqrt(np.outer(diag_safe, diag_safe))
    np.fill_diagonal(corr, 0)  # 대각선은 제외

    max_corr = float(np.abs(corr).max())
    if max_corr > max_correlation:
        # 어떤 자산 쌍이 문제인지 찾기
        i, j = np.unravel_index(np.abs(corr).argmax(), corr.shape)
        issues.append(
            f"Near-perfect correlation detected between assets {i} and {j} "
            f"(|ρ| = {max_corr:.4f})"
        )

    # 5. 대각선 음수 검사 (분산이 음수인 경우)
    if np.any(diag < 0):
        issues.append("Negative variance detected on diagonal")

    is_valid = len(issues) == 0

    if not is_valid:
        logger.warning(
            "covariance_validation_failed",
            issues=issues,
            condition_number=cond_number,
            min_eigenvalue=min_eigenvalue
        )

    return CovarianceValidation(
        is_valid=is_valid,
        issues=issues,
        condition_number=cond_number,
        min_eigenvalue=min_eigenvalue,
        max_correlation=max_corr
    )


def regularize_covariance(
    cov: NDArray[np.float64],
    validation: CovarianceValidation,
    target_condition_number: float = 1e8
) -> tuple[NDArray[np.float64], CovarianceValidation]:
    """
    ill-conditioned 또는 non-PSD 공분산 행렬 정규화

    방법:
    1. 음의 고유값 → 0으로 클리핑
    2. 대각선에 작은 값 추가 (ridge regularization)

    Args:
        cov: 원본 공분산 행렬
        validation: 검증 결과
        target_condition_number: 목표 조건수

    Returns:
        (정규화된 공분산 행렬, 업데이트된 검증 결과)
    """
    n = cov.shape[0]
    cov_reg = cov.copy()

    # 고유값 분해
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # 1. 음의 고유값 클리핑
    min_eigenvalue = eigenvalues.min()
    if min_eigenvalue < 0:
        eigenvalues = np.maximum(eigenvalues, 0)
        cov_reg = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

    # 2. 조건수 개선 (대각선에 값 추가)
    max_eigenvalue = eigenvalues.max()
    if max_eigenvalue > 0:
        # 목표 조건수를 위한 최소 고유값 계산
        target_min_eig = max_eigenvalue / target_condition_number
        current_min_eig = eigenvalues[eigenvalues > 0].min() if np.any(eigenvalues > 0) else 0

        if current_min_eig < target_min_eig:
            ridge = target_min_eig - current_min_eig
            cov_reg = cov_reg + ridge * np.eye(n)
        else:
            ridge = 0
    else:
        # 모든 고유값이 0 이하면 identity 추가
        ridge = 1e-6
        cov_reg = cov_reg + ridge * np.eye(n)

    # 대칭성 보장
    cov_reg = (cov_reg + cov_reg.T) / 2

    # 정규화 결과 검증
    new_validation = validate_covariance_matrix(cov_reg)
    new_validation.was_regularized = True
    new_validation.regularization_amount = ridge if 'ridge' in dir() else 0

    logger.info(
        "covariance_regularized",
        original_condition_number=validation.condition_number,
        new_condition_number=new_validation.condition_number,
        regularization_amount=new_validation.regularization_amount
    )

    return cov_reg, new_validation


def portfolio_metrics(
    weights: NDArray[np.float64],
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    rf: float = 0.0
) -> PortfolioMetrics:
    """
    포트폴리오 성과 지표 계산

    Args:
        weights: 자산 비중 (N,)
        mu: 기대수익률 벡터 (N,)
        cov: 공분산 행렬 (N x N)
        rf: 무위험 이자율

    Returns:
        PortfolioMetrics 객체
    """
    w = np.asarray(weights)
    expected_return = float(w @ mu)
    volatility = float(np.sqrt(w @ cov @ w))
    sharpe_ratio = (expected_return - rf) / volatility if volatility > 0 else 0.0

    return PortfolioMetrics(
        weights=w,
        expected_return=expected_return,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio
    )


def optimize_min_variance(
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    target_return: Optional[float] = None,
    auto_regularize: bool = True
) -> PortfolioMetrics:
    """
    최소 분산 포트폴리오 (MVP) 최적화

    목적함수: min w^T * Σ * w
    제약조건: Σw = 1, 0 ≤ w ≤ 1, (선택) w^T*μ = target_return

    Args:
        mu: 기대수익률 벡터 (N,)
        cov: 공분산 행렬 (N x N)
        target_return: 목표 수익률 (None이면 글로벌 MVP)
        auto_regularize: 공분산 행렬 문제 시 자동 정규화 여부

    Returns:
        PortfolioMetrics 객체
    """
    n_assets = len(mu)
    w0 = np.ones(n_assets) / n_assets  # 동일 비중 초기값

    # 공분산 행렬 검증
    validation = validate_covariance_matrix(cov)

    if not validation.is_valid:
        if auto_regularize:
            logger.warning(
                "covariance_issues_detected",
                issues=validation.issues,
                action="auto_regularize"
            )
            cov, validation = regularize_covariance(cov, validation)
        else:
            raise ValueError(
                f"Invalid covariance matrix: {'; '.join(validation.issues)}"
            )

    # 목적함수: 포트폴리오 분산
    def objective(w: NDArray) -> float:
        return float(w @ cov @ w)

    # 제약조건
    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1}  # 비중 합 = 1
    ]

    if target_return is not None:
        constraints.append({
            "type": "eq",
            "fun": lambda w: w @ mu - target_return  # 목표 수익률
        })

    # 경계조건: 0 ≤ w ≤ 1 (공매도 불가)
    bounds = [(0, 1) for _ in range(n_assets)]

    result: OptimizeResult = minimize(
        objective,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1000}
    )

    if not result.success:
        # 에러 메시지에 진단 정보 추가
        raise ValueError(
            f"Optimization failed: {result.message}. "
            f"Iterations: {result.nit}, "
            f"Condition number: {validation.condition_number:.2e}"
        )

    return portfolio_metrics(result.x, mu, cov)


def optimize_min_variance_with_diagnostics(
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    target_return: Optional[float] = None,
    auto_regularize: bool = True
) -> OptimizationResult:
    """
    최소 분산 포트폴리오 최적화 + 진단 정보 반환

    Args:
        mu: 기대수익률 벡터 (N,)
        cov: 공분산 행렬 (N x N)
        target_return: 목표 수익률 (None이면 글로벌 MVP)
        auto_regularize: 공분산 행렬 문제 시 자동 정규화 여부

    Returns:
        OptimizationResult(metrics, diagnostics)
    """
    n_assets = len(mu)
    w0 = np.ones(n_assets) / n_assets

    # 공분산 행렬 검증
    validation = validate_covariance_matrix(cov)

    if not validation.is_valid:
        if auto_regularize:
            logger.warning(
                "covariance_issues_detected",
                issues=validation.issues,
                action="auto_regularize"
            )
            cov, validation = regularize_covariance(cov, validation)
        else:
            raise ValueError(
                f"Invalid covariance matrix: {'; '.join(validation.issues)}"
            )

    # 목적함수: 포트폴리오 분산
    def objective(w: NDArray) -> float:
        return float(w @ cov @ w)

    # 제약조건
    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    ]

    if target_return is not None:
        constraints.append({
            "type": "eq",
            "fun": lambda w: w @ mu - target_return
        })

    bounds = [(0, 1) for _ in range(n_assets)]

    result: OptimizeResult = minimize(
        objective,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1000}
    )

    # 진단 정보 생성
    gradient_norm = None
    if hasattr(result, 'jac') and result.jac is not None:
        gradient_norm = float(np.linalg.norm(result.jac))

    diagnostics = OptimizationDiagnostics(
        converged=result.success,
        iterations=result.nit,
        final_objective=float(result.fun),
        condition_number=validation.condition_number,
        covariance_validation=validation,
        solver_message=result.message,
        gradient_norm=gradient_norm
    )

    if not result.success:
        logger.error(
            "optimization_failed",
            message=result.message,
            iterations=result.nit,
            condition_number=validation.condition_number
        )
        raise ValueError(
            f"Optimization failed: {result.message}. "
            f"Iterations: {result.nit}, "
            f"Condition number: {validation.condition_number:.2e}"
        )

    metrics = portfolio_metrics(result.x, mu, cov)

    logger.info(
        "optimization_completed",
        strategy="min_variance",
        converged=True,
        iterations=result.nit,
        sharpe_ratio=metrics.sharpe_ratio
    )

    return OptimizationResult(metrics=metrics, diagnostics=diagnostics)


def optimize_max_sharpe(
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    rf: float = 0.0,
    auto_regularize: bool = True
) -> PortfolioMetrics:
    """
    최대 샤프 비율 포트폴리오 (MSR) 최적화

    목적함수: max (w^T*μ - rf) / √(w^T*Σ*w)
             ≡ min -Sharpe Ratio
    제약조건: Σw = 1, 0 ≤ w ≤ 1

    Args:
        mu: 기대수익률 벡터 (N,)
        cov: 공분산 행렬 (N x N)
        rf: 무위험 이자율
        auto_regularize: 공분산 행렬 문제 시 자동 정규화 여부

    Returns:
        PortfolioMetrics 객체
    """
    n_assets = len(mu)
    w0 = np.ones(n_assets) / n_assets

    # 공분산 행렬 검증
    validation = validate_covariance_matrix(cov)

    if not validation.is_valid:
        if auto_regularize:
            logger.warning(
                "covariance_issues_detected",
                issues=validation.issues,
                action="auto_regularize"
            )
            cov, validation = regularize_covariance(cov, validation)
        else:
            raise ValueError(
                f"Invalid covariance matrix: {'; '.join(validation.issues)}"
            )

    # 목적함수: -Sharpe (최소화 → 최대 샤프)
    def objective(w: NDArray) -> float:
        port_return = w @ mu
        port_vol = np.sqrt(w @ cov @ w)
        if port_vol < 1e-10:
            return 1e10  # 페널티
        return -(port_return - rf) / port_vol

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    ]

    bounds = [(0, 1) for _ in range(n_assets)]

    result: OptimizeResult = minimize(
        objective,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1000}
    )

    if not result.success:
        raise ValueError(
            f"Optimization failed: {result.message}. "
            f"Iterations: {result.nit}, "
            f"Condition number: {validation.condition_number:.2e}"
        )

    return portfolio_metrics(result.x, mu, cov, rf)


def optimize_max_sharpe_with_diagnostics(
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    rf: float = 0.0,
    auto_regularize: bool = True
) -> OptimizationResult:
    """
    최대 샤프 비율 포트폴리오 최적화 + 진단 정보 반환

    Args:
        mu: 기대수익률 벡터 (N,)
        cov: 공분산 행렬 (N x N)
        rf: 무위험 이자율
        auto_regularize: 공분산 행렬 문제 시 자동 정규화 여부

    Returns:
        OptimizationResult(metrics, diagnostics)
    """
    n_assets = len(mu)
    w0 = np.ones(n_assets) / n_assets

    # 공분산 행렬 검증
    validation = validate_covariance_matrix(cov)

    if not validation.is_valid:
        if auto_regularize:
            logger.warning(
                "covariance_issues_detected",
                issues=validation.issues,
                action="auto_regularize"
            )
            cov, validation = regularize_covariance(cov, validation)
        else:
            raise ValueError(
                f"Invalid covariance matrix: {'; '.join(validation.issues)}"
            )

    # 목적함수: -Sharpe
    def objective(w: NDArray) -> float:
        port_return = w @ mu
        port_vol = np.sqrt(w @ cov @ w)
        if port_vol < 1e-10:
            return 1e10
        return -(port_return - rf) / port_vol

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    ]

    bounds = [(0, 1) for _ in range(n_assets)]

    result: OptimizeResult = minimize(
        objective,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1000}
    )

    # 진단 정보 생성
    gradient_norm = None
    if hasattr(result, 'jac') and result.jac is not None:
        gradient_norm = float(np.linalg.norm(result.jac))

    diagnostics = OptimizationDiagnostics(
        converged=result.success,
        iterations=result.nit,
        final_objective=float(result.fun),
        condition_number=validation.condition_number,
        covariance_validation=validation,
        solver_message=result.message,
        gradient_norm=gradient_norm
    )

    if not result.success:
        logger.error(
            "optimization_failed",
            message=result.message,
            iterations=result.nit,
            condition_number=validation.condition_number
        )
        raise ValueError(
            f"Optimization failed: {result.message}. "
            f"Iterations: {result.nit}, "
            f"Condition number: {validation.condition_number:.2e}"
        )

    metrics = portfolio_metrics(result.x, mu, cov, rf)

    logger.info(
        "optimization_completed",
        strategy="max_sharpe",
        converged=True,
        iterations=result.nit,
        sharpe_ratio=metrics.sharpe_ratio
    )

    return OptimizationResult(metrics=metrics, diagnostics=diagnostics)


def efficient_frontier(
    mu: NDArray[np.float64],
    cov: NDArray[np.float64],
    n_points: int = 25,
    rf: float = 0.0
) -> EfficientFrontier:
    """
    효율적 프론티어 계산

    MVP에서 최대 수익률까지 n_points 포인트의 최적 포트폴리오 계산.

    Args:
        mu: 기대수익률 벡터 (N,)
        cov: 공분산 행렬 (N x N)
        n_points: 프론티어 포인트 수
        rf: 무위험 이자율

    Returns:
        EfficientFrontier 객체
    """
    # MVP 계산 (최소 수익률 지점)
    mvp = optimize_min_variance(mu, cov)
    min_return = mvp.expected_return

    # 최대 수익률 (단일 자산 최대)
    max_return = float(np.max(mu))

    # 타겟 수익률 범위
    target_returns = np.linspace(min_return, max_return, n_points)

    frontier_returns = []
    frontier_volatilities = []
    frontier_weights = []

    for target in target_returns:
        try:
            result = optimize_min_variance(mu, cov, target_return=target)
            frontier_returns.append(result.expected_return)
            frontier_volatilities.append(result.volatility)
            frontier_weights.append(result.weights)
        except ValueError:
            # 최적화 실패 시 스킵
            continue

    return EfficientFrontier(
        returns=np.array(frontier_returns),
        volatilities=np.array(frontier_volatilities),
        weights=np.array(frontier_weights)
    )
