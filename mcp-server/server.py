"""
MCP Server for FinBank AI.
Provides banking tools via the Model Context Protocol.
"""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)

from tools import TOOLS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finbank-mcp")

# Create MCP server instance
server = Server("finbank-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available banking tools."""
    tools = []
    for name, config in TOOLS.items():
        tools.append(
            Tool(
                name=name,
                description=config["description"],
                inputSchema=config["parameters"]
            )
        )
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Execute a banking tool."""
    if name not in TOOLS:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")]
        )

    tool_config = TOOLS[name]
    tool_function = tool_config["function"]

    try:
        result = await tool_function(**arguments)
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def main():
    """Run the MCP server."""
    logger.info("Starting FinBank MCP Server...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
