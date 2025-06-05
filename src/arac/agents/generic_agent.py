"""
Generic Agent Implementation

Simple configuration-driven agent that can be specialized through prompts and tools.
"""

from typing import List, Optional
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from pathlib import Path


def create_agent(
    name: str,
    model: str,
    project_root: str,
    prompt_template: Optional[str] = None,
    tools: Optional[List] = None,
    description: Optional[str] = None,
    max_output_tokens: Optional[int] = None,
    max_context_tokens: Optional[int] = None,
    **kwargs
) -> Agent:
    """
    Create a generic agent based on configuration.
    
    Args:
        name: Name of the agent
        model: Model to use for the agent
        project_root: Root directory of the project
        prompt_template: Path to prompt template file
        tools: List of tools to provide to the agent
        description: Agent description
        **kwargs: Additional configuration parameters
        
    Returns:
        Agent: Configured agent
    """
    # Load prompt template or use default
    prompt_content = _load_prompt_template(project_root, prompt_template)
    if not prompt_content:
        prompt_content = f"You are {name}, an AI assistant specialized for this project at {project_root}."
    
    # Use provided description or generate one
    agent_description = description or f"AI assistant: {name}"
    
    # Build model kwargs
    model_kwargs = {"model": model}
    if max_output_tokens:
        model_kwargs["max_completion_tokens"] = max_output_tokens
    if max_context_tokens:
        model_kwargs["max_tokens"] = max_context_tokens
    
    return Agent(
        name=name,
        model=LiteLlm(**model_kwargs),
        description=agent_description,
        instruction=prompt_content,
        tools=tools or []
    )


def _load_prompt_template(project_root: str, template_path: Optional[str]) -> Optional[str]:
    """
    Load prompt template from file.
    
    Args:
        project_root: Root directory of the project
        template_path: Path to the prompt template file
        
    Returns:
        Optional[str]: Prompt content or None if not found
    """
    if not template_path:
        return None
    
    try:
        # Try relative to .arclient first
        arclient_path = Path(project_root) / '.arclient' / template_path
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