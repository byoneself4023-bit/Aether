"""채팅 API 요청/응답 스키마"""

from pydantic import BaseModel, Field
from typing import Literal


# ============================================================
# Chat Schemas
# ============================================================

class ChatRequest(BaseModel):
    """자연어 채팅 요청"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="사용자 메시지",
        json_schema_extra={"example": "AAPL, GOOGL, NVDA로 포트폴리오 분석해줘"}
    )
    tickers: list[str] | None = Field(
        default=None,
        description="분석할 종목 리스트 (없으면 메시지에서 추출)",
        json_schema_extra={"example": ["AAPL", "GOOGL", "NVDA"]}
    )
    strategy: Literal["min_variance", "max_sharpe"] | None = Field(
        default=None,
        description="최적화 전략 (없으면 max_sharpe)"
    )
    include_backtest: bool = Field(
        default=True,
        description="백테스트 포함 여부"
    )


class PortfolioAnalysisRequest(BaseModel):
    """포트폴리오 분석 요청"""
    tickers: list[str] = Field(
        ...,
        min_length=2,
        max_length=20,
        description="분석할 종목 리스트",
        json_schema_extra={"example": ["AAPL", "GOOGL", "NVDA", "MSFT"]}
    )
    strategy: Literal["min_variance", "max_sharpe"] = Field(
        default="max_sharpe",
        description="최적화 전략"
    )
    period: Literal["1y", "3y", "5y"] = Field(
        default="3y",
        description="분석 기간"
    )
    investment_amount: float | None = Field(
        default=None,
        description="투자 금액 (원화, 리스크 계산용)",
        json_schema_extra={"example": 100000000}
    )


class SourceInfo(BaseModel):
    """출처 정보"""
    title: str
    source: str
    relevance: float | None = None


class PortfolioData(BaseModel):
    """포트폴리오 데이터"""
    weights: dict[str, float]
    metrics: dict[str, float]
    risk_summary: dict[str, float] | None = None
    backtest_metrics: dict[str, float] | None = None


class ChatResponse(BaseModel):
    """채팅 응답"""
    answer: str = Field(..., description="LLM 분석 답변")
    sources: list[SourceInfo] | None = Field(
        default=None,
        description="참조한 출처 (RAG 사용 시)"
    )
    portfolio_data: PortfolioData | None = Field(
        default=None,
        description="포트폴리오 원본 데이터"
    )


class QuickAnalysisRequest(BaseModel):
    """최적화 결과 간단 분석 요청"""
    weights: dict[str, float] = Field(
        ...,
        description="종목별 비중",
        json_schema_extra={"example": {"AAPL": 0.4, "GOOGL": 0.35, "MSFT": 0.25}}
    )
    metrics: dict[str, float] = Field(
        ...,
        description="포트폴리오 지표",
        json_schema_extra={"example": {"expected_return": 0.15, "volatility": 0.18, "sharpe_ratio": 0.83}}
    )


class QuickAnalysisResponse(BaseModel):
    """최적화 결과 간단 분석 응답"""
    analysis: str = Field(..., description="마크다운 형식의 분석 텍스트")


class AnalysisResponse(BaseModel):
    """상세 분석 응답"""
    summary: str = Field(..., description="한 줄 요약")
    portfolio_analysis: dict = Field(..., description="포트폴리오 분석 결과")
    risk_analysis: dict | None = Field(default=None, description="리스크 분석 결과")
    backtest_analysis: dict | None = Field(default=None, description="백테스트 분석 결과")
    portfolio_data: PortfolioData = Field(..., description="원본 데이터")
    recommendation: dict | None = Field(default=None, description="투자 제안")


# ============================================================
# RAG Schemas
# ============================================================

class RAGQueryRequest(BaseModel):
    """RAG 질문 요청"""
    question: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="금융 관련 질문",
        json_schema_extra={"example": "샤프 비율이란 무엇인가요?"}
    )
    k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="참조할 문서 수"
    )
    filter_source: str | None = Field(
        default=None,
        description="특정 소스로 필터링",
        json_schema_extra={"example": "portfolio_theory"}
    )


class RAGQueryResponse(BaseModel):
    """RAG 질문 응답"""
    answer: str = Field(..., description="LLM 답변")
    sources: list[SourceInfo] = Field(..., description="참조한 문서")
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="답변 신뢰도 (평균 relevance)"
    )


class RAGInitRequest(BaseModel):
    """벡터스토어 초기화 요청"""
    force_reload: bool = Field(
        default=False,
        description="기존 데이터 삭제 후 재로드"
    )


class RAGStatusResponse(BaseModel):
    """벡터스토어 상태 응답"""
    initialized: bool
    document_count: int
    persist_dir: str | None = None
    available_sources: list[str] | None = None
