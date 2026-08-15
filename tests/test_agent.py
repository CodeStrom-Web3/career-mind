import asyncio
from typing import Any

from agent.agent import mcp


def test_mcp_tool_is_registered():
    async def check():
        tools = await mcp.list_tools()
        names = [tool.name for tool in tools]

        assert "search_user_memory" in names

    asyncio.run(check())


def test_mcp_memory_search():
    async def check():
        result: Any = await mcp.call_tool(
            "search_user_memory",
            {
                "user_id": "user_001",
                "query": "What career does the user want?",
                "limit": 3,
            },
        )

        assert result.is_error is False
        assert result.structured_content is not None

        memories = result.structured_content["result"]

        assert len(memories) > 0
        assert any(
            "Data Analyst" in memory["content"]
            for memory in memories
        )

    asyncio.run(check())