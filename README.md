# trifecta-guard

`trifecta-guard` is a runtime security linter and middleware layer for AI agents.
It enforces architectural guardrails against catastrophic prompt-injection paths by
tracking capability taint across tool calls.

## Why this exists

The critical risk pattern is the "lethal trifecta":
1. Reads private data.
2. Reads untrusted content.
3. Can communicate externally.

If a single agent session can do all three, prompt-injection exfiltration risk
becomes severe. `trifecta-guard` enforces policy before execution reaches that state.

## Core model

- `ToolTagging`: each tool is explicitly tagged with capabilities.
- `TaintEngine`: builds per-session capability state and call trace.
- `PolicyDSL`: maps risk states to actions (`allow`, `block`, `hitl`, `fresh_session`, `secure_env`).
- `Adapters`: integration shims for MCP tool registries and LangGraph middleware.
- `Telemetry`: optional OpenTelemetry events for violations and policy decisions.

## Architecture fit for ArchzOS

This repo aligns with ArchzOS vault-first and centralized control patterns:
- Capability policy is centralized, explicit, and auditable.
- Dangerous compositions are blocked at runtime, not by prompt heuristics.
- Human-in-the-loop escalation is available for high-risk transitions.

See [docs/ARCHZOS_AGENT_ARCHITECTURE_CONTEXT.md](docs/ARCHZOS_AGENT_ARCHITECTURE_CONTEXT.md).

## Quick start

```bash
cd trifecta-guard
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## CLI simulation

```bash
trifecta-guard \
  --policy config/policy.json \
  --chain "gmail_read:private,web_fetch:untrusted,http_post:exfil"
```

This prints per-tool decisions and will block on lethal-trifecta composition.

## Policy config

Policy is file-driven using `config/policy.json`. You can add additional rules with:
- `required_capabilities`
- `action` (`allow`, `block`, `hitl`, `fresh_session`, `secure_env`)
- `reason`
- `required_approval_roles`

## Minimal usage

```python
from trifecta_guard.models import ToolSpec, Capability
from trifecta_guard.policy import GuardPolicy
from trifecta_guard.taint_engine import TaintEngine

tools = [
    ToolSpec(name="gmail_read", capabilities={Capability.READS_PRIVATE_DATA}),
    ToolSpec(name="web_fetch", capabilities={Capability.SEES_UNTRUSTED_CONTENT}),
    ToolSpec(name="http_post", capabilities={Capability.CAN_EXFILTRATE}),
]

engine = TaintEngine(policy=GuardPolicy())
session_id = "sess-1"
for tool in tools:
    decision = engine.evaluate_tool_call(session_id, tool)
    print(tool.name, decision.action, decision.reason)
```

## Repo status

Initial scaffold with core engine, adapters, config-driven policy, CLI, tests, and CI.
