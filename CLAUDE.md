# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Setup
```bash
# Install dependencies with UV package manager
uv sync

# Install with development dependencies
uv sync --dev
```

### Testing and Validation
```bash
# Test configuration loading and validation
uv run python test_config.py

# Validate a specific project
python -c "
from src.arac.utils.validation import validate_project
is_valid, errors, warnings = validate_project('/path/to/project')
print(f'Valid: {is_valid}, Errors: {errors}, Warnings: {warnings}')
"
```

### Code Quality
```bash
# Format code with black
uv run black src/

# Sort imports with isort
uv run isort src/

# Type checking with mypy
uv run mypy src/

# Run tests
uv run pytest
```

### Running with Google ADK
```bash
# Set project path environment variable
export ARAC_PROJECT_PATH=/path/to/your/project

# Run with ADK CLI
adk run /path/to/arac/src/arac

# Run with ADK web interface
cd /path/to/arac/src
adk web
```

## Architecture Overview

### Core System Design
ARAC (AkashicRecords Agent Client) is a multi-agent orchestration system built on Google's Agent Development Kit (ADK). The system implements a hierarchical agent architecture where a coordinator agent manages specialized sub-agents for different types of knowledge management tasks.

### Key Components

#### Entry Point (`src/arac/agent.py`)
- Contains `root_agent` that ADK expects to find
- `create_root_agent()` function initializes the entire agent hierarchy
- Handles fallback to basic agent if configuration fails
- Uses project discovery to locate `.arclient` configuration

#### Coordinator System (`src/arac/core/coordinator.py`)
- `AkashicCoordinator` class orchestrates the multi-agent system
- Implements AkashicRecords file-based knowledge management principles
- Creates agent hierarchy with specialized sub-agents
- Loads prompt templates from `.arclient/prompts/` directory
- Integrates MCP (Model Context Protocol) filesystem tools

#### Agent Factory (`src/arac/core/agent_factory.py`)
- Factory pattern for creating specialized agents based on configuration
- Uses generic agent implementation with prompt-driven specialization
- Supports flexible agent types through configuration
- Handles prompt template loading and tool assignment from `.arclient/prompts/`

#### Configuration System (`src/arac/core/config_loader.py`)
Projects use `.arclient/config.json` for agent configuration:
- Defines enabled agents and their models
- Specifies prompt templates and permissions
- Configures MCP tools and workflow settings
- Supports multi-model configurations (OpenAI, Anthropic, Google)

### Agent Types and Responsibilities

#### Coordinator Agent
- Main orchestrator and user interface
- Delegates tasks to specialized agents
- Maintains knowledge base consistency
- Enforces directory rules and AkashicRecords principles

#### Generic Agent (`src/arac/agents/generic_agent.py`)
- Unified agent implementation driven by configuration and prompts
- Specialization through prompt templates in `.arclient/prompts/`
- Supports any agent type with appropriate tools and instructions
- Flexible architecture allowing custom agent behaviors

### Integration Layer (`src/arac/integrations/`)

#### MCP Filesystem (`mcp_filesystem.py`)
- Provides file system operations through Model Context Protocol
- Tools: read_file, write_file, list_directory, create_directory, search_files, get_file_info, move_file
- Root path restrictions for security

#### Multi-Model Support (`multi_model.py`)
- LiteLLM integration for multiple model providers
- Supports OpenAI GPT-4o, Claude, Gemini
- Configurable model routing per agent


### Project Discovery (`src/arac/utils/project_discovery.py`)
- Automatic detection of project root via `ARAC_PROJECT_PATH` or `.arclient` directories
- Searches up directory tree to find configuration
- Handles multiple project types and structures

### AkashicRecords Principles Integration
The system enforces these core principles:
1. **Directory-First Organization**: Structure drives functionality
2. **Rule Inheritance**: Parent directory rules cascade to children
3. **Documentation Consistency**: README.md files maintain current state
4. **Cross-Reference Integrity**: Links between documents are preserved
5. **Confirmation-Based Operations**: User consent for structural changes

### Development Workflow
1. Agents are created through the factory pattern based on `.arclient/config.json`
2. Generic agents are specialized using prompt templates from `.arclient/prompts/`
3. MCP tools provide secure filesystem access within project boundaries
4. Agents handle domain-specific tasks based on their prompt configuration
5. All operations maintain AkashicRecords methodology compliance

### Error Handling and Fallbacks
- Configuration loading failures fall back to basic agent mode
- Missing prompt templates use default prompts
- Agent creation failures are logged but don't crash the system
- Project validation provides detailed error reporting

### Testing Strategy
Use `test_config.py` to validate:
- Project discovery functionality
- Configuration loading and parsing
- Agent creation without ADK dependencies
- Project structure validation
- Prompt template loading