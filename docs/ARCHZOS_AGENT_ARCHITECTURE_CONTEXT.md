# ArchzOS Agent Architecture Context

This repository is designed to fit the existing ArchzOS architecture principles:

## 1) Centralized control plane

ArchzOS is already organized around a centralized vault/control pattern
(`auth.archzos.com` vault-first runtime configuration model). `trifecta-guard`
extends that same control-plane approach into agent execution paths.

## 2) Runtime enforcement, not prompt-only safety

Prompt injection is treated as a systems security problem. This repo enforces:
- explicit tool capability tagging,
- session-level taint accumulation,
- policy-based hard stops or escalation.

This avoids relying on "model says no" behavior.

## 3) Agent architecture integration points

- MCP servers/clients: wrap tool registries and gate every tool invocation.
- LangGraph agents: apply pre-tool hooks and post-tool commit hooks.
- Observability layer: emit policy decisions to OTel-compatible pipelines.

## 4) ArchzOS rollout plan

1. Tag existing tools used by ArchzOS agents (`reads_private_data`,
   `sees_untrusted_content`, `can_exfiltrate`).
2. Run in audit mode first (record and alert only).
3. Move to block mode for high-risk workflows.
4. Add HITL approval for narrowly scoped exception routes.
5. Publish policy metrics into existing ArchzOS status/security dashboards.
