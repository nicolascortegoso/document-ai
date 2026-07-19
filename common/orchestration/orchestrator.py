from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from common.orchestration.models import AgentEvent, ConversationState


class Orchestrator(ABC):
    @abstractmethod
    async def arun(self, session_id: str, user_input: str) -> ConversationState: ...

    @abstractmethod
    def astream(self, session_id: str, user_input: str) -> AsyncIterator[AgentEvent]: ...
