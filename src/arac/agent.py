"""
ADK Entry Point for AkashicRecords Agent Client

This module provides the root_agent that ADK expects to find.
"""

import os
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from .core.coordinator import AkashicCoordinator
from .core.config_loader import load_project_config
from .utils.project_discovery import discover_project_root


def create_root_agent():
    """
    Create the root agent for the AkashicRecords multi-agent system.
    
    This function is called by ADK to initialize the agent hierarchy.
    """
    try:
        # Discover project root from environment or current directory
        project_path = discover_project_root()
        print(f"🏗️  ARAC Project Path: {project_path}")
        
        # Load project configuration
        config = load_project_config(project_path)
        print(f"✅ Config loaded successfully")
        
        # Create the coordinator agent
        coordinator = AkashicCoordinator(config, project_path)
        print(f"DEBUG: Coordinator created successfully")
        
        return coordinator.create_agent_hierarchy()
        
    except Exception as e:
        # Show detailed error and fallback to basic agent
        print(f"ERROR: Failed to load project config: {e}")
        import traceback
        traceback.print_exc()
        print("Falling back to basic AkashicRecords agent")
        
        # Try to get fallback token limits from environment
        fallback_max_output = os.environ.get('ARAC_FALLBACK_MAX_OUTPUT_TOKENS')
        fallback_max_context = os.environ.get('ARAC_FALLBACK_MAX_CONTEXT_TOKENS')
        
        model_kwargs = {"model": "openai/gpt-4o"}
        if fallback_max_output:
            model_kwargs["max_tokens"] = int(fallback_max_output)
        if fallback_max_context:
            model_kwargs["max_completion_tokens"] = int(fallback_max_context)
            
        return Agent(
            name="akashic_records_fallback",
            model=LiteLlm(**model_kwargs),
            description="Basic AkashicRecords agent (fallback mode)",
            instruction="You are a basic file management assistant. Help users organize and manage their files and documents.",
            tools=[]
        )


# ADK expects to find a root_agent in this module
root_agent = create_root_agent()