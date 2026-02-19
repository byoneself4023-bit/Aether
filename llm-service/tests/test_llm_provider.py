"""Major #6: LLM Provider 추상화 테스트"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.llm_provider import (
    LLMProvider,
    GeminiProvider,
    get_llm_provider,
    reset_provider,
    LLMError,
    JSONParseError,
    _extract_json,
)


class TestLLMProviderProtocol:
    """LLMProvider Protocol 테스트"""

    def test_gemini_provider_satisfies_protocol(self):
        """GeminiProvider가 LLMProvider Protocol을 만족하는지"""
        assert isinstance(GeminiProvider(), LLMProvider)

    def test_mock_provider_satisfies_protocol(self):
        """Mock provider도 Protocol을 만족하는지"""
        mock = MagicMock(spec=LLMProvider)
        assert isinstance(mock, LLMProvider)


class TestGeminiProvider:
    """GeminiProvider 구현 테스트"""

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
        result = provider.generate("Test prompt")

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

    @patch("app.services.llm_provider.GeminiProvider._get_model")
    @patch("app.services.llm_provider.get_settings")
    def test_generate_json_success(self, mock_get_settings, mock_get_model):
        settings = MagicMock()
        settings.google_api_key = "test-key"
        settings.llm_temperature = 0.7
        settings.llm_max_tokens = 2048
        settings.llm_timeout = 30
        mock_get_settings.return_value = settings

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"result": "success"}'
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model

        provider = GeminiProvider()
        provider._settings = settings
        result = provider.generate_json("Test prompt")

        assert result == {"result": "success"}


class TestGetLLMProvider:
    """팩토리 함수 테스트"""

    def setup_method(self):
        reset_provider()

    def test_default_returns_gemini(self):
        """기본 provider는 GeminiProvider"""
        provider = get_llm_provider()
        assert isinstance(provider, GeminiProvider)

    def test_singleton_behavior(self):
        """같은 인스턴스를 반환"""
        p1 = get_llm_provider()
        p2 = get_llm_provider()
        assert p1 is p2

    def test_reset_clears_provider(self):
        """reset 후 새 인스턴스 생성"""
        p1 = get_llm_provider()
        reset_provider()
        p2 = get_llm_provider()
        assert p1 is not p2

    @patch("app.services.llm_provider.get_settings")
    def test_unsupported_provider_raises(self, mock_get_settings):
        """지원하지 않는 provider 설정 시 에러"""
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
        """get_llm_provider를 mock으로 교체"""
        mock_provider = MagicMock(spec=LLMProvider)
        mock_provider.generate.return_value = "mock response"
        mock_provider.generate_json.return_value = {"mock": True}

        with patch("app.services.llm.get_llm_provider", return_value=mock_provider):
            from app.services.llm import call_llm, call_llm_json

            assert call_llm("test") == "mock response"
            assert call_llm_json("test") == {"mock": True}


class TestExtractJson:
    """_extract_json 테스트 (provider 모듈로 이동)"""

    def test_plain_json(self):
        result = _extract_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_with_markdown_block(self):
        result = _extract_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}
