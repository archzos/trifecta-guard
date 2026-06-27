# Research Notes (June 2026)

These references informed the architecture and threat model in this repo.

## Core references

- Simon Willison, "The lethal trifecta for AI agents" (June 16, 2025): frames the
  high-risk capability composition.
- Model Context Protocol Specification (version 2025-03-26): emphasizes security
  and trust/safety duties for implementers.
- LangChain/LangGraph middleware docs: shows where to place runtime hooks that
  consistently enforce policy in graph execution.
- OWASP MCP Security Cheat Sheet: practical MCP threat controls and hardening patterns.

## Notes on "Agents Rule of Two"

The "Rule of Two" framing is widely discussed in secondary sources and referenced
by Simon Willison as tied to a Meta publication in late 2025. Direct official
source discovery may vary by indexing availability at query time. The enforceable
engineering takeaway is to prevent a single session from combining all three
dangerous capabilities without strict controls.

## Design implications used here

1. Treat prompt injection as fundamentally unresolved in-model.
2. Enforce capability composition constraints at middleware/runtime.
3. Prefer deterministic, auditable policies over model-intent inference.
4. Include explicit escalation paths: HITL, fresh session, or isolated env.
