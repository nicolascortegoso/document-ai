from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from common.orchestration.models import Message


class LLMBackend(ABC):
    @abstractmethod
    async def complete(self, messages: Sequence[Message], **kwargs: Any) -> Message: ...
