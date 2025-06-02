"""
Agent Factory for Creating Specialized Agents

Creates different types of agents based on configuration.
"""

from typing import Optional, Dict, Any
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from pathlib import Path

from .config_loader import ProjectConfig, AgentConfig
from ..agents.base_agent import create_base_agent
from ..agents.meeting_agent import create_meeting_agent
from ..integrations.mcp_filesystem import create_filesystem_toolset


class AgentFactory:
    """Factory for creating specialized agents based on configuration."""
    
    def __init__(self, config: ProjectConfig):
        """
        Initialize the factory with project configuration.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.project_root = config.project.get('root_path', '.')
        
        # Registry of agent creation functions
        self.agent_creators = {
            'akashic_base': self._create_base_agent,
            'meeting_minutes': self._create_meeting_agent,
            'template_manager': self._create_template_agent,
            'custom': self._create_custom_agent
        }
    
    def create_agent(self, name: str, agent_config: AgentConfig) -> Optional[Agent]:
        """
        Create an agent based on its configuration.
        
        Args:
            name: Name of the agent
            agent_config: Agent configuration
            
        Returns:
            Optional[Agent]: Created agent or None if creation failed
        """
        creator = self.agent_creators.get(agent_config.type)
        if not creator:
            print(f"Warning: Unknown agent type '{agent_config.type}' for agent '{name}'")
            return None
        
        try:
            return creator(name, agent_config)
        except Exception as e:
            print(f"Error creating agent '{name}': {e}")
            return None
    
    def _create_base_agent(self, name: str, config: AgentConfig) -> Agent:
        """Create an AkashicRecords Base Agent."""
        tools = []
        
        # Add filesystem tools if configured
        if self.config.mcp_tools.filesystem['enabled']:
            filesystem_toolset = create_filesystem_toolset(
                self.project_root,
                self.config.mcp_tools.filesystem.get('tools', [])
            )
            tools.append(filesystem_toolset)
        
        return create_base_agent(
            name=name,
            model=LiteLlm(model=config.model),
            project_root=self.project_root,
            prompt_template=config.prompt_template,
            tools=tools,
            permissions=config.permissions
        )
    
    def _create_meeting_agent(self, name: str, config: AgentConfig) -> Agent:
        """Create a Meeting Minutes Agent."""
        tools = []
        
        # Add filesystem tools if configured
        if self.config.mcp_tools.filesystem['enabled']:
            filesystem_toolset = create_filesystem_toolset(
                self.project_root,
                self.config.mcp_tools.filesystem.get('tools', [])
            )
            tools.append(filesystem_toolset)
        
        return create_meeting_agent(
            name=name,
            model=LiteLlm(model=config.model),
            project_root=self.project_root,
            prompt_template=config.prompt_template,
            tools=tools,
            target_directories=config.target_directories
        )
    
    def _create_template_agent(self, name: str, config: AgentConfig) -> Agent:
        """Create a Template Management Agent."""
        # Load template agent prompt
        prompt_content = self._load_prompt_template(config.prompt_template)
        if not prompt_content:
            prompt_content = self._get_default_template_prompt()
        
        tools = []
        if self.config.mcp_tools.filesystem['enabled']:
            filesystem_toolset = create_filesystem_toolset(
                self.project_root,
                self.config.mcp_tools.filesystem.get('tools', [])
            )
            tools.append(filesystem_toolset)
        
        return Agent(
            name=name,
            model=LiteLlm(model=config.model),
            description="Template management agent for AkashicRecords",
            instruction=prompt_content,
            tools=tools
        )
    
    def _create_custom_agent(self, name: str, config: AgentConfig) -> Agent:
        """Create a custom agent based on configuration."""
        prompt_content = self._load_prompt_template(config.prompt_template)
        if not prompt_content:
            prompt_content = f"You are {name}, a specialized agent for this AkashicRecords project."
        
        tools = []
        if self.config.mcp_tools.filesystem['enabled']:
            filesystem_toolset = create_filesystem_toolset(
                self.project_root,
                self.config.mcp_tools.filesystem.get('tools', [])
            )
            tools.append(filesystem_toolset)
        
        return Agent(
            name=name,
            model=LiteLlm(model=config.model),
            description=f"Custom agent: {name}",
            instruction=prompt_content,
            tools=tools
        )
    
    def _load_prompt_template(self, template_path: Optional[str]) -> Optional[str]:
        """
        Load prompt template from file.
        
        Args:
            template_path: Path to the prompt template file
            
        Returns:
            Optional[str]: Prompt content or None if not found
        """
        if not template_path:
            return None
        
        try:
            # Try relative to .arclient first
            arclient_path = Path(self.project_root) / '.arclient' / template_path
            if arclient_path.exists():
                with open(arclient_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Try absolute path
            abs_path = Path(template_path)
            if abs_path.exists():
                with open(abs_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
        except Exception as e:
            print(f"Warning: Could not load prompt template {template_path}: {e}")
        
        return None
    
    def _get_default_template_prompt(self) -> str:
        """Get default template agent prompt."""
        return """You are a Template Management Agent for the AkashicRecords system.

Your responsibilities include:

1. **Template Discovery**: Find and catalog available templates
2. **Template Application**: Apply templates to create new project structures
3. **Template Validation**: Ensure templates are properly formatted and functional
4. **Template Customization**: Help users customize templates for their needs

You work with the AkashicRecords template system to help users quickly set up structured knowledge bases for their projects."""