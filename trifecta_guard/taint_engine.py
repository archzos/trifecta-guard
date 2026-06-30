from __future__ import annotations

from dataclasses import dataclass, field

from trifecta_guard.models import Capability, PolicyDecision, ToolCallRecord, ToolSpec
from trifecta_guard.policy import GuardPolicy


@dataclass(slots=True)
class SessionState:
    session_id: str
    capabilities: set[Capability] = field(default_factory=set)
    trace: list[ToolCallRecord] = field(default_factory=list)

    def clone_with(self, tool: ToolSpec) -> "SessionState":
        return SessionState(
            session_id=self.session_id,
            capabilities=self.capabilities.union(tool.capabilities),
            trace=self.trace + [ToolCallRecord(tool_name=tool.name, capabilities=tool.capabilities)],
        )


class TaintEngine:
    def __init__(self, policy: GuardPolicy | None = None) -> None:
        self._policy = policy or GuardPolicy()
        self._sessions: dict[str, SessionState] = {}

    def get_state(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)
        return self._sessions[session_id]

    def evaluate_tool_call(self, session_id: str, tool: ToolSpec) -> PolicyDecision:
        current = self.get_state(session_id)
        candidate = current.clone_with(tool)
        return self._policy.evaluate(candidate.capabilities)

    def commit_tool_call(self, session_id: str, tool: ToolSpec) -> SessionState:
        current = self.get_state(session_id)
        updated = current.clone_with(tool)
        self._sessions[session_id] = updated
        return updated

    def reset_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
