from typing import Any

import pytest

from common.tooling.tool import Tool


class EchoTool(Tool):
    """Smallest possible implementation, used only to exercise the contract."""

    @property
    def name(self) -> str:
        return "echo"

    async def execute(self, arguments: dict[str, Any]) -> str:
        return str(arguments.get("value", ""))


class TestToolContract:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            Tool()  # type: ignore[abstract]

    def test_subclass_missing_name_cannot_instantiate(self) -> None:
        class MissingName(Tool):
            async def execute(self, arguments: dict[str, Any]) -> str:
                return ""

        with pytest.raises(TypeError):
            MissingName()  # type: ignore[abstract]

    def test_subclass_missing_execute_cannot_instantiate(self) -> None:
        class MissingExecute(Tool):
            @property
            def name(self) -> str:
                return "x"

        with pytest.raises(TypeError):
            MissingExecute()  # type: ignore[abstract]

    def test_name_is_a_property(self) -> None:
        tool = EchoTool()
        assert tool.name == "echo"

    @pytest.mark.asyncio
    async def test_execute_returns_a_string(self) -> None:
        tool = EchoTool()
        result = await tool.execute({"value": "hello"})
        assert result == "hello"
