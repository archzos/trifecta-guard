from __future__ import annotations

from dataclasses import dataclass, field

from trifecta_guard.models import Capability, GuardAction, PolicyDecision


@dataclass(slots=True)
class PolicyRule:
    name: str
    required_capabilities: set[Capability]
    action: GuardAction
    reason: str
    required_approval_roles: list[str] = field(default_factory=list)

    def matches(self, capabilities: set[Capability]) -> bool:
        return self.required_capabilities.issubset(capabilities)


class GuardPolicy:
    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        if rules is not None:
            self._rules = rules
            return

        trifecta = {
            Capability.READS_PRIVATE_DATA,
            Capability.SEES_UNTRUSTED_CONTENT,
            Capability.CAN_EXFILTRATE,
        }
        self._rules = [
            PolicyRule(
                name="lethal_trifecta_block",
                required_capabilities=trifecta,
                action=GuardAction.BLOCK,
                reason=(
                    "Blocked lethal-trifecta path in a single session. "
                    "Route through HITL or split capabilities across isolated sessions."
                ),
                required_approval_roles=["security_reviewer"],
            ),
        ]

    @property
    def rules(self) -> list[PolicyRule]:
        return list(self._rules)

    def evaluate(self, capabilities: set[Capability]) -> PolicyDecision:
        for rule in self._rules:
            if rule.matches(capabilities):
                return PolicyDecision(
                    action=rule.action,
                    reason=rule.reason,
                    matched_capabilities=capabilities,
                    required_approval_roles=rule.required_approval_roles,
                )

        return PolicyDecision(
            action=GuardAction.ALLOW,
            reason="No blocking policy matched.",
            matched_capabilities=capabilities,
        )
