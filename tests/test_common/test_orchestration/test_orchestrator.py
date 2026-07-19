from collections.abc import AsyncIterator

import pytest

from common.orchestration.enums import AgentEventType, MessageRole
from common.orchestration.models import AgentEvent, ConversationState, Message
from common.orchestration.orchestrator import Orchestrator


class MinimalOrchestrator(Orchestrator):
    """Smallest possible implementation, used only to exercise the contract."""

    async def arun(self, session_id: str, user_input: str) -> ConversationState:
        return ConversationState(
            session_id=session_id,
            messages=[Message(role=MessageRole.ASSISTANT, content=user_input)],
        )

    async def astream(self, session_id: str, user_input: str) -> AsyncIterator[AgentEvent]:
        yield AgentEvent(type=AgentEventType.DELTA, payload=user_input)
        yield AgentEvent(type=AgentEventType.FINAL, payload=None)


class TestOrchestratorContract:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            Orchestrator()  # type: ignore[abstract]

    def test_subclass_missing_arun_cannot_instantiate(self) -> None:
        class MissingArun(Orchestrator):
            async def astream(self, session_id: str, user_input: str) -> AsyncIterator[AgentEvent]:
                yield AgentEvent(type=AgentEventType.FINAL, payload=None)

        with pytest.raises(TypeError):
            MissingArun()  # type: ignore[abstract]

    def test_subclass_missing_astream_cannot_instantiate(self) -> None:
        class MissingAstream(Orchestrator):
            async def arun(self, session_id: str, user_input: str) -> ConversationState:
                return ConversationState(session_id=session_id, messages=[])

        with pytest.raises(TypeError):
            MissingAstream()  # type: ignore[abstract]

    @pytest.mark.asyncio
    async def test_arun_returns_conversation_state(self) -> None:
        orchestrator = MinimalOrchestrator()
        state = await orchestrator.arun(session_id="s1", user_input="hello")
        assert isinstance(state, ConversationState)
        assert state.session_id == "s1"

    @pytest.mark.asyncio
    async def test_astream_yields_agent_events(self) -> None:
        orchestrator = MinimalOrchestrator()
        events = [event async for event in orchestrator.astream(session_id="s1", user_input="hello")]
        assert all(isinstance(event, AgentEvent) for event in events)
        assert events[-1].type == AgentEventType.FINAL
