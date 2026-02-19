"""LLM Provider 추상화 - Gemini/OpenAI/Claude 교체 가능"""

import json
import logging
import re
from typing import Protocol, runtime_checkable, Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.config import get_settings
from app.services.token_tracker import get_tracker
from app.services.cache import get_llm_cache, _make_key

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """LLM 호출 관련 에러"""
    pass


class JSONParseError(LLMError):
    """JSON 파싱 에러"""
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

    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
    ) -> dict:
        """JSON 응답 생성"""
        ...


def _extract_json(text: str) -> dict:
    """텍스트에서 JSON 추출

    Gemini가 ```json ... ``` 코드펜스로 감싸는 경우를 처리.
    """
    stripped = text.strip()

    # 코드펜스 제거: ```json ... ``` 또는 ``` ... ```
    if stripped.startswith("```"):
        # 첫 줄(```json 또는 ```) 제거
        first_newline = stripped.find("\n")
        if first_newline != -1:
            stripped = stripped[first_newline + 1:]
        # 끝의 ``` 제거
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()
            stripped = stripped[:-3].rstrip()

    # { ... } 블록 추출 (앞뒤 잡음 제거)
    brace_match = re.search(r'\{[\s\S]*\}', stripped)
    if brace_match:
        stripped = brace_match.group(0)

    return json.loads(stripped)


class GeminiProvider:
    """Google Gemini LLM Provider"""

    def __init__(self):
        self._settings = get_settings()
        self._client_initialized = False

    def _ensure_client(self) -> None:
        if not self._client_initialized and self._settings.google_api_key:
            genai.configure(api_key=self._settings.google_api_key)
            self._client_initialized = True

    def _get_model(self) -> Any:
        self._ensure_client()
        return genai.GenerativeModel(
            model_name=self._settings.llm_model,
            generation_config=GenerationConfig(
                temperature=self._settings.llm_temperature,
                max_output_tokens=self._settings.llm_max_tokens,
            ),
        )

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

        # 캐시 확인
        if use_cache:
            cache_key = _make_key(prompt, system_prompt, temperature=temperature, max_tokens=max_tokens)
            cached = get_llm_cache().get(cache_key)
            if cached is not None:
                logger.debug("LLM cache hit for generate")
                return cached

        try:
            model = self._get_model()

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"

            gen_config = None
            if temperature is not None or max_tokens is not None:
                gen_config = GenerationConfig(
                    temperature=temperature or self._settings.llm_temperature,
                    max_output_tokens=max_tokens or self._settings.llm_max_tokens,
                )

            logger.debug(f"Calling Gemini with prompt length: {len(full_prompt)}")

            response = model.generate_content(
                full_prompt,
                generation_config=gen_config,
                request_options={"timeout": self._settings.llm_timeout},
            )

            if not response.text:
                raise LLMError("Empty response from LLM")

            # 토큰 사용량 추적
            try:
                usage_metadata = getattr(response, "usage_metadata", None)
                if usage_metadata:
                    input_tokens = getattr(usage_metadata, "prompt_token_count", 0) or 0
                    output_tokens = getattr(usage_metadata, "candidates_token_count", 0) or 0
                    get_tracker().record_usage(input_tokens, output_tokens)
            except Exception as e:
                logger.debug(f"Failed to record token usage: {e}")

            logger.debug(f"Gemini response length: {len(response.text)}")

            # 캐시 저장
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
        retry=retry_if_exception_type((JSONParseError,)),
        reraise=True,
    )
    def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        use_cache: bool = True,
    ) -> dict:
        # JSON 캐시 확인
        if use_cache:
            cache_key = _make_key(prompt, system_prompt, temperature=temperature, response_type="json")
            cached = get_llm_cache().get(cache_key)
            if cached is not None and isinstance(cached, dict):
                logger.debug("LLM cache hit for generate_json")
                return cached

        temp = temperature if temperature is not None else 0.3

        response_text = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temp,
            use_cache=False,  # 이미 JSON 캐시에서 확인했으므로 중복 방지
        )

        try:
            result = _extract_json(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}, response: {response_text[:200]}...")
            raise JSONParseError(f"Failed to parse JSON: {e}") from e

        # JSON 결과 캐시 저장
        if use_cache:
            get_llm_cache().set(cache_key, result)

        return result


# Provider 싱글톤
_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """
    설정에 따라 LLM Provider 인스턴스 반환.

    현재는 Gemini만 지원. 추후 OpenAI/Claude 등 추가 가능.
    """
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
