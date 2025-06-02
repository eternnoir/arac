# AkashicRecords Basic Project Example

This is an example project demonstrating how to use AkashicRecords Agent Client (arac) for file-based knowledge management.

## Project Structure

```
basic_project/
├── .arclient/                 # AkashicRecords agent configuration
│   ├── config.json           # Main agent configuration
│   └── prompts/              # Agent prompt templates
│       ├── coordinator.md    # Coordinator agent prompt
│       ├── base_agent.md     # Base agent prompt
│       └── meeting_agent.md  # Meeting agent prompt
├── Meetings/                 # Meeting documentation
├── Documents/                # General documents
├── Projects/                 # Project-specific files
└── README.md                # This file
```

## Configured Agents

### Coordinator Agent
- **Model**: OpenAI GPT-4.1 Preview
- **Role**: Main orchestrator and user interface
- **Capabilities**: Task delegation, overall coordination

### Base Agent  
- **Model**: OpenAI GPT-4.1 Preview
- **Role**: Core file operations and knowledge management
- **Capabilities**: File CRUD, directory management, README maintenance

### Meeting Agent
- **Model**: OpenAI GPT-4.1 Preview  
- **Role**: Meeting transcript processing and documentation
- **Capabilities**: Meeting minutes creation, meeting organization

## Getting Started

1. **Copy this example** to your project root
2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
3. **Run with ADK**:
   ```bash
   adk run basic_project
   ```

## Configuration

Edit `.arclient/config.json` to customize:
- Agent models and configurations
- Target directories for different agents
- MCP filesystem tool settings
- Workflow behavior

## Usage Examples

### General File Management
Ask the coordinator to help organize your files:
> "Help me organize the documents in my project"

### Meeting Processing
Provide a meeting transcript:
> "Please process this meeting transcript and create meeting minutes"

### Knowledge Base Queries
Search across your knowledge base:
> "Find all documents related to project planning"

## Directory Rules

This project follows AkashicRecords principles:
- Each directory should have a README.md explaining its purpose
- File operations respect directory-specific rules
- Cross-references between documents are maintained
- Structural changes update relevant documentation

## Customization

To extend this configuration:
1. Add new agents to `config.json`
2. Create custom prompt templates in `prompts/`
3. Modify MCP tool configurations
4. Adjust workflow settings

For more details, see the [arac documentation](../../README.md).