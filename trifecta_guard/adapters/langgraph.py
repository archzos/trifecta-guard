from __future__ import annotations

from typing import Any

from trifecta_guard.middleware import ToolExecutionContext, TrifectaMiddleware
from trifecta_guard.models import ToolSpec


class LangGraphGuardMiddleware:
    """
    Lightweight adapter for LangGraph/LangChain middleware hooks.
    """

    def __init__(self, middleware: TrifectaMiddleware, tool_specs: dict[str, ToolSpec]) -> None:
        self.middleware = middleware
        self.tool_specs = tool_specs

    def before_tool(self, session_id: str, tool_name: str, tool_input: dict[str, Any]) -> None:
        spec = self.tool_specs.get(tool_name, ToolSpec(name=tool_name))
        ctx = ToolExecutionContext(session_id=session_id, tool=spec, args=tool_input)
        self.middleware.guard(ctx)

    def after_tool(self, session_id: str, tool_name: str, tool_input: dict[str, Any]) -> None:
        spec = self.tool_specs.get(tool_name, ToolSpec(name=tool_name))
        self.middleware.engine.commit_tool_call(session_id, spec)
