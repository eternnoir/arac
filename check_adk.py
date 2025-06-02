#!/usr/bin/env python3

import google.adk
import pkgutil

print('Available ADK submodules:')
for finder, name, ispkg in pkgutil.iter_modules(google.adk.__path__, google.adk.__name__ + '.'):
    print(f'  {name}')

# Check for MCP tools specifically
try:
    import google.adk.tools.mcp
    print('\nMCP tools available!')
    print(dir(google.adk.tools.mcp))
except ImportError as e:
    print(f'\nMCP tools not available: {e}')

# Check alternatives
try:
    from google.adk.tools import BaseTool, FunctionTool
    print('\nBasic tools available')
except ImportError as e:
    print(f'\nBasic tools not available: {e}')