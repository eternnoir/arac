"""
MCP Filesystem Integration for AkashicRecords

Provides filesystem tools using Model Context Protocol.
"""

from typing import Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


def create_filesystem_toolset(root_path: str) -> MCPToolset:
    """
    Create an MCP filesystem toolset for the given root path.
    
    Args:
        root_path: Root directory path for filesystem operations
        
    Returns:
        MCPToolset: Configured filesystem toolset
    """
    # Create MCP toolset for filesystem operations
    # Let MCP protocol handle tool discovery dynamically
    return MCPToolset(
        connection_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                root_path
            ]
        )
    )


