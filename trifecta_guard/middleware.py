from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from trifecta_guard.models import GuardAction, ToolSpec
from trifecta_guard.taint_engine import TaintEngine


class GuardViolationError(RuntimeError):
    pass


@dataclass(slots=True)
class ToolExecutionContext:
    session_id: str
    tool: ToolSpec
    args: dict[str, Any]


class TrifectaMiddleware:
    def __init__(self, engine: TaintEngine | None = None) -> None:
        self.engine = engine or TaintEngine()

    def guard(self, ctx: ToolExecutionContext) -> None:
        decision = self.engine.evaluate_tool_call(ctx.session_id, ctx.tool)
        if decision.action == GuardAction.ALLOW:
            return
        raise GuardViolationError(
            f"{decision.action.value}: {decision.reason} "
            f"(tool={ctx.tool.name}, session={ctx.session_id})"
        )

    def run_guarded(
        self,
        ctx: ToolExecutionContext,
        executor: Callable[[ToolExecutionContext], Any],
    ) -> Any:
        self.guard(ctx)
        result = executor(ctx)
        self.engine.commit_tool_call(ctx.session_id, ctx.tool)
        return result
