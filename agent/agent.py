from mcp.server import MCPServer

from agent.tools.memory_tools import search_memory


mcp = MCPServer("career-mind-memory")


@mcp.tool()
def search_user_memory(
    user_id: str,
    query: str,
    limit: int = 5,
) -> list[dict]:
    """Search the user's stored memories using semantic similarity."""
    return search_memory(
        user_id=user_id,
        query=query,
        limit=limit,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")