"""
Agent Factory for Creating Configuration-Driven Agents

Creates agents based on configuration using a simplified approach.
"""

from typing import Optional
from google.adk import Agent

from .config_loader import ProjectConfig, AgentConfig
from ..agents.generic_agent import create_agent
from ..integrations.mcp_filesystem import create_filesystem_toolset


class AgentFactory:
    """Factory for creating configuration-driven agents."""
    
    def __init__(self, config: ProjectConfig, project_root: str = '.'):
        """
        Initialize the factory with project configuration.
        
        Args:
            config: Project configuration
            project_root: Project root path (from environment or discovery)
        """
        self.config = config
        self.project_root = project_root
    
    def create_agent(self, name: str, agent_config: AgentConfig) -> Optional[Agent]:
        """
        Create an agent based on its configuration.
        
        Args:
            name: Name of the agent
            agent_config: Agent configuration
            
        Returns:
            Optional[Agent]: Created agent or None if creation failed
        """
        try:
            # Prepare tools based on agent configuration
            tools = []
            
            # Add filesystem tools if any MCP-based tool is requested
            needs_filesystem = any(tool in ["mcp_filesystem", "akashic_mcp"] for tool in agent_config.tools)
            if needs_filesystem and self.config.mcp_tools.filesystem['enabled']:
                filesystem_toolset = create_filesystem_toolset(self.project_root)
                tools.append(filesystem_toolset)
            
            # Create agent with configuration
            return create_agent(
                name=name,
                model=agent_config.model,
                project_root=self.project_root,
                prompt_template=agent_config.prompt_template,
                tools=tools,
                description=f"Agent: {name} (type: {agent_config.type})",
                agent_type=agent_config.type,
                permissions=agent_config.permissions,
                target_directories=getattr(agent_config, 'target_directories', None),
                max_output_tokens=agent_config.max_output_tokens,
                max_context_tokens=agent_config.max_context_tokens
            )
        except Exception as e:
            print(f"Error creating agent '{name}': {e}")
            return None
