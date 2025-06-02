"""
MCP Filesystem Integration for AkashicRecords

Provides filesystem tools using Model Context Protocol.
"""

from typing import List, Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


def create_filesystem_toolset(
    root_path: str,
    allowed_tools: Optional[List[str]] = None
) -> MCPToolset:
    """
    Create an MCP filesystem toolset for the given root path.
    
    Args:
        root_path: Root directory path for filesystem operations
        allowed_tools: List of allowed tools, or None for all tools
        
    Returns:
        MCPToolset: Configured filesystem toolset
    """
    # Default tools if none specified
    if allowed_tools is None:
        allowed_tools = [
            'read_file',
            'write_file', 
            'list_directory',
            'create_directory',
            'search_files',
            'get_file_info'
        ]
    
    # Create MCP toolset for filesystem operations
    return MCPToolset(
        connection_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                root_path
            ]
        ),
        tool_filter=allowed_tools
    )


def create_akashic_mcp_server(project_root: str) -> MCPToolset:
    """
    Create a specialized MCP server for AkashicRecords operations.
    
    This would eventually connect to a custom MCP server that understands
    AkashicRecords directory rules and provides higher-level operations.
    
    Args:
        project_root: Root directory of the AkashicRecords project
        
    Returns:
        MCPToolset: Configured AkashicRecords MCP toolset
    """
    # For now, use the standard filesystem server
    # In the future, this could connect to a custom AkashicRecords MCP server
    # that understands README.md rules, directory structures, etc.
    
    return create_filesystem_toolset(
        root_path=project_root,
        allowed_tools=[
            'read_file',
            'write_file',
            'list_directory', 
            'create_directory',
            'search_files',
            'get_file_info',
            'move_file'
        ]
    )