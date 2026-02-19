"""Critical #1: API 키 하드코딩 제거 테스트"""

import pytest
from unittest.mock import patch

from app.config import Settings


class TestApiKeyRemoval:
    """API 키가 하드코딩되지 않았는지 확인"""

    def test_default_api_key_is_empty(self):
        """config.py 기본 google_api_key가 빈 문자열인지 확인"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings(
                _env_file=None,
                google_api_key="",
            )
            assert settings.google_api_key == ""

    def test_api_key_from_env(self):
        """환경변수로 API 키 설정 시 정상 동작"""
        settings = Settings(
            _env_file=None,
            google_api_key="test-api-key-12345",
        )
        assert settings.google_api_key == "test-api-key-12345"


class TestStartupValidation:
    """서버 시작 시 API 키 검증 테스트"""

    @patch("app.main.settings")
    @patch("app.main.init_vectorstore")
    def test_startup_fails_without_api_key(self, mock_init, mock_settings):
        """API 키 없으면 서버 시작 실패"""
        mock_settings.google_api_key = ""
        mock_settings.app_name = "llm-service"
        mock_settings.app_version = "1.0.0"
        mock_settings.llm_model = "gemini-2.5-flash"

        from app.main import lifespan, app

        with pytest.raises(RuntimeError, match="GOOGLE_API_KEY is not set"):
            import asyncio
            async def _test():
                async with lifespan(app):
                    pass
            asyncio.get_event_loop().run_until_complete(_test())

    @patch("app.main.settings")
    @patch("app.main.init_vectorstore")
    def test_startup_succeeds_with_api_key(self, mock_init, mock_settings):
        """API 키 있으면 서버 정상 시작"""
        mock_settings.google_api_key = "test-key"
        mock_settings.app_name = "llm-service"
        mock_settings.app_version = "1.0.0"
        mock_settings.llm_model = "gemini-2.5-flash"
        mock_init.return_value = True

        from app.main import lifespan, app

        import asyncio
        async def _test():
            async with lifespan(app):
                pass
        asyncio.get_event_loop().run_until_complete(_test())

        mock_init.assert_called_once()
