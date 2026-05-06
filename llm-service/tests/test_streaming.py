"""D-6 Streaming SSE 단위 테스트 (ADR 0019)"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


class TestSseEvent:
    def test_format_basic(self):
        from app.services.streaming import sse_event

        out = sse_event({"hello": "world"})
        assert out.startswith("data: ")
        assert out.endswith("\n\n")
        body = out.replace("data: ", "").strip()
        assert json.loads(body) == {"hello": "world"}

    def test_with_event_name(self):
        from app.services.streaming import sse_event

        out = sse_event({"x": 1}, event="custom")
        assert "event: custom\n" in out
        assert "data: " in out
        assert out.endswith("\n\n")

    def test_korean_not_escaped(self):
        from app.services.streaming import sse_event

        out = sse_event({"msg": "샤프 비율"})
        assert "샤프 비율" in out


class TestSseDone:
    def test_done_signal_format(self):
        from app.services.streaming import sse_done

        out = sse_done()
        assert "event: done" in out
        assert "done" in out


class TestFormatHelpers:
    def test_token_event(self):
        from app.services.streaming import format_token_event

        out = format_token_event("hello")
        body = out.split("data: ", 1)[1].strip()
        data = json.loads(body)
        assert data == {"type": "token", "content": "hello"}

    def test_tool_event_includes_name_and_status(self):
        from app.services.streaming import format_tool_event

        out = format_tool_event("search_knowledge_base", "tool_start")
        assert "event: tool" in out
        body = out.split("data: ", 1)[1].strip()
        data = json.loads(body)
        assert data["name"] == "search_knowledge_base"
        assert data["status"] == "tool_start"

    def test_error_event(self):
        from app.services.streaming import format_error_event

        out = format_error_event("API down")
        assert "event: error" in out
        body = out.split("data: ", 1)[1].strip()
        data = json.loads(body)
        assert data["type"] == "error"
        assert "API down" in data["message"]


class TestReactAgentRunStream:
    @pytest.mark.asyncio
    async def test_yields_token_events(self):
        from app.agents.react_agent import ReActAgent

        chunk_msg = MagicMock()
        chunk_msg.content = "hello"

        async def fake_astream_events(*args, **kwargs):
            yield {"event": "on_chat_model_stream", "data": {"chunk": chunk_msg}}

        with patch("app.agents.react_agent.create_react_agent") as mock_create, \
             patch("app.agents.react_agent.ChatGoogleGenerativeAI"), \
             patch("app.agents.react_agent.get_tool_registry"), \
             patch("app.agents.react_agent.get_registry"):
            mock_agent = MagicMock()
            mock_agent.astream_events = fake_astream_events
            mock_create.return_value = mock_agent

            agent = ReActAgent()
            results = [c async for c in agent.run_stream("test")]
            assert len(results) == 1
            assert results[0]["type"] == "token"
            assert results[0]["content"] == "hello"

    @pytest.mark.asyncio
    async def test_yields_tool_events(self):
        from app.agents.react_agent import ReActAgent

        async def fake_astream_events(*args, **kwargs):
            yield {"event": "on_tool_start", "name": "search_knowledge_base"}
            yield {"event": "on_tool_end", "name": "search_knowledge_base"}

        with patch("app.agents.react_agent.create_react_agent") as mock_create, \
             patch("app.agents.react_agent.ChatGoogleGenerativeAI"), \
             patch("app.agents.react_agent.get_tool_registry"), \
             patch("app.agents.react_agent.get_registry"):
            mock_agent = MagicMock()
            mock_agent.astream_events = fake_astream_events
            mock_create.return_value = mock_agent

            agent = ReActAgent()
            results = [c async for c in agent.run_stream("test")]
            assert {r["type"] for r in results} == {"tool_start", "tool_end"}
            assert all(r["name"] == "search_knowledge_base" for r in results)

    @pytest.mark.asyncio
    async def test_skips_unknown_event_kinds(self):
        from app.agents.react_agent import ReActAgent

        async def fake_astream_events(*args, **kwargs):
            yield {"event": "on_chain_start", "name": "irrelevant"}
            yield {"event": "on_some_other_event"}

        with patch("app.agents.react_agent.create_react_agent") as mock_create, \
             patch("app.agents.react_agent.ChatGoogleGenerativeAI"), \
             patch("app.agents.react_agent.get_tool_registry"), \
             patch("app.agents.react_agent.get_registry"):
            mock_agent = MagicMock()
            mock_agent.astream_events = fake_astream_events
            mock_create.return_value = mock_agent

            agent = ReActAgent()
            results = [c async for c in agent.run_stream("test")]
            assert results == []
