from pathlib import Path

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


def test_policy_can_load_from_config_file() -> None:
    config_path = Path(__file__).resolve().parents[1] / "config" / "policy.json"
    policy = GuardPolicy.from_config_file(config_path)
    decision = policy.evaluate(
        {
            Capability.READS_PRIVATE_DATA,
            Capability.SEES_UNTRUSTED_CONTENT,
            Capability.CAN_EXFILTRATE,
        }
    )
    assert decision.action == GuardAction.BLOCK
