from dataclasses import dataclass, field
from typing import Any

from common.orchestration.enums import AgentEventType, MessageRole


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    session_id: str
    messages: list[Message]


@dataclass(frozen=True)
class AgentEvent:
    type: AgentEventType
    payload: Any
