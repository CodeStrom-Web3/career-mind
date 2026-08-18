"""
MCP client / dispatcher abstraction.

Provides a thin dispatch layer so the agent service can invoke MCP tools
by name without managing database connections directly.  The client
looks up tools in the registry and executes them with the supplied
arguments.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.mcp.tools import TOOL_DEFINITIONS, TOOL_REGISTRY
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    """
    MCP dispatcher that routes tool calls to their implementations.

    Usage::

        client = MCPClient()
        result = await client.call_tool(
            db=session,
            tool_name="search_user_memory",
            arguments={"user_id": "...", "query": "..."},
        )
    """

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the list of available MCP tool definitions."""
        return TOOL_DEFINITIONS

    async def call_tool(
        self,
        db: AsyncSession,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Dispatch a tool call by name.

        Args:
            db: Active database session (injected by the caller).
            tool_name: Registered tool name.
            arguments: Keyword arguments for the tool function.

        Returns:
            The tool's return value.

        Raises:
            ValueError: If the tool name is not registered.
        """
        handler = TOOL_REGISTRY.get(tool_name)
        if handler is None:
            raise ValueError(f"Unknown MCP tool: {tool_name}")

        logger.info(
            "MCP tool invoked",
            extra={"service": "mcp", "tool": tool_name},
        )
        return await handler(db=db, **arguments)


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: MCPClient | None = None


def get_mcp_client() -> MCPClient:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = MCPClient()
    return _instance
