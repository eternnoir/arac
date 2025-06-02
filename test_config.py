#!/usr/bin/env python3
"""
Test script for AkashicRecords Agent Client configuration loading.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from arac.utils.project_discovery import discover_project_root, find_arclient_config
from arac.core.config_loader import load_project_config
from arac.utils.validation import validate_project


def test_project_discovery():
    """Test project discovery functionality."""
    print("=== Testing Project Discovery ===")
    
    # Test with example project
    example_project = Path(__file__).parent / 'examples' / 'basic_project'
    os.chdir(example_project)
    
    try:
        project_root = discover_project_root()
        print(f"✓ Discovered project root: {project_root}")
        
        arclient_config = find_arclient_config(project_root)
        print(f"✓ Found .arclient config: {arclient_config}")
        
        return project_root
    except Exception as e:
        print(f"✗ Project discovery failed: {e}")
        return None


def test_config_loading(project_root):
    """Test configuration loading."""
    print("\n=== Testing Configuration Loading ===")
    
    try:
        config = load_project_config(project_root)
        print(f"✓ Loaded project config for: {config.project.get('name')}")
        print(f"✓ Found {len(config.agents)} agents configured")
        
        enabled_agents = [name for name, agent in config.agents.items() if agent.enabled]
        print(f"✓ Enabled agents: {', '.join(enabled_agents)}")
        
        return config
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        return None


def test_validation(project_root):
    """Test project validation."""
    print("\n=== Testing Project Validation ===")
    
    try:
        is_valid, errors, warnings = validate_project(project_root)
        
        print(f"✓ Validation completed")
        print(f"  Valid: {is_valid}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        
        if errors:
            print("  Error details:")
            for error in errors:
                print(f"    - {error}")
        
        if warnings:
            print("  Warning details:")
            for warning in warnings:
                print(f"    - {warning}")
        
        return is_valid
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False


def test_agent_creation(config):
    """Test agent creation (without ADK)."""
    print("\n=== Testing Agent Creation ===")
    
    try:
        from arac.core.coordinator import AkashicCoordinator
        
        coordinator = AkashicCoordinator(config)
        print("✓ Created AkashicCoordinator")
        
        # Test prompt loading
        coordinator_config = config.agents.get('coordinator')
        if coordinator_config:
            prompt = coordinator._load_prompt_template(coordinator_config.prompt_template)
            print(f"✓ Loaded coordinator prompt ({len(prompt)} characters)")
        
        return True
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("AkashicRecords Agent Client - Configuration Test")
    print("=" * 50)
    
    # Test project discovery
    project_root = test_project_discovery()
    if not project_root:
        return 1
    
    # Test config loading
    config = test_config_loading(project_root)
    if not config:
        return 1
    
    # Test validation
    is_valid = test_validation(project_root)
    
    # Test agent creation
    agent_created = test_agent_creation(config)
    
    # Summary
    print("\n=== Test Summary ===")
    if project_root and config and agent_created:
        print("✓ All core functionality tests passed")
        if is_valid:
            print("✓ Project configuration is valid")
        else:
            print("⚠ Project configuration has warnings (but is functional)")
        print("\nReady for ADK integration testing!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())