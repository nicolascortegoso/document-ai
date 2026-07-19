import dataclasses

import pytest

from common.orchestration.enums import AgentEventType, MessageRole
from common.orchestration.models import AgentEvent, ConversationState, Message


class TestMessage:
    def test_metadata_defaults_to_empty_dict(self) -> None:
        message = Message(role=MessageRole.USER, content="hi")
        assert message.metadata == {}

    def test_default_metadata_is_not_shared_between_instances(self) -> None:
        a = Message(role=MessageRole.USER, content="a")
        b = Message(role=MessageRole.USER, content="b")
        a.metadata["k"] = "v"
        assert b.metadata == {}

    def test_is_frozen(self) -> None:
        message = Message(role=MessageRole.USER, content="hi")
        with pytest.raises(dataclasses.FrozenInstanceError):
            message.content = "changed"  # type: ignore[misc]

    def test_equality_is_value_based(self) -> None:
        a = Message(role=MessageRole.USER, content="hi")
        b = Message(role=MessageRole.USER, content="hi")
        assert a == b


class TestConversationState:
    def test_holds_session_id_and_messages(self) -> None:
        message = Message(role=MessageRole.USER, content="hi")
        state = ConversationState(session_id="s1", messages=[message])
        assert state.session_id == "s1"
        assert state.messages == [message]

    def test_messages_are_mutable_in_place(self) -> None:
        state = ConversationState(session_id="s1", messages=[])
        state.messages.append(Message(role=MessageRole.USER, content="hi"))
        assert len(state.messages) == 1


class TestAgentEvent:
    def test_holds_type_and_payload(self) -> None:
        event = AgentEvent(type=AgentEventType.DELTA, payload="chunk")
        assert event.type == AgentEventType.DELTA
        assert event.payload == "chunk"

    def test_is_frozen(self) -> None:
        event = AgentEvent(type=AgentEventType.FINAL, payload=None)
        with pytest.raises(dataclasses.FrozenInstanceError):
            event.payload = "x"  # type: ignore[misc]
