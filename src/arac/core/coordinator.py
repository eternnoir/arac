"""
AkashicRecords Coordinator Agent

The main coordinator that implements AkashicRecords logic and manages other agents.
"""

from typing import Dict, List, Any
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from litellm import Router

from .config_loader import ProjectConfig
from .agent_factory import AgentFactory
from ..integrations.mcp_filesystem import create_filesystem_toolset


class AkashicCoordinator:
    """
    Main coordinator for the AkashicRecords multi-agent system.
    
    Implements the core AkashicRecords logic for file-based knowledge management
    and coordinates with specialized agents.
    """
    
    def __init__(self, config: ProjectConfig):
        """
        Initialize the coordinator with project configuration.
        
        Args:
            config: Project configuration loaded from .arclient
        """
        self.config = config
        self.project_root = config.project.get('root_path', '.')
        self.factory = AgentFactory(config)
        
    def create_agent_hierarchy(self) -> Agent:
        """
        Create the complete agent hierarchy for this project.
        
        Returns:
            Agent: The root agent with all sub-agents configured
        """
        # Load coordinator prompt template
        coordinator_config = self.config.agents.get('coordinator')
        if not coordinator_config:
            raise ValueError("Coordinator agent configuration is required")
        
        # Load the coordinator prompt
        prompt_content = self._load_prompt_template(coordinator_config.prompt_template)
        
        # Create MCP filesystem tools
        mcp_tools = []
        if self.config.mcp_tools.filesystem['enabled']:
            filesystem_toolset = create_filesystem_toolset(
                self.project_root,
                self.config.mcp_tools.filesystem.get('tools', [])
            )
            mcp_tools.append(filesystem_toolset)
        
        # Create specialized sub-agents
        sub_agents = self._create_sub_agents()
        
        # Create the coordinator agent
        coordinator = Agent(
            name="akashic_coordinator",
            model=LiteLlm(model=coordinator_config.model),
            description="AkashicRecords coordinator agent for file-based knowledge management",
            instruction=prompt_content,
            tools=mcp_tools,
            sub_agents=sub_agents
        )
        
        return coordinator
    
    def _create_sub_agents(self) -> List[Agent]:
        """
        Create all enabled sub-agents based on configuration.
        
        Returns:
            List[Agent]: List of configured sub-agents
        """
        sub_agents = []
        
        for name, agent_config in self.config.agents.items():
            # Skip coordinator (it's the parent)
            if name == 'coordinator':
                continue
                
            if agent_config.enabled:
                agent = self.factory.create_agent(name, agent_config)
                if agent:
                    sub_agents.append(agent)
        
        return sub_agents
    
    def _load_prompt_template(self, template_path: str) -> str:
        """
        Load prompt template from file or return default.
        
        Args:
            template_path: Path to the prompt template file
            
        Returns:
            str: Prompt content
        """
        if not template_path:
            return self._get_default_coordinator_prompt()
        
        try:
            from pathlib import Path
            
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
        
        return self._get_default_coordinator_prompt()
    
    def _get_default_coordinator_prompt(self) -> str:
        """
        Get the default coordinator prompt based on AkashicRecords principles.
        
        Returns:
            str: Default coordinator prompt
        """
        return f"""You are the AkashicRecords Coordinator Agent, managing a file-based knowledge management system for the project "{self.config.project.get('name', 'Unknown')}" located at "{self.project_root}".

## Core Responsibilities

1. **File System Operations**: Navigate, query, create, modify, and organize files following directory structure rules
2. **Agent Coordination**: Delegate specialized tasks to appropriate sub-agents
3. **Knowledge Management**: Maintain consistency and integrity of the knowledge base
4. **Directory Rules**: Enforce rules defined in README.md and Rule.md files

## Available Sub-Agents

{self._format_agent_list()}

## Operation Principles

1. **Directory-First Approach**: Always understand directory structure and rules before operations
2. **Rule Inheritance**: Parent directory rules apply unless overridden by local rules  
3. **Consistency Maintenance**: Update README.md files after any structural changes
4. **Confirmation Required**: Ask for user confirmation before file write operations
5. **Agent Delegation**: Route specialized tasks to appropriate sub-agents

## Workflow

1. Analyze user request and identify task type
2. Use filesystem tools to understand current structure
3. Check relevant directory rules and permissions
4. Delegate to specialized agents if appropriate, or handle directly
5. Ensure all changes maintain knowledge base consistency
6. Update documentation as needed

Remember: You are the orchestrator ensuring the AkashicRecords file-based knowledge management principles are followed while leveraging specialized agents for optimal task execution."""

    def _format_agent_list(self) -> str:
        """Format the list of available agents for the prompt."""
        agent_descriptions = []
        for name, config in self.config.agents.items():
            if name != 'coordinator' and config.enabled:
                agent_descriptions.append(f"- **{name}**: {config.type}")
        
        return '\n'.join(agent_descriptions) if agent_descriptions else "- No specialized agents configured"