from __future__ import annotations

from typing import Any

from trifecta_guard.models import PolicyDecision, ToolSpec

try:
    from opentelemetry import trace
except Exception:  # pragma: no cover - optional dependency
    trace = None


class TelemetryEmitter:
    def __init__(self, tracer_name: str = "trifecta-guard") -> None:
        self._tracer_name = tracer_name

    def emit_decision(
        self,
        session_id: str,
        tool: ToolSpec,
        decision: PolicyDecision,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if trace is None:
            return
        tracer = trace.get_tracer(self._tracer_name)
        with tracer.start_as_current_span("trifecta_guard.policy_decision") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("tool.name", tool.name)
            span.set_attribute("decision.action", decision.action.value)
            span.set_attribute("decision.reason", decision.reason)
            span.set_attribute(
                "decision.capabilities",
                ",".join(sorted(c.value for c in decision.matched_capabilities)),
            )
            if metadata:
                for key, value in metadata.items():
                    span.set_attribute(f"meta.{key}", str(value))
