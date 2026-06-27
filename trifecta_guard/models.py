from __future__ import annotations

from enum import Enum
from typing import Iterable

from pydantic import BaseModel, Field


class Capability(str, Enum):
    READS_PRIVATE_DATA = "reads_private_data"
    SEES_UNTRUSTED_CONTENT = "sees_untrusted_content"
    CAN_EXFILTRATE = "can_exfiltrate"


class GuardAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    HUMAN_APPROVAL = "hitl"
    FRESH_SESSION = "fresh_session"
    SECURE_ENV = "secure_env"


class ToolSpec(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    capabilities: set[Capability] = Field(default_factory=set)

    @classmethod
    def from_flags(
        cls,
        name: str,
        *,
        reads_private_data: bool = False,
        sees_untrusted_content: bool = False,
        can_exfiltrate: bool = False,
        description: str | None = None,
    ) -> "ToolSpec":
        caps: set[Capability] = set()
        if reads_private_data:
            caps.add(Capability.READS_PRIVATE_DATA)
        if sees_untrusted_content:
            caps.add(Capability.SEES_UNTRUSTED_CONTENT)
        if can_exfiltrate:
            caps.add(Capability.CAN_EXFILTRATE)
        return cls(name=name, description=description, capabilities=caps)


class PolicyDecision(BaseModel):
    action: GuardAction
    reason: str
    matched_capabilities: set[Capability] = Field(default_factory=set)
    required_approval_roles: list[str] = Field(default_factory=list)


class ToolCallRecord(BaseModel):
    tool_name: str
    capabilities: set[Capability] = Field(default_factory=set)


def capability_set(values: Iterable[Capability]) -> set[Capability]:
    return set(values)
