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
    
    def __init__(self, config: ProjectConfig, project_root: str = '.'):
        """
        Initialize the coordinator with project configuration.
        
        Args:
            config: Project configuration loaded from .arclient
            project_root: Project root path (from environment or discovery)
        """
        self.config = config
        self.project_root = project_root
        self.factory = AgentFactory(config, project_root)
        
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
        
        # Create specialized sub-agents
        sub_agents = self._create_sub_agents()
        
        # Create the coordinator agent (no filesystem tools - pure orchestration)
        model_kwargs = {"model": coordinator_config.model}
        if coordinator_config.max_output_tokens:
            model_kwargs["max_completion_tokens"] = coordinator_config.max_output_tokens
        if coordinator_config.max_context_tokens:
            model_kwargs["max_tokens"] = coordinator_config.max_context_tokens
            
        coordinator = Agent(
            name="akashic_coordinator",
            model=LiteLlm(**model_kwargs),
            description="AkashicRecords coordinator agent for task delegation and orchestration",
            instruction=prompt_content,
            tools=[],  # No direct tools - pure delegation
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

1. **Task Analysis**: Analyze user requests to determine the most appropriate agent
2. **Agent Delegation**: Route ALL tasks to appropriate specialized sub-agents
3. **Orchestration Only**: You should NOT perform file operations directly - always delegate
4. **Progress Coordination**: Monitor and report on delegated task progress

## Available Sub-Agents

{self._format_agent_list()}

## Delegation Strategy

**IMPORTANT**: You should delegate ALL tasks to sub-agents. Your role is purely coordination and orchestration.

- **General file operations**: Delegate to base_agent
- **Meeting-related tasks**: Delegate to meeting_agent  
- **Custom tasks**: Delegate to the most appropriate specialized agent
- **Complex multi-step tasks**: Break down and delegate to multiple agents as needed

## Operation Principles

1. **Delegation First**: NEVER perform file operations yourself - always delegate to sub-agents
2. **Clear Instructions**: Provide clear, specific instructions to sub-agents
3. **Task Decomposition**: Break complex tasks into smaller parts for appropriate agents
4. **Progress Monitoring**: Track and report on delegated task status
5. **User Communication**: Keep users informed about which agent is handling their request

## Workflow

1. **Analyze**: Understand what the user wants to accomplish
2. **Identify Agent**: Determine which sub-agent is best suited for the task
3. **Delegate**: Pass the task to the appropriate agent with clear instructions
4. **Monitor**: Track progress and handle any coordination needs
5. **Report**: Communicate results and status back to the user

## What You Should NOT Do

- Do not read, write, create, or modify files directly
- Do not perform directory operations yourself
- Do not handle specialized tasks that sub-agents are designed for
- Do not bypass the delegation system

Remember: You are a pure orchestrator. Your job is to understand user needs and route tasks to the right agents, not to perform the work yourself."""

    def _format_agent_list(self) -> str:
        """Format the list of available agents for the prompt."""
        agent_descriptions = []
        for name, config in self.config.agents.items():
            if name != 'coordinator' and config.enabled:
                agent_descriptions.append(f"- **{name}**: {config.type}")
        
        return '\n'.join(agent_descriptions) if agent_descriptions else "- No specialized agents configured"