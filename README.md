# trifecta-guard

[![CI](https://github.com/archzos/trifecta-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/archzos/trifecta-guard/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

`trifecta-guard` is runtime security middleware for AI agents. It enforces
capability-composition guardrails so dangerous prompt-injection pathways are
blocked at execution time, not left to model behavior.

## Why this project exists

Prompt injection becomes severe when one session can combine:
1. Reading private data.
2. Reading untrusted content.
3. Exfiltrating data externally.

This is the capability composition risk that `trifecta-guard` is designed to
detect and stop before the risky tool call runs.

## What it provides

- Tool capability tagging (`reads_private_data`, `sees_untrusted_content`, `can_exfiltrate`)
- Session-level taint tracking engine
- Deterministic policy evaluation
- Runtime middleware enforcement (`allow`, `block`, `hitl`, `fresh_session`, `secure_env`)
- Adapters for MCP-like tool registries and LangGraph middleware hooks
- CLI for local simulation and policy validation
- Optional OpenTelemetry and dashboard integration points

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick start

Run tests:

```bash
pytest
```

Run a policy simulation:

```bash
trifecta-guard \
  --policy config/policy.json \
  --chain "gmail_read:private,web_fetch:untrusted,http_post:exfil" \
  --session-id demo-1
```

Expected result: first two tools allowed, final tool blocked.

## Usage examples

### Example 1: Core SDK

```python
from trifecta_guard.models import Capability, ToolSpec
from trifecta_guard.policy import GuardPolicy
from trifecta_guard.taint_engine import TaintEngine

policy = GuardPolicy.from_config_file("config/policy.json")
engine = TaintEngine(policy=policy)
session_id = "sess-42"

tools = [
    ToolSpec(name="vault_read", capabilities={Capability.READS_PRIVATE_DATA}),
    ToolSpec(name="web_fetch", capabilities={Capability.SEES_UNTRUSTED_CONTENT}),
    ToolSpec(name="http_post", capabilities={Capability.CAN_EXFILTRATE}),
]

for tool in tools:
    decision = engine.evaluate_tool_call(session_id, tool)
    print(tool.name, decision.action.value, decision.reason)
    if decision.action.value == "allow":
        engine.commit_tool_call(session_id, tool)
```

### Example 2: MCP-style registry guard

```python
from trifecta_guard.adapters.mcp import MCPToolRegistryGuard
from trifecta_guard.middleware import TrifectaMiddleware
from trifecta_guard.models import Capability, ToolSpec

registry = {
    "web_fetch": lambda url: f"fetched {url}",
    "send_email": lambda to, body: f"sent to {to}",
}

tool_specs = {
    "web_fetch": ToolSpec(name="web_fetch", capabilities={Capability.SEES_UNTRUSTED_CONTENT}),
    "send_email": ToolSpec(name="send_email", capabilities={Capability.CAN_EXFILTRATE}),
}

wrapped = MCPToolRegistryGuard(
    middleware=TrifectaMiddleware(),
    tool_specs=tool_specs,
).wrap_registry(registry)

print(wrapped["web_fetch"](session_id="s1", url="https://example.com"))
```

### Example 3: LangGraph middleware adapter

```python
from trifecta_guard.adapters.langgraph import LangGraphGuardMiddleware
from trifecta_guard.middleware import TrifectaMiddleware
from trifecta_guard.models import Capability, ToolSpec

adapter = LangGraphGuardMiddleware(
    middleware=TrifectaMiddleware(),
    tool_specs={
        "gmail_read": ToolSpec(name="gmail_read", capabilities={Capability.READS_PRIVATE_DATA}),
        "http_post": ToolSpec(name="http_post", capabilities={Capability.CAN_EXFILTRATE}),
    },
)

adapter.before_tool("session-a", "gmail_read", {})
adapter.after_tool("session-a", "gmail_read", {})
```

## Policy configuration

Default policy file: `config/policy.json`

```json
{
  "rules": [
    {
      "name": "lethal_trifecta_block",
      "required_capabilities": [
        "reads_private_data",
        "sees_untrusted_content",
        "can_exfiltrate"
      ],
      "action": "block",
      "reason": "Blocked lethal-trifecta path in a single session.",
      "required_approval_roles": ["security_reviewer"]
    }
  ]
}
```

Supported actions:
- `allow`
- `block`
- `hitl`
- `fresh_session`
- `secure_env`

## Making this public

Before switching the repository visibility to public:
1. Verify no secrets in commit history.
2. Confirm `LICENSE`, `CONTRIBUTING.md`, and `SECURITY.md` are present.
3. Ensure CI is green on `main`.
4. Add maintainers and invite collaborators with least-privilege permissions.

## Open source and governance

- License: [MIT](./LICENSE)
- Contribution guide: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Security policy: [SECURITY.md](./SECURITY.md)
- Architecture context: [docs/ARCHZOS_AGENT_ARCHITECTURE_CONTEXT.md](./docs/ARCHZOS_AGENT_ARCHITECTURE_CONTEXT.md)

## Current status

Production-oriented starter with core policy enforcement, adapters, tests, and CI.
