from trifecta_guard.cli import parse_chain
from trifecta_guard.models import Capability


def test_parse_chain_parses_capabilities() -> None:
    tools = parse_chain("gmail_read:private,web_fetch:untrusted,http_post:exfil")
    assert len(tools) == 3
    assert Capability.READS_PRIVATE_DATA in tools[0].capabilities
    assert Capability.SEES_UNTRUSTED_CONTENT in tools[1].capabilities
    assert Capability.CAN_EXFILTRATE in tools[2].capabilities
