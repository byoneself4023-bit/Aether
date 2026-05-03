"""LLM Provider 추상화 - Gemini/OpenAI/Claude 교체 가능"""

from __future__ import annotations

import logging
from typing import Any, Protocol, runtime_checkable

from google import genai
from google.genai import types as genai_types
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings
from app.services.cache import _make_key, get_llm_cache
from app.services.token_tracker import get_tracker

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """LLM 호출 관련 에러"""

    pass


class LLMResponseError(LLMError):
    """구조화 응답 검증 실패 — Pydantic ValidationError 래핑 (H-6)."""

    pass


@runtime_checkable
class LLMProvider(Protocol):
    """LLM Provider 인터페이스"""

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """텍스트 생성"""
        ...

    def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str | None = None,
        temperature: float | None = None,
    ) -> BaseModel:
        """Pydantic 모델 강제 출력 (Gemini response_schema)."""
        ...


class GeminiProvider:
    """Google Gemini LLM Provider"""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: genai.Client | None = None

    def _ensure_client(self) -> genai.Client:
        if self._client is None:
            if not self._settings.google_api_key:
                raise LLMError("GOOGLE_API_KEY not configured")
            self._client = genai.Client(
                api_key=self._settings.google_api_key,
                http_options=genai_types.HttpOptions(
                    timeout=int(self._settings.llm_timeout * 1000),
                ),
            )
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        use_cache: bool = True,
    ) -> str:
        if not self._settings.google_api_key:
            raise LLMError("GOOGLE_API_KEY not configured")

        if use_cache:
            cache_key = _make_key(prompt, system_prompt, temperature=temperature, max_tokens=max_tokens)
            cached = get_llm_cache().get(cache_key)
            if cached is not None:
                logger.debug("LLM cache hit for generate")
                return cached  # type: ignore[return-value]

        try:
            client = self._ensure_client()

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"

            config = genai_types.GenerateContentConfig(
                temperature=temperature if temperature is not None else self._settings.llm_temperature,
                max_output_tokens=max_tokens if max_tokens is not None else self._settings.llm_max_tokens,
            )

            logger.debug(f"Calling Gemini with prompt length: {len(full_prompt)}")

            response = client.models.generate_content(
                model=self._settings.llm_model,
                contents=full_prompt,
                config=config,
            )

            if not response.text:
                raise LLMError("Empty response from LLM")

            try:
                usage_metadata = getattr(response, "usage_metadata", None)
                if usage_metadata:
                    input_tokens = getattr(usage_metadata, "prompt_token_count", 0) or 0
                    output_tokens = getattr(usage_metadata, "candidates_token_count", 0) or 0
                    get_tracker().record_usage(input_tokens, output_tokens)
            except Exception as e:
                logger.debug(f"Failed to record token usage: {e}")

            logger.debug(f"Gemini response length: {len(response.text)}")

            if use_cache:
                get_llm_cache().set(cache_key, response.text)

            return response.text

        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Gemini call failed: {e}")
            raise LLMError(f"LLM call failed: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((LLMResponseError,)),
        reraise=True,
    )
    def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        system_prompt: str | None = None,
        temperature: float | None = None,
        use_cache: bool = True,
    ) -> BaseModel:
        if not self._settings.google_api_key:
            raise LLMError("GOOGLE_API_KEY not configured")

        if use_cache:
            cache_key = _make_key(
                prompt,
                system_prompt,
                temperature=temperature,
                response_model=response_model.__name__,
            )
            cached = get_llm_cache().get(cache_key)
            if cached is not None and isinstance(cached, dict):
                logger.debug("LLM cache hit for generate_structured")
                return response_model.model_validate(cached)

        temp = temperature if temperature is not None else 0.3

        try:
            client = self._ensure_client()

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"

            config = genai_types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=self._settings.llm_max_tokens,
                response_mime_type="application/json",
                response_schema=response_model,
            )

            response = client.models.generate_content(
                model=self._settings.llm_model,
                contents=full_prompt,
                config=config,
            )

            if not response.text:
                raise LLMError("Empty response from LLM")

            try:
                usage_metadata = getattr(response, "usage_metadata", None)
                if usage_metadata:
                    input_tokens = getattr(usage_metadata, "prompt_token_count", 0) or 0
                    output_tokens = getattr(usage_metadata, "candidates_token_count", 0) or 0
                    get_tracker().record_usage(input_tokens, output_tokens)
            except Exception as e:
                logger.debug(f"Failed to record token usage: {e}")

        except (LLMError, LLMResponseError):
            raise
        except Exception as e:
            logger.error(f"Gemini structured call failed: {e}")
            raise LLMError(f"LLM call failed: {e}") from e

        try:
            result = response_model.model_validate_json(response.text)
        except ValidationError as e:
            logger.warning(f"Structured response validation failed: {e}")
            raise LLMResponseError(f"Response did not match {response_model.__name__}: {e}") from e

        if use_cache:
            get_llm_cache().set(cache_key, result.model_dump())

        return result


_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """설정에 따라 LLM Provider 인스턴스 반환."""
    global _provider
    if _provider is None:
        settings = get_settings()
        provider_name = getattr(settings, "llm_provider", "gemini")

        if provider_name == "gemini":
            _provider = GeminiProvider()
        else:
            raise LLMError(f"Unsupported LLM provider: {provider_name}")

    return _provider


def reset_provider() -> None:
    """Provider 초기화 (테스트용)"""
    global _provider
    _provider = None
