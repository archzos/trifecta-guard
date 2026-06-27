from __future__ import annotations

import argparse
import json
from pathlib import Path

from trifecta_guard.models import Capability, ToolSpec
from trifecta_guard.policy import GuardPolicy
from trifecta_guard.taint_engine import TaintEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trifecta-guard",
        description="Evaluate tool chains against lethal-trifecta guard policy.",
    )
    parser.add_argument(
        "--policy",
        default="config/policy.json",
        help="Path to policy JSON file (default: config/policy.json).",
    )
    parser.add_argument(
        "--chain",
        required=True,
        help=(
            "Comma-separated tool chain. Each item is "
            "name:cap1|cap2 where caps are private,untrusted,exfil."
        ),
    )
    parser.add_argument("--session-id", default="cli-session")
    return parser


def parse_capability_token(token: str) -> Capability:
    mapping = {
        "private": Capability.READS_PRIVATE_DATA,
        "untrusted": Capability.SEES_UNTRUSTED_CONTENT,
        "exfil": Capability.CAN_EXFILTRATE,
    }
    key = token.strip().lower()
    if key not in mapping:
        raise ValueError(f"Unknown capability token: {token}")
    return mapping[key]


def parse_chain(spec: str) -> list[ToolSpec]:
    tools: list[ToolSpec] = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            name, caps_raw = item.split(":", 1)
            cap_tokens = [part.strip() for part in caps_raw.split("|") if part.strip()]
            capabilities = {parse_capability_token(token) for token in cap_tokens}
        else:
            name = item
            capabilities = set()
        tools.append(ToolSpec(name=name.strip(), capabilities=capabilities))
    if not tools:
        raise ValueError("No tools parsed from --chain.")
    return tools


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    policy_path = Path(args.policy)
    policy = GuardPolicy.from_config_file(policy_path) if policy_path.exists() else GuardPolicy()
    engine = TaintEngine(policy=policy)
    tools = parse_chain(args.chain)

    decisions = []
    for tool in tools:
        decision = engine.evaluate_tool_call(args.session_id, tool)
        decisions.append(
            {
                "tool": tool.name,
                "action": decision.action.value,
                "reason": decision.reason,
                "matched_capabilities": sorted(c.value for c in decision.matched_capabilities),
            }
        )
        if decision.action.value == "allow":
            engine.commit_tool_call(args.session_id, tool)

    print(json.dumps({"session_id": args.session_id, "decisions": decisions}, indent=2))


if __name__ == "__main__":
    main()
