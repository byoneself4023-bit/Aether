"""채팅 API 라우터 - 자연어 포트폴리오 분석"""

import re
import logging
from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    PortfolioAnalysisRequest,
    AnalysisResponse,
    QuickAnalysisRequest,
    QuickAnalysisResponse,
    SourceInfo,
    PortfolioData,
)
from app.services.portfolio_client import (
    get_optimization,
    get_risk_analysis,
    get_backtest,
    get_full_analysis,
    is_available,
    PortfolioServiceError,
    PortfolioServiceUnavailable,
)
from app.services.llm import (
    analyze_portfolio,
    explain_risk,
    summarize_backtest,
    get_recommendation,
    LLMError,
)
from app.services.rag import query_with_llm
from app.services.guardrails import sanitize_user_input, wrap_user_input

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ============================================================
# 유틸리티 함수
# ============================================================

def extract_tickers(message: str) -> list[str]:
    """
    메시지에서 티커 심볼 추출

    예: "AAPL, GOOGL, NVDA 분석해줘" → ["AAPL", "GOOGL", "NVDA"]
    """
    # 대문자 1-5자 패턴 (티커 형식)
    pattern = r'\b([A-Z]{1,5})\b'
    matches = re.findall(pattern, message.upper())

    # 일반 영어 단어 제외
    common_words = {
        "I", "A", "AN", "THE", "TO", "FOR", "AND", "OR", "BUT", "IS", "IT",
        "IN", "ON", "AT", "BY", "OF", "AS", "IF", "MY", "ME", "WE", "US",
        "API", "LLM", "RAG", "MVP", "MSR", "VAR", "ETF", "IPO", "CEO", "CFO",
        "DO", "BE", "HAS", "HAD", "CAN", "WILL", "WITH", "WANT", "NEED", "GET",
        "ALL", "ANY", "ARE", "NOT", "NEW", "OLD", "TOP", "LOW", "HIGH", "BEST",
    }

    tickers = [t for t in matches if t not in common_words]

    # 중복 제거하면서 순서 유지
    seen = set()
    unique_tickers = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            unique_tickers.append(t)

    return unique_tickers


def detect_intent(message: str) -> str:
    """
    메시지 의도 파악

    Returns:
        "analyze": 포트폴리오 분석 요청
        "risk": 리스크 분석 요청
        "backtest": 백테스트 요청
        "question": 일반 금융 질문
        "unknown": 알 수 없음
    """
    message_lower = message.lower()

    if any(word in message_lower for word in ["분석", "최적화", "포트폴리오", "비중", "배분"]):
        return "analyze"

    if any(word in message_lower for word in ["리스크", "위험", "var", "손실", "mdd"]):
        return "risk"

    if any(word in message_lower for word in ["백테스트", "과거", "성과", "수익률"]):
        return "backtest"

    if any(word in message_lower for word in ["뭐", "무엇", "어떻게", "왜", "설명", "알려"]):
        return "question"

    return "unknown"


