"""프롬프트 버전 관리 레지스트리"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """버전 관리되는 프롬프트 템플릿"""

    name: str
    version: str
    template: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class PromptRegistry:
    """프롬프트 레지스트리 - 버전 관리 및 조회"""

    def __init__(self):
        self._prompts: dict[str, list[PromptTemplate]] = {}

    def register(
        self,
        name: str,
        version: str,
        template: str,
        metadata: dict[str, Any] | None = None,
    ) -> PromptTemplate:
        """
        프롬프트 등록.

        Args:
            name: 프롬프트 이름
            version: 버전 (예: "1.0", "1.1")
            template: 템플릿 문자열
            metadata: 추가 메타데이터

        Returns:
            등록된 PromptTemplate
        """
        prompt = PromptTemplate(
            name=name,
            version=version,
            template=template,
            metadata=metadata or {},
        )

        if name not in self._prompts:
            self._prompts[name] = []

        # 중복 버전 체크
        for existing in self._prompts[name]:
            if existing.version == version:
                logger.warning(f"Overwriting prompt {name} v{version}")
                self._prompts[name].remove(existing)
                break

        self._prompts[name].append(prompt)
        logger.info(f"Registered prompt: {name} v{version}")

        return prompt

    def get(self, name: str, version: str | None = None) -> PromptTemplate:
        """
        프롬프트 조회.

        Args:
            name: 프롬프트 이름
            version: 특정 버전 (None이면 최신 버전)

        Returns:
            PromptTemplate

        Raises:
            KeyError: 프롬프트가 존재하지 않을 때
        """
        if name not in self._prompts or not self._prompts[name]:
            raise KeyError(f"Prompt not found: {name}")

        versions = self._prompts[name]

        if version is not None:
            for p in versions:
                if p.version == version:
                    return p
            raise KeyError(f"Prompt version not found: {name} v{version}")

        # 최신 버전 반환 (등록 시간 기준)
        return max(versions, key=lambda p: p.created_at)

    def list_versions(self, name: str) -> list[str]:
        """
        프롬프트의 버전 히스토리 반환.

        Args:
            name: 프롬프트 이름

        Returns:
            버전 리스트 (오래된 순)
        """
        if name not in self._prompts:
            return []

        sorted_prompts = sorted(self._prompts[name], key=lambda p: p.created_at)
        return [p.version for p in sorted_prompts]

    def list_prompts(self) -> list[str]:
        """등록된 모든 프롬프트 이름 반환"""
        return list(self._prompts.keys())


# 글로벌 레지스트리 싱글톤
_registry: PromptRegistry | None = None


def get_registry() -> PromptRegistry:
    """글로벌 PromptRegistry 인스턴스 반환"""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
        _register_default_prompts(_registry)
    return _registry


def _schema_template(model: type[BaseModel]) -> str:
    """Pydantic 모델의 JSON Schema를 정렬된 JSON 문자열로 직렬화 (registry 자산 등록용, H-6)."""
    import json

    return json.dumps(model.model_json_schema(), sort_keys=True, ensure_ascii=False)


def _register_default_prompts(registry: PromptRegistry) -> None:
    """기본 프롬프트 v1.0 등록"""
    from app.schemas.llm_output import (
        BacktestSummaryResponse,
        PortfolioAnalysisResponse,
        RecommendationResponse,
        RiskAnalysisResponse,
    )
    from app.services.prompts import (
        RAG_SYSTEM_PROMPT,
        RAG_USER_TEMPLATE,
        SYSTEM_PROMPT,
    )

    registry.register(
        name="system_prompt",
        version="1.0",
        template=SYSTEM_PROMPT,
        metadata={"description": "Aether 포트폴리오 분석 AI 시스템 프롬프트"},
    )

    registry.register(
        name="portfolio_analysis_schema",
        version="1.0",
        template=_schema_template(PortfolioAnalysisResponse),
        metadata={
            "description": "포트폴리오 분석 JSON 스키마 (PortfolioAnalysisResponse.model_json_schema)",
            "source_model": "app.schemas.llm_output.PortfolioAnalysisResponse",
        },
    )

    registry.register(
        name="risk_explanation_schema",
        version="1.0",
        template=_schema_template(RiskAnalysisResponse),
        metadata={
            "description": "리스크 설명 JSON 스키마 (RiskAnalysisResponse.model_json_schema)",
            "source_model": "app.schemas.llm_output.RiskAnalysisResponse",
        },
    )

    registry.register(
        name="backtest_summary_schema",
        version="1.0",
        template=_schema_template(BacktestSummaryResponse),
        metadata={
            "description": "백테스트 요약 JSON 스키마 (BacktestSummaryResponse.model_json_schema)",
            "source_model": "app.schemas.llm_output.BacktestSummaryResponse",
        },
    )

    registry.register(
        name="recommendation_schema",
        version="1.0",
        template=_schema_template(RecommendationResponse),
        metadata={
            "description": "투자 추천 JSON 스키마 (RecommendationResponse.model_json_schema)",
            "source_model": "app.schemas.llm_output.RecommendationResponse",
        },
    )

    registry.register(
        name="rag_system",
        version="1.0",
        template=RAG_SYSTEM_PROMPT,
        metadata={"description": "RAG 시스템 프롬프트 - 금융 지식 답변"},
    )

    registry.register(
        name="rag_user",
        version="1.0",
        template=RAG_USER_TEMPLATE,
        metadata={"description": "RAG 유저 프롬프트 - context/question 치환"},
    )
