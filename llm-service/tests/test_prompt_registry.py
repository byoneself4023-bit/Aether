"""Major #8: 프롬프트 버전 관리 테스트"""

import pytest
import time

from app.services.prompt_registry import (
    PromptTemplate,
    PromptRegistry,
    get_registry,
)


class TestPromptTemplate:
    def test_create_template(self):
        pt = PromptTemplate(
            name="test",
            version="1.0",
            template="Hello {{ name }}",
        )
        assert pt.name == "test"
        assert pt.version == "1.0"
        assert pt.created_at is not None


class TestPromptRegistry:
    def setup_method(self):
        self.registry = PromptRegistry()

    def test_register_and_get(self):
        """프롬프트 등록 후 조회"""
        self.registry.register("greeting", "1.0", "Hello!")
        result = self.registry.get("greeting")
        assert result.template == "Hello!"
        assert result.version == "1.0"

    def test_get_specific_version(self):
        """특정 버전 조회"""
        self.registry.register("greeting", "1.0", "Hello v1!")
        time.sleep(0.01)
        self.registry.register("greeting", "2.0", "Hello v2!")

        v1 = self.registry.get("greeting", version="1.0")
        assert v1.template == "Hello v1!"

        v2 = self.registry.get("greeting", version="2.0")
        assert v2.template == "Hello v2!"

    def test_get_latest_version(self):
        """최신 버전 반환"""
        self.registry.register("greeting", "1.0", "Hello v1!")
        time.sleep(0.01)
        self.registry.register("greeting", "2.0", "Hello v2!")

        latest = self.registry.get("greeting")
        assert latest.version == "2.0"
        assert latest.template == "Hello v2!"

    def test_list_versions(self):
        """버전 히스토리"""
        self.registry.register("greeting", "1.0", "v1")
        time.sleep(0.01)
        self.registry.register("greeting", "1.1", "v1.1")
        time.sleep(0.01)
        self.registry.register("greeting", "2.0", "v2")

        versions = self.registry.list_versions("greeting")
        assert versions == ["1.0", "1.1", "2.0"]

    def test_list_versions_empty(self):
        """존재하지 않는 프롬프트"""
        versions = self.registry.list_versions("nonexistent")
        assert versions == []

    def test_get_nonexistent_raises(self):
        """존재하지 않는 프롬프트 조회 시 에러"""
        with pytest.raises(KeyError, match="Prompt not found"):
            self.registry.get("nonexistent")

    def test_get_nonexistent_version_raises(self):
        """존재하지 않는 버전 조회 시 에러"""
        self.registry.register("greeting", "1.0", "v1")
        with pytest.raises(KeyError, match="version not found"):
            self.registry.get("greeting", version="9.9")

    def test_overwrite_version(self):
        """같은 버전 등록 시 덮어쓰기"""
        self.registry.register("greeting", "1.0", "old")
        self.registry.register("greeting", "1.0", "new")

        result = self.registry.get("greeting", version="1.0")
        assert result.template == "new"

        versions = self.registry.list_versions("greeting")
        assert len(versions) == 1

    def test_list_prompts(self):
        """등록된 프롬프트 목록"""
        self.registry.register("a", "1.0", "template a")
        self.registry.register("b", "1.0", "template b")

        names = self.registry.list_prompts()
        assert "a" in names
        assert "b" in names

    def test_metadata(self):
        """메타데이터 저장"""
        self.registry.register(
            "test", "1.0", "template",
            metadata={"author": "team", "description": "test prompt"},
        )
        result = self.registry.get("test")
        assert result.metadata["author"] == "team"


class TestGlobalRegistry:
    """글로벌 레지스트리 테스트"""

    def test_get_registry_returns_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_default_prompts_registered(self):
        """기본 프롬프트가 등록되어 있는지"""
        registry = get_registry()

        # system_prompt이 등록되어 있어야 함
        sp = registry.get("system_prompt")
        assert sp.version == "1.0"
        assert "Aether" in sp.template

    def test_default_schemas_registered(self):
        """기본 스키마 프롬프트가 등록되어 있는지"""
        registry = get_registry()

        names = registry.list_prompts()
        assert "portfolio_analysis_schema" in names
        assert "risk_explanation_schema" in names
        assert "backtest_summary_schema" in names
        assert "recommendation_schema" in names


class TestPromptsIntegration:
    """prompts.py 통합 테스트"""

    def test_get_system_prompt_uses_registry(self):
        """get_system_prompt()이 레지스트리를 사용하는지"""
        from app.services.prompts import get_system_prompt

        prompt = get_system_prompt()
        assert "Aether" in prompt

    def test_get_system_prompt_version(self):
        """특정 버전의 system prompt 조회"""
        from app.services.prompts import get_system_prompt

        prompt = get_system_prompt(version="1.0")
        assert "Aether" in prompt
