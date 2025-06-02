"""
Configuration Loader for AkashicRecords Projects

Loads and validates .arclient configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    type: str
    enabled: bool = True
    model: str = "openai/gpt-4o"
    prompt_template: Optional[str] = None
    tools: List[str] = ["mcp_filesystem"]
    permissions: List[str] = ["read"]
    target_directories: List[str] = []
    custom_config: Dict[str, Any] = {}


class MCPConfig(BaseModel):
    """Configuration for MCP tools."""
    filesystem: Dict[str, Any] = {
        "enabled": True
    }


class WorkflowConfig(BaseModel):
    """Configuration for agent workflow."""
    default_agent: str = "coordinator"
    delegation_strategy: str = "llm_driven"
    enable_parallel_execution: bool = True


class ProjectConfig(BaseModel):
    """Complete project configuration."""
    project: Dict[str, str]
    agents: Dict[str, AgentConfig]
    mcp_tools: MCPConfig = MCPConfig()
    workflow: WorkflowConfig = WorkflowConfig()
    
    @property
    def default_model(self) -> str:
        """Get the default model from coordinator agent or fallback."""
        coordinator = self.agents.get('coordinator')
        if coordinator:
            return coordinator.model
        return "openai/gpt-4o"


def load_project_config(project_root: str) -> ProjectConfig:
    """
    Load project configuration from .arclient directory.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        ProjectConfig: Validated project configuration
        
    Raises:
        FileNotFoundError: If configuration files are missing
        ValidationError: If configuration is invalid
    """
    arclient_path = Path(project_root) / '.arclient'
    config_path = arclient_path / 'config.json'
    
    if not config_path.exists():
        # Create default configuration
        default_config = create_default_config(project_root)
        return default_config
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Convert agents dict to AgentConfig objects
        if 'agents' in config_data:
            agents = {}
            for name, agent_data in config_data['agents'].items():
                agents[name] = AgentConfig(**agent_data)
            config_data['agents'] = agents
        
        # Convert nested configs
        if 'mcp_tools' in config_data:
            config_data['mcp_tools'] = MCPConfig(**config_data['mcp_tools'])
        
        if 'workflow' in config_data:
            config_data['workflow'] = WorkflowConfig(**config_data['workflow'])
        
        return ProjectConfig(**config_data)
        
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Invalid configuration format: {e}")


def create_default_config(project_root: str) -> ProjectConfig:
    """
    Create a default configuration for a project.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        ProjectConfig: Default configuration
    """
    project_name = Path(project_root).name
    
    return ProjectConfig(
        project={
            "name": project_name,
            "type": "general"
        },
        agents={
            "coordinator": AgentConfig(
                type="akashic_coordinator",
                enabled=True,
                model="openai/gpt-4o",
                prompt_template="prompts/coordinator.md",
                tools=["mcp_filesystem"],
                permissions=["read", "write", "create"]
            ),
            "base_agent": AgentConfig(
                type="akashic_base",
                enabled=True,
                model="openai/gpt-4o", 
                prompt_template="prompts/base_agent.md",
                tools=["mcp_filesystem"],
                permissions=["read", "write", "create"]
            )
        }
    )


def save_config(config: ProjectConfig, project_root: str) -> None:
    """
    Save project configuration to .arclient directory.
    
    Args:
        config: Project configuration to save
        project_root: Root directory of the project
    """
    arclient_path = Path(project_root) / '.arclient'
    arclient_path.mkdir(exist_ok=True)
    
    config_path = arclient_path / 'config.json'
    
    # Convert to serializable dict
    config_dict = config.model_dump()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)