# AkashicRecords Agent Client (arac)

A multi-agent system for file-based knowledge management using Google ADK and the AkashicRecords methodology.

## Overview

The AkashicRecords Agent Client (arac) is a sophisticated multi-agent orchestration system that brings the AkashicRecords file-based knowledge management approach to Google's Agent Development Kit (ADK). It allows projects to define custom agent configurations through `.arclient` directories, enabling tailored AI assistance for different types of knowledge work.

## Key Features

- **Multi-Agent Architecture**: Coordinated agents with specialized capabilities
- **AkashicRecords Integration**: Built-in understanding of directory rules and file organization
- **Flexible Configuration**: Project-specific agent combinations via `.arclient` folders
- **MCP Filesystem Support**: Native file system operations through Model Context Protocol
- **Multi-Model Support**: OpenAI GPT-4o, Claude, Gemini, and other LLM providers
- **Template-Based Setup**: Quick start with predefined agent configurations

## Quick Start

### 1. Installation

```bash
# Clone and set up the project
git clone <repository-url>
cd arac

# Install with uv (Python package manager)
uv sync
```

### 2. Copy Example Configuration

```bash
# Copy the basic project example to your working directory
cp -r examples/basic_project/* /path/to/your/project/
cd /path/to/your/project/

# Configure your API keys
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 3. Run with ADK

```bash
# Set environment variable for project path
export ARAC_PROJECT_PATH=/path/to/your/project

# Run with ADK CLI
adk run /path/to/arac/src/arac

# Or use the web interface
cd /path/to/arac/src
adk web
```

## Project Structure

### Your Project Layout
```
your_project/
   .arclient/                 # AkashicRecords agent configuration
      config.json           # Main agent configuration
      prompts/              # Agent prompt templates
          coordinator.md    # Coordinator agent prompt
          base_agent.md     # Base agent prompt
          meeting_agent.md  # Meeting agent prompt
   Meetings/                 # Meeting documentation
   Documents/                # General documents
   Projects/                 # Project-specific files
   .env                      # Environment configuration
   README.md                # Project documentation
```

### arac System Layout
```
arac/
   src/arac/
      agent.py             # ADK entry point (root_agent)
      core/                # Core system components
         coordinator.py   # Main coordinator agent
         agent_factory.py # Agent creation factory
         config_loader.py # Configuration management
      agents/              # Agent implementations
         generic_agent.py # Generic configurable agent
      integrations/        # External integrations
         mcp_filesystem.py # MCP filesystem tools
         multi_model.py   # Multi-model support
      utils/               # Utilities
          project_discovery.py # Project auto-discovery
          validation.py    # Configuration validation
   examples/                # Example configurations
       basic_project/       # Basic setup example
```

## Configuration

### `.arclient/config.json`

The main configuration file defines your agent setup:

```json
{
  "project": {
    "name": "Your Project Name",
    "type": "knowledge-management",
    "root_path": "."
  },
  "agents": {
    "coordinator": {
      "type": "akashic_coordinator",
      "enabled": true,
      "model": "openai/gpt-4o",
      "prompt_template": "prompts/coordinator.md",
      "permissions": ["read", "write", "create", "delete"]
    },
    "base_agent": {
      "type": "akashic_base",
      "enabled": true,
      "model": "openai/gpt-4o",
      "prompt_template": "prompts/base_agent.md",
      "permissions": ["read", "write", "create"]
    },
    "meeting_agent": {
      "type": "meeting_minutes",
      "enabled": true,
      "model": "openai/gpt-4o",
      "prompt_template": "prompts/meeting_agent.md",
      "permissions": ["read", "write", "create"],
      "target_directories": ["Meetings", "會議記錄"]
    }
  },
  "mcp_tools": {
    "filesystem": {
      "enabled": true,
      "root_path": ".",
      "tools": ["read_file", "write_file", "list_directory", "create_directory", "search_files", "get_file_info", "move_file"]
    }
  },
  "workflow": {
    "default_agent": "coordinator",
    "delegation_strategy": "llm_driven",
    "enable_parallel_execution": true,
    "confirmation_required": true
  }
}
```

### Environment Variables

Configure `.env` in your project root:

```bash
# OpenAI Configuration (required)
OPENAI_API_KEY=your_openai_api_key_here

# Project Configuration
ARAC_PROJECT_PATH=.

# Optional: Other model providers
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Debug settings
ARAC_DEBUG=false
ARAC_LOG_LEVEL=INFO
```

## Available Agents

### Coordinator Agent
- **Purpose**: Main orchestrator and user interface
- **Capabilities**: Task delegation, multi-agent coordination, user interaction
- **Model**: Typically GPT-4o for complex reasoning

### Generic Agent
- **Purpose**: Flexible agent implementation specialized through prompts
- **Capabilities**: Any task based on prompt configuration and tool assignment
- **Model**: Configurable per instance (GPT-4o, Claude, Gemini, etc.)

## Usage Examples

### General File Management
```
User: "Help me organize the documents in my project according to AkashicRecords principles"

System: The coordinator will:
1. Analyze current directory structure
2. Delegate to specialized agent for file organization
3. Update README.md files as needed
4. Report changes and improvements
```

### Meeting Processing
```
User: "Please process this meeting transcript and create meeting minutes"

System: The meeting_agent will:
1. Read existing meeting context from README.md
2. Review previous meeting minutes for continuity
3. Analyze the transcript for key points and decisions
4. Create structured meeting minutes
5. Update meeting documentation
```

### Knowledge Base Queries
```
User: "Find all documents related to project planning"

System: The system will:
1. Use MCP filesystem tools to search across directories
2. Respect directory rules and organization
3. Provide structured results with context
4. Suggest related documents and cross-references
```

## AkashicRecords Principles

The system follows core AkashicRecords methodology:

1. **Directory-First Organization**: Structure drives functionality
2. **Rule Inheritance**: Parent directory rules cascade to children
3. **Documentation Consistency**: README.md files maintain current state
4. **Cross-Reference Integrity**: Links between documents are preserved
5. **Confirmation-Based Operations**: User consent for structural changes

## Customization

### Adding Custom Agents

1. **Configure Agent**: Add to your project's `config.json`
2. **Create Prompt**: Create prompt template in `.arclient/prompts/`
3. **Assign Tools**: Configure tools and permissions
4. **Test**: Validate with the configuration test script

### Custom Models

Support for additional models via LiteLLM:

```json
{
  "agents": {
    "custom_agent": {
      "type": "custom",
      "model": "anthropic/claude-3-sonnet",
      "prompt_template": "prompts/custom.md"
    }
  }
}
```

### Custom MCP Tools

Extend filesystem capabilities with custom MCP servers:

```json
{
  "mcp_tools": {
    "custom_tools": {
      "enabled": true,
      "server_command": "python",
      "server_args": ["custom_mcp_server.py"]
    }
  }
}
```

## Testing and Validation

### Configuration Test
```bash
cd arac
uv run python test_config.py
```

### Project Validation
```bash
cd your_project
python -c "
from arac.utils.validation import validate_project
is_valid, errors, warnings = validate_project('.')
print(f'Valid: {is_valid}')
print(f'Errors: {errors}')
print(f'Warnings: {warnings}')
"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the arac directory when running
2. **MCP Connection Failures**: Check that Node.js and npx are available
3. **Model API Errors**: Verify API keys in `.env` file
4. **Path Issues**: Use absolute paths for ARAC_PROJECT_PATH

### Debug Mode

Enable debug logging:
```bash
export ARAC_DEBUG=true
export ARAC_LOG_LEVEL=DEBUG
```

## Development

### Project Structure for Contributors

- `src/arac/core/`: Core system components
- `src/arac/agents/`: Agent implementations  
- `src/arac/integrations/`: External system integrations
- `src/arac/utils/`: Utility functions
- `examples/`: Example configurations
- `test_config.py`: Configuration testing script

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

[License information]

## Support

For issues and questions:
- Create GitHub issues for bugs
- Check documentation for configuration help
- Review examples for implementation patterns

---

*Built with Google ADK and following AkashicRecords methodology for file-based knowledge management.*