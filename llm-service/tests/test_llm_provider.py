"""Major #6: LLM Provider 추상화 테스트 (H-6: structured output)"""

from unittest.mock import MagicMock, patch

import pytest
from app.services.llm_provider import (
    GeminiProvider,
    LLMError,
    LLMProvider,
    LLMResponseError,
    get_llm_provider,
    reset_provider,
)
from pydantic import BaseModel


class _SampleResponse(BaseModel):
    summary: str
    score: int


class TestLLMProviderProtocol:
    """LLMProvider Protocol 테스트"""

    def test_gemini_provider_satisfies_protocol(self):
        assert isinstance(GeminiProvider(), LLMProvider)

    def test_mock_provider_satisfies_protocol(self):
        mock = MagicMock(spec=LLMProvider)
        assert isinstance(mock, LLMProvider)


class TestGeminiProviderGenerate:
    """generate() 텍스트 생성"""

    @patch("app.services.llm_provider.GeminiProvider._get_model")
    @patch("app.services.llm_provider.get_settings")
    def test_generate_success(self, mock_get_settings, mock_get_model):
        settings = MagicMock()
        settings.google_api_key = "test-key"
        settings.llm_temperature = 0.7
        settings.llm_max_tokens = 2048
        settings.llm_timeout = 30
        mock_get_settings.return_value = settings

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated text"
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model

        provider = GeminiProvider()
        provider._settings = settings
        result = provider.generate("Test prompt", use_cache=False)

        assert result == "Generated text"

    @patch("app.services.llm_provider.get_settings")
    def test_generate_without_api_key(self, mock_get_settings):
        settings = MagicMock()
        settings.google_api_key = ""
        mock_get_settings.return_value = settings

        provider = GeminiProvider()
        provider._settings = settings

        with pytest.raises(LLMError, match="GOOGLE_API_KEY not configured"):
            provider.generate("Test prompt")


class TestGeminiProviderGenerateStructured:
    """generate_structured() Pydantic 강제 출력 (H-6)"""

    @patch("app.services.llm_provider.genai.GenerativeModel")
    @patch("app.services.llm_provider.GeminiProvider._ensure_client")
    @patch("app.services.llm_provider.get_settings")
    def test_generate_structured_success(self, mock_get_settings, _mock_ensure, mock_model_cls):
        settings = MagicMock()
        settings.google_api_key = "test-key"
        settings.llm_temperature = 0.3
        settings.llm_max_tokens = 4096
        settings.llm_timeout = 30
        mock_get_settings.return_value = settings

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"summary": "ok", "score": 7}'
        mock_model.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model

        provider = GeminiProvider()
        provider._settings = settings

        result = provider.generate_structured(
            "Test prompt",
            response_model=_SampleResponse,
            use_cache=False,
        )

        assert isinstance(result, _SampleResponse)
        assert result.summary == "ok"
        assert result.score == 7

        config = mock_model_cls.call_args.kwargs["generation_config"]
        assert config.response_mime_type == "application/json"
        assert config.response_schema is _SampleResponse

    @patch("app.services.llm_provider.genai.GenerativeModel")
    @patch("app.services.llm_provider.GeminiProvider._ensure_client")
    @patch("app.services.llm_provider.get_settings")
    def test_generate_structured_validation_error_retries_then_raises(
        self, mock_get_settings, _mock_ensure, mock_model_cls
    ):
        settings = MagicMock()
        settings.google_api_key = "test-key"
        settings.llm_temperature = 0.3
        settings.llm_max_tokens = 4096
        settings.llm_timeout = 30
        mock_get_settings.return_value = settings

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"summary": "ok"}'
        mock_model.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model

        provider = GeminiProvider()
        provider._settings = settings

        with pytest.raises(LLMResponseError):
            provider.generate_structured(
                "Test prompt",
                response_model=_SampleResponse,
                use_cache=False,
            )

        assert mock_model.generate_content.call_count == 3

    @patch("app.services.llm_provider.get_settings")
    def test_generate_structured_without_api_key(self, mock_get_settings):
        settings = MagicMock()
        settings.google_api_key = ""
        mock_get_settings.return_value = settings

        provider = GeminiProvider()
        provider._settings = settings

        with pytest.raises(LLMError, match="GOOGLE_API_KEY not configured"):
            provider.generate_structured("Test", response_model=_SampleResponse)

    @patch("app.services.llm_provider.genai.GenerativeModel")
    @patch("app.services.llm_provider.GeminiProvider._ensure_client")
    @patch("app.services.llm_provider.get_settings")
    def test_generate_structured_passes_system_prompt(self, mock_get_settings, _mock_ensure, mock_model_cls):
        settings = MagicMock()
        settings.google_api_key = "test-key"
        settings.llm_temperature = 0.3
        settings.llm_max_tokens = 4096
        settings.llm_timeout = 30
        mock_get_settings.return_value = settings

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"summary": "x", "score": 1}'
        mock_model.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model

        provider = GeminiProvider()
        provider._settings = settings

        provider.generate_structured(
            "User prompt",
            response_model=_SampleResponse,
            system_prompt="System prompt",
            use_cache=False,
        )

        full_prompt = mock_model.generate_content.call_args.args[0]
        assert "System prompt" in full_prompt
        assert "User prompt" in full_prompt


class TestGetLLMProvider:
    """팩토리 함수 테스트"""

    def setup_method(self):
        reset_provider()

    def test_default_returns_gemini(self):
        provider = get_llm_provider()
        assert isinstance(provider, GeminiProvider)

    def test_singleton_behavior(self):
        p1 = get_llm_provider()
        p2 = get_llm_provider()
        assert p1 is p2

    def test_reset_clears_provider(self):
        p1 = get_llm_provider()
        reset_provider()
        p2 = get_llm_provider()
        assert p1 is not p2

    @patch("app.services.llm_provider.get_settings")
    def test_unsupported_provider_raises(self, mock_get_settings):
        reset_provider()
        settings = MagicMock()
        settings.llm_provider = "openai"
        mock_get_settings.return_value = settings

        with pytest.raises(LLMError, match="Unsupported LLM provider"):
            get_llm_provider()

    def teardown_method(self):
        reset_provider()


class TestMockProviderReplacement:
    """Mock provider로 교체 가능한지 테스트"""

    def test_can_replace_with_mock(self):
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.generate.return_value = "mock response"
        mock_provider.generate_structured.return_value = _SampleResponse(summary="m", score=1)

        with patch("app.services.llm.get_llm_provider", return_value=mock_provider):
            from app.services.llm import call_llm, call_llm_structured

            assert call_llm("test") == "mock response"
            result = call_llm_structured("test", _SampleResponse)
            assert isinstance(result, _SampleResponse)
            assert result.summary == "m"
