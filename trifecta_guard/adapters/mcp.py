from __future__ import annotations

from collections.abc import Callable
from typing import Any

from trifecta_guard.middleware import ToolExecutionContext, TrifectaMiddleware
from trifecta_guard.models import ToolSpec


class MCPToolRegistryGuard:
    """
    Wrapper for MCP-like tool registries.
    Expects registry format: {tool_name: callable}.
    """

    def __init__(
        self,
        middleware: TrifectaMiddleware,
        tool_specs: dict[str, ToolSpec],
    ) -> None:
        self.middleware = middleware
        self.tool_specs = tool_specs

    def wrap_registry(
        self,
        registry: dict[str, Callable[..., Any]],
    ) -> dict[str, Callable[..., Any]]:
        wrapped: dict[str, Callable[..., Any]] = {}
        for name, func in registry.items():
            spec = self.tool_specs.get(name, ToolSpec(name=name))

            def make_wrapper(
                tool_name: str,
                tool_spec: ToolSpec,
                tool_func: Callable[..., Any],
            ) -> Callable[..., Any]:
                def guarded(session_id: str, **kwargs: Any) -> Any:
                    ctx = ToolExecutionContext(
                        session_id=session_id,
                        tool=tool_spec,
                        args=kwargs,
                    )
                    return self.middleware.run_guarded(
                        ctx,
                        lambda context: tool_func(**context.args),
                    )

                guarded.__name__ = f"guarded_{tool_name}"
                return guarded

            wrapped[name] = make_wrapper(name, spec, func)
        return wrapped
