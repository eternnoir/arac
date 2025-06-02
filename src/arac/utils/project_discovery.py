"""
Project Discovery Utilities

Automatically discover the project root and .arclient configuration.
"""

import os
from pathlib import Path
from typing import Optional


def discover_project_root() -> str:
    """
    Discover the project root directory.
    
    Priority:
    1. ARAC_PROJECT_PATH environment variable
    2. Walk up from current directory looking for .arclient folder
    3. Current working directory as fallback
    
    Returns:
        str: Path to the project root directory
    """
    # Check environment variable first
    env_path = os.getenv('ARAC_PROJECT_PATH')
    if env_path and Path(env_path).exists():
        return env_path
    
    # Walk up from current directory
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        arclient_path = parent / '.arclient'
        if arclient_path.exists() and arclient_path.is_dir():
            return str(parent)
    
    # Fallback to current directory
    return str(Path.cwd())


def find_arclient_config(project_root: str) -> Optional[str]:
    """
    Find the .arclient configuration directory.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        Optional[str]: Path to .arclient directory if found
    """
    arclient_path = Path(project_root) / '.arclient'
    if arclient_path.exists() and arclient_path.is_dir():
        return str(arclient_path)
    return None


def validate_project_structure(project_root: str) -> bool:
    """
    Validate that the project has the expected structure.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        bool: True if structure is valid
    """
    arclient_path = find_arclient_config(project_root)
    if not arclient_path:
        return False
    
    # Check for required configuration files
    config_file = Path(arclient_path) / 'config.json'
    return config_file.exists()