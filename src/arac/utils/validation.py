"""
Configuration Validation Utilities

Validates AkashicRecords project configurations and setup.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from pydantic import ValidationError

from ..core.config_loader import ProjectConfig, AgentConfig


class ConfigValidator:
    """Validates AkashicRecords project configurations."""
    
    def __init__(self, project_root: str):
        """
        Initialize validator for a project.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.arclient_path = self.project_root / '.arclient'
    
    def validate_project(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate the entire project configuration.
        
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check if .arclient directory exists
        if not self.arclient_path.exists():
            errors.append("Missing .arclient configuration directory")
            return False, errors, warnings
        
        # Validate config.json
        config_valid, config_errors, config_warnings = self._validate_config()
        errors.extend(config_errors)
        warnings.extend(config_warnings)
        
        # Validate prompts directory
        prompt_warnings = self._validate_prompts()
        warnings.extend(prompt_warnings)
        
        # Validate directory structure
        structure_warnings = self._validate_directory_structure()
        warnings.extend(structure_warnings)
        
        # Validate environment
        env_warnings = self._validate_environment()
        warnings.extend(env_warnings)
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def _validate_config(self) -> Tuple[bool, List[str], List[str]]:
        """Validate config.json file."""
        errors = []
        warnings = []
        
        config_path = self.arclient_path / 'config.json'
        if not config_path.exists():
            errors.append("Missing config.json file")
            return False, errors, warnings
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in config.json: {e}")
            return False, errors, warnings
        except Exception as e:
            errors.append(f"Could not read config.json: {e}")
            return False, errors, warnings
        
        # Validate structure using Pydantic
        try:
            # Convert agents to AgentConfig objects for validation
            if 'agents' in config_data:
                agents = {}
                for name, agent_data in config_data['agents'].items():
                    agents[name] = AgentConfig(**agent_data)
                config_data['agents'] = agents
            
            config = ProjectConfig(**config_data)
            
            # Additional validation checks
            if 'coordinator' not in config.agents:
                warnings.append("No coordinator agent configured - system may not work properly")
            
            # Check for enabled agents
            enabled_agents = [name for name, agent in config.agents.items() if agent.enabled]
            if len(enabled_agents) == 0:
                errors.append("No agents are enabled")
            elif len(enabled_agents) == 1 and 'coordinator' in enabled_agents:
                warnings.append("Only coordinator agent enabled - limited functionality")
            
            # Validate model configurations
            for name, agent in config.agents.items():
                if agent.model and not self._is_valid_model_format(agent.model):
                    warnings.append(f"Agent '{name}' has unusual model format: {agent.model}")
            
        except ValidationError as e:
            errors.append(f"Configuration validation failed: {e}")
            return False, errors, warnings
        
        return True, errors, warnings
    
    def _validate_prompts(self) -> List[str]:
        """Validate prompt templates."""
        warnings = []
        
        prompts_path = self.arclient_path / 'prompts'
        if not prompts_path.exists():
            warnings.append("No prompts directory found - agents will use default prompts")
            return warnings
        
        # Check for standard prompt files
        standard_prompts = ['coordinator.md', 'base_agent.md', 'meeting_agent.md']
        for prompt_file in standard_prompts:
            prompt_path = prompts_path / prompt_file
            if not prompt_path.exists():
                warnings.append(f"Missing prompt template: {prompt_file}")
            elif prompt_path.stat().st_size == 0:
                warnings.append(f"Empty prompt template: {prompt_file}")
        
        return warnings
    
    def _validate_directory_structure(self) -> List[str]:
        """Validate expected directory structure."""
        warnings = []
        
        # Load config to check target directories
        try:
            config_path = self.arclient_path / 'config.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Check for meeting agent target directories
            agents = config_data.get('agents', {})
            meeting_agent = agents.get('meeting_agent', {})
            target_dirs = meeting_agent.get('target_directories', [])
            
            for target_dir in target_dirs:
                dir_path = self.project_root / target_dir
                if not dir_path.exists():
                    warnings.append(f"Target directory '{target_dir}' does not exist")
                elif not (dir_path / 'README.md').exists():
                    warnings.append(f"Target directory '{target_dir}' missing README.md")
        
        except Exception as e:
            warnings.append(f"Could not validate directory structure: {e}")
        
        return warnings
    
    def _validate_environment(self) -> List[str]:
        """Validate environment configuration."""
        warnings = []
        
        # Check for .env file
        env_path = self.project_root / '.env'
        if not env_path.exists():
            warnings.append("No .env file found - ensure API keys are configured")
        
        # Check for .env.example
        env_example_path = self.project_root / '.env.example'
        if not env_example_path.exists():
            warnings.append("No .env.example file found - consider providing example configuration")
        
        return warnings
    
    def _is_valid_model_format(self, model: str) -> bool:
        """Check if model string follows expected format."""
        # Valid formats: "openai/gpt-4", "gpt-4", "anthropic/claude-3-sonnet", etc.
        if '/' in model:
            provider, model_name = model.split('/', 1)
            return len(provider) > 0 and len(model_name) > 0
        else:
            # Direct model name
            return len(model) > 0
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive health report for the project.
        
        Returns:
            Dict[str, Any]: Health report with status and recommendations
        """
        is_valid, errors, warnings = self.validate_project()
        
        # Get configuration info
        config_info = {}
        try:
            from ..core.config_loader import load_project_config
            config = load_project_config(str(self.project_root))
            config_info = {
                "project_name": config.project.get('name', 'Unknown'),
                "project_type": config.project.get('type', 'Unknown'),
                "enabled_agents": [
                    name for name, agent in config.agents.items() 
                    if agent.enabled
                ],
                "mcp_filesystem_enabled": config.mcp_tools.filesystem.get('enabled', False)
            }
        except Exception as e:
            config_info = {"error": f"Could not load config: {e}"}
        
        # Generate recommendations
        recommendations = []
        if errors:
            recommendations.append("Fix configuration errors before running agents")
        if len(warnings) > 3:
            recommendations.append("Review warnings to improve configuration")
        if 'meeting_agent' in config_info.get('enabled_agents', []):
            recommendations.append("Ensure meeting target directories have README.md files")
        
        return {
            "status": "healthy" if is_valid else "needs_attention",
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "recommendations": recommendations,
            "configuration": config_info,
            "timestamp": Path(__file__).stat().st_mtime
        }


def validate_project(project_root: str) -> Tuple[bool, List[str], List[str]]:
    """
    Quick validation function for a project.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
    """
    validator = ConfigValidator(project_root)
    return validator.validate_project()