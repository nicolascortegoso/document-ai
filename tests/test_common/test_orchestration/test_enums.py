from common.orchestration.enums import AgentEventType, MessageRole


class TestMessageRole:
    def test_members_equal_their_string_value(self) -> None:
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.TOOL == "tool"

    def test_constructible_from_raw_string(self) -> None:
        assert MessageRole("user") is MessageRole.USER


class TestAgentEventType:
    def test_members_equal_their_string_value(self) -> None:
        assert AgentEventType.DELTA == "delta"
        assert AgentEventType.TOOL_CALL == "tool_call"
        assert AgentEventType.TOOL_RESULT == "tool_result"
        assert AgentEventType.FINAL == "final"

    def test_constructible_from_raw_string(self) -> None:
        assert AgentEventType("final") is AgentEventType.FINAL