# ============================================================
# 엔드포인트
# ============================================================

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    자연어 포트폴리오 분석

    사용자 메시지를 파싱하여:
    1. 종목이 있으면 포트폴리오 분석 수행
    2. 종목이 없으면 RAG 기반 금융 질문 답변
    """
    message = request.message

    # 입력 정제 및 인젝션 방어
    sanitized_message, input_warnings = sanitize_user_input(message)
    if input_warnings:
        logger.warning(f"Input warnings: {input_warnings}")

    tickers = request.tickers or extract_tickers(sanitized_message)
    strategy = request.strategy or "max_sharpe"

    logger.info(f"Chat request: {sanitized_message[:50]}..., tickers={tickers}")

    # 종목이 없으면 RAG 질문으로 처리
    if len(tickers) < 2:
        try:
            wrapped_message = wrap_user_input(sanitized_message)
            rag_result = query_with_llm(wrapped_message, k=3)
            sources = [
                SourceInfo(
                    title=s["title"],
                    source=s["source"],
                    relevance=s.get("relevance"),
                )
                for s in rag_result.get("sources", [])
            ]
            return ChatResponse(
                answer=rag_result["answer"],
                sources=sources if sources else None,
                portfolio_data=None,
            )
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return ChatResponse(
                answer=f"죄송합니다, 질문에 답변하는 중 오류가 발생했습니다: {e}",
                sources=None,
                portfolio_data=None,
            )

    # Portfolio 서비스 확인
    if not await is_available():
        raise HTTPException(
            status_code=503,
            detail="Portfolio service is unavailable"
        )

    try:
        # 최적화 수행
        optimization = await get_optimization(
            tickers=tickers,
            strategy=strategy,
            period="3y",
        )

        weights = optimization["weights"]
        metrics = optimization["metrics"]

        # 리스크 분석
        risk = await get_risk_analysis(
            tickers=tickers,
            weights=weights,
        )

        # 백테스트 (옵션)
        backtest_metrics = None
        if request.include_backtest:
            try:
                backtest = await get_backtest(
                    tickers=tickers,
                    strategy=strategy,
                )
                backtest_metrics = backtest["metrics"]
            except Exception as e:
                logger.warning(f"Backtest failed: {e}")

        # LLM 분석
        portfolio_analysis = analyze_portfolio(
            weights=weights,
            metrics=metrics,
        )

        # 포트폴리오 데이터
        portfolio_data = PortfolioData(
            weights=weights,
            metrics=metrics,
            risk_summary=risk.get("risk_summary"),
            backtest_metrics=backtest_metrics,
        )

        # 응답 생성
        answer = portfolio_analysis.get("summary", "분석이 완료되었습니다.")

        # 상세 분석 추가
        if "composition" in portfolio_analysis:
            comp = portfolio_analysis["composition"]
            if isinstance(comp, dict) and "description" in comp:
                answer += f"\n\n{comp['description']}"

        if "metrics_interpretation" in portfolio_analysis:
            interp = portfolio_analysis["metrics_interpretation"]
            if isinstance(interp, dict):
                for key, value in interp.items():
                    if value:
                        answer += f"\n\n**{key}**: {value}"

        return ChatResponse(
            answer=answer,
            sources=None,
            portfolio_data=portfolio_data,
        )

    except PortfolioServiceUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Portfolio service is unavailable"
        )
    except PortfolioServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e)
        )
    except LLMError as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM analysis failed: {e}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_portfolio_endpoint(request: PortfolioAnalysisRequest) -> AnalysisResponse:
    """
    포트폴리오 상세 분석

    종목과 전략을 지정하여:
    1. 포트폴리오 최적화
    2. 리스크 분석
    3. 백테스트
    4. LLM 종합 분석 및 투자 제안
    """
    tickers = request.tickers
    strategy = request.strategy
    period = request.period

    logger.info(f"Analyze request: tickers={tickers}, strategy={strategy}")

    # Portfolio 서비스 확인
    if not await is_available():
        raise HTTPException(
            status_code=503,
            detail="Portfolio service is unavailable"
        )

    try:
        # 전체 분석 수행
        full_analysis = await get_full_analysis(
            tickers=tickers,
            strategy=strategy,
            period=period,
        )

        optimization = full_analysis["optimization"]
        risk = full_analysis["risk"]
        backtest = full_analysis["backtest"]
        summary_data = full_analysis["summary"]

        weights = optimization["weights"]
        metrics = optimization["metrics"]

        # LLM 분석들
        portfolio_analysis = analyze_portfolio(
            weights=weights,
            metrics=metrics,
        )

        risk_analysis = explain_risk(
            risk_data=risk["risk_summary"],
            investment_amount=request.investment_amount,
        )

        backtest_analysis = summarize_backtest(
            metrics=backtest["metrics"],
            strategy=strategy,
            period="5y",
            tickers=tickers,
            final_weights=backtest.get("final_weights"),
        )

        recommendation = get_recommendation(
            current_portfolio=weights,
            metrics=metrics,
            risk_data={
                "var_95": risk["risk_summary"]["var_95_montecarlo"],
                "cvar_99": risk["risk_summary"]["cvar_99"],
            },
        )

        # 포트폴리오 데이터
        portfolio_data = PortfolioData(
            weights=weights,
            metrics=metrics,
            risk_summary=risk["risk_summary"],
            backtest_metrics=backtest["metrics"],
        )

        # 한 줄 요약 생성
        summary = (
            f"{len(tickers)}개 종목 {strategy} 전략: "
            f"샤프 {metrics['sharpe_ratio']:.2f}, "
            f"기대수익 {metrics['expected_return']*100:.1f}%, "
            f"MDD {backtest['metrics']['max_drawdown']*100:.1f}%"
        )

        return AnalysisResponse(
            summary=summary,
            portfolio_analysis=portfolio_analysis,
            risk_analysis=risk_analysis,
            backtest_analysis=backtest_analysis,
            portfolio_data=portfolio_data,
            recommendation=recommendation,
        )

    except PortfolioServiceUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Portfolio service is unavailable"
        )
    except PortfolioServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=str(e)
        )
    except LLMError as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM analysis failed: {e}"
        )


@router.post("/analyze-result", response_model=QuickAnalysisResponse)
async def analyze_result(request: QuickAnalysisRequest) -> QuickAnalysisResponse:
    """
    최적화 결과 간단 분석

    프론트엔드에서 이미 계산된 weights/metrics를 받아
    LLM으로 해석한 마크다운 텍스트를 반환.
    """
    logger.info(f"Quick analysis: {list(request.weights.keys())}")

    try:
        result = analyze_portfolio(
            weights=request.weights,
            metrics=request.metrics,
        )

        # 구조화된 결과에서 마크다운 텍스트 조합
        parts: list[str] = []

        summary = result.get("summary")
        if summary:
            parts.append(summary)

        composition = result.get("composition")
        if isinstance(composition, dict) and "description" in composition:
            parts.append(composition["description"])

        metrics_interp = result.get("metrics_interpretation")
        if isinstance(metrics_interp, dict):
            for key, value in metrics_interp.items():
                if value:
                    parts.append(f"**{key}**: {value}")

        analysis_text = "\n\n".join(parts) if parts else "분석이 완료되었습니다."

        return QuickAnalysisResponse(analysis=analysis_text)

    except LLMError as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {e}")
    except Exception as e:
        logger.error(f"Quick analysis failed: {e}")
        raise HTTPException(status_code=500, detail="분석 중 오류가 발생했습니다.")


@router.get("/health")
async def chat_health():
    """Chat 서비스 헬스체크"""
    portfolio_available = await is_available()

    return {
        "status": "healthy" if portfolio_available else "degraded",
        "portfolio_service": "connected" if portfolio_available else "disconnected",
    }
