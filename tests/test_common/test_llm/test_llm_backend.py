from collections.abc import Sequence
from typing import Any

import pytest

from common.llm.llm_backend import LLMBackend
from common.orchestration.enums import MessageRole
from common.orchestration.models import Message


class EchoLLMBackend(LLMBackend):
    """Smallest possible implementation, used only to exercise the contract."""

    async def complete(self, messages: Sequence[Message], **kwargs: Any) -> Message:
        last = messages[-1] if messages else Message(role=MessageRole.USER, content="")
        return Message(role=MessageRole.ASSISTANT, content=last.content)


class TestLLMBackendContract:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            LLMBackend()  # type: ignore[abstract]

    def test_subclass_missing_complete_cannot_instantiate(self) -> None:
        class MissingComplete(LLMBackend):
            pass

        with pytest.raises(TypeError):
            MissingComplete()  # type: ignore[abstract]

    @pytest.mark.asyncio
    async def test_complete_returns_a_message(self) -> None:
        backend = EchoLLMBackend()
        result = await backend.complete([Message(role=MessageRole.USER, content="hi")])
        assert isinstance(result, Message)
        assert result.role == MessageRole.ASSISTANT
        assert result.content == "hi"

    @pytest.mark.asyncio
    async def test_complete_accepts_arbitrary_kwargs(self) -> None:
        backend = EchoLLMBackend()
        result = await backend.complete(
            [Message(role=MessageRole.USER, content="hi")], temperature=0.0, max_tokens=10
        )
        assert isinstance(result, Message)
