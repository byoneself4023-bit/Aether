"""D-6 SSE format 헬퍼 — Streaming endpoint 공통 (ADR 0019).

SSE format: `[event: <name>\\n]data: <json>\\n\\n`
"""

from __future__ import annotations

import json
from typing import Any


def sse_event(data: dict[str, Any], event: str | None = None) -> str:
    """SSE 단일 이벤트 — `data: {json}\\n\\n` (event 명시 시 prefix)."""
    parts = []
    if event:
        parts.append(f"event: {event}")
    parts.append(f"data: {json.dumps(data, ensure_ascii=False)}")
    return "\n".join(parts) + "\n\n"


def sse_done() -> str:
    """종료 시그널 — `event: done`."""
    return sse_event({"status": "done"}, event="done")


def format_token_event(token: str) -> str:
    """LLM token 청크."""
    return sse_event({"type": "token", "content": token})


def format_tool_event(tool_name: str, status: str, content: dict | None = None) -> str:
    """도구 호출 이벤트 (tool_start / tool_end)."""
    payload: dict[str, Any] = {"type": "tool", "name": tool_name, "status": status}
    if content is not None:
        payload["content"] = content
    return sse_event(payload, event="tool")


def format_error_event(error: str) -> str:
    """오류 이벤트 — stream 중단 시그널."""
    return sse_event({"type": "error", "message": error}, event="error")
