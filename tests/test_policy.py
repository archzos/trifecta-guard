from trifecta_guard.models import Capability, GuardAction
from trifecta_guard.policy import GuardPolicy


def test_policy_blocks_lethal_trifecta() -> None:
    policy = GuardPolicy()
    decision = policy.evaluate(
        {
            Capability.READS_PRIVATE_DATA,
            Capability.SEES_UNTRUSTED_CONTENT,
            Capability.CAN_EXFILTRATE,
        }
    )
    assert decision.action == GuardAction.BLOCK


def test_policy_allows_non_trifecta() -> None:
    policy = GuardPolicy()
    decision = policy.evaluate(
        {
            Capability.READS_PRIVATE_DATA,
            Capability.SEES_UNTRUSTED_CONTENT,
        }
    )
    assert decision.action == GuardAction.ALLOW
