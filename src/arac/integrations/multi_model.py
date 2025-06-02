"""
Multi-Model Support for AkashicRecords Agents

Provides configuration and management for different language models.
"""

from typing import Dict, Any, Optional
from litellm import Router


class ModelManager:
    """
    Manages different language models for AkashicRecords agents.
    
    Supports OpenAI, Anthropic, Google, and other model providers through LiteLLM.
    """
    
    def __init__(self, model_configs: Optional[Dict[str, Any]] = None):
        """
        Initialize the model manager with configurations.
        
        Args:
            model_configs: Dictionary of model configurations
        """
        self.model_configs = model_configs or self._get_default_configs()
        self.router = None
        
    def _get_default_configs(self) -> Dict[str, Any]:
        """
        Get default model configurations with GPT-4.1 as primary.
        
        Returns:
            Dict[str, Any]: Default model configurations
        """
        return {
            "models": [
                {
                    "model_name": "gpt-4o",
                    "litellm_params": {
                        "model": "openai/gpt-4o",
                        "api_key": "os.environ/OPENAI_API_KEY"
                    }
                },
                {
                    "model_name": "gpt-4o",
                    "litellm_params": {
                        "model": "openai/gpt-4o",
                        "api_key": "os.environ/OPENAI_API_KEY"
                    }
                },
                {
                    "model_name": "claude-3-sonnet",
                    "litellm_params": {
                        "model": "anthropic/claude-3-sonnet-20240229",
                        "api_key": "os.environ/ANTHROPIC_API_KEY"
                    }
                },
                {
                    "model_name": "claude-3-haiku",
                    "litellm_params": {
                        "model": "anthropic/claude-3-haiku-20240307",
                        "api_key": "os.environ/ANTHROPIC_API_KEY"
                    }
                },
                {
                    "model_name": "gemini-2.0-flash",
                    "litellm_params": {
                        "model": "gemini/gemini-2.0-flash-exp",
                        "api_key": "os.environ/GOOGLE_API_KEY"
                    }
                }
            ],
            "routing_strategy": "least-busy",
            "fallbacks": [
                {
                    "gpt-4o": ["claude-3-sonnet"]
                },
                {
                    "claude-3-sonnet": ["gpt-4o"]
                }
            ]
        }
    
    def get_router(self) -> Router:
        """
        Get or create a LiteLLM router for model management.
        
        Returns:
            Router: Configured LiteLLM router
        """
        if self.router is None:
            self.router = Router(
                model_list=self.model_configs["models"],
                routing_strategy=self.model_configs.get("routing_strategy", "least-busy"),
                fallbacks=self.model_configs.get("fallbacks", [])
            )
        return self.router
    
    def get_model_for_agent(self, agent_type: str, model_preference: Optional[str] = None) -> str:
        """
        Get the appropriate model for a specific agent type.
        
        Args:
            agent_type: Type of agent requesting model
            model_preference: Preferred model if specified
            
        Returns:
            str: Model identifier to use
        """
        # Use preference if provided and available
        if model_preference and self._is_model_available(model_preference):
            return model_preference
        
        # Default model mappings based on agent type
        agent_model_mapping = {
            "akashic_coordinator": "openai/gpt-4o",
            "akashic_base": "openai/gpt-4o", 
            "meeting_minutes": "openai/gpt-4o",
            "template_manager": "openai/gpt-4o",
            "custom": "openai/gpt-4o"
        }
        
        return agent_model_mapping.get(agent_type, "openai/gpt-4o")
    
    def _is_model_available(self, model_name: str) -> bool:
        """
        Check if a model is available in the configuration.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            bool: True if model is available
        """
        available_models = [
            model["model_name"] for model in self.model_configs["models"]
        ]
        return model_name in available_models
    
    def add_model(self, model_config: Dict[str, Any]) -> None:
        """
        Add a new model configuration.
        
        Args:
            model_config: Model configuration dictionary
        """
        self.model_configs["models"].append(model_config)
        # Reset router to pick up new configuration
        self.router = None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about available models.
        
        Returns:
            Dict[str, Any]: Information about configured models
        """
        return {
            "available_models": [
                {
                    "name": model["model_name"],
                    "provider": model["litellm_params"]["model"].split("/")[0],
                    "model_id": model["litellm_params"]["model"]
                }
                for model in self.model_configs["models"]
            ],
            "default_model": "openai/gpt-4o",
            "routing_strategy": self.model_configs.get("routing_strategy", "least-busy")
        }


def create_model_manager(model_configs: Optional[Dict[str, Any]] = None) -> ModelManager:
    """
    Create a model manager instance.
    
    Args:
        model_configs: Optional model configurations
        
    Returns:
        ModelManager: Configured model manager
    """
    return ModelManager(model_configs)