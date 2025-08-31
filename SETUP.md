# Setup Instructions

This document provides step-by-step instructions for setting up and running the MCP Testing Repository.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AH289/Testing-MCP.git
cd Testing-MCP
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running Tests

### Quick Start

Run all tests with the test runner:

```bash
python scripts/run_tests.py --all
```

### Individual Test Categories

```bash
# Run only unit tests
python scripts/run_tests.py --unit

# Run only integration tests
python scripts/run_tests.py --integration

# Run example scripts
python scripts/run_tests.py --examples

# Run linting checks
python scripts/run_tests.py --lint
```

### Manual Test Execution

```bash
# Run specific test files
python -m pytest tests/test_mcp_server.py -v
python -m pytest tests/test_integration.py -v

# Run all tests
python -m pytest tests/ -v
```

## Running Examples

### Basic Client Example

```bash
python examples/basic_client.py
```

This example demonstrates:
- Server initialization
- Tool listing
- Basic tool calls (echo, list_files, read_file)

### Tool Validation Example

```bash
python examples/tool_validation.py
```

This example shows:
- Automated tool validation
- Schema compliance checking
- Tool execution testing

## MCP Server Usage

### Basic Server Setup

```python
from src.mcp_server import MCPServer

# Create server instance
server = MCPServer("my-test-server")

# Handle requests
request = {
    "method": "tools/list",
    "params": {}
}

response = await server.handle_request(request)
print(response)
```

### Available Tools

The server includes these built-in tools:

1. **echo** - Echo back a message
   ```json
   {
     "name": "echo",
     "arguments": {
       "message": "Hello, MCP!"
     }
   }
   ```

2. **read_file** - Read file contents
   ```json
   {
     "name": "read_file",
     "arguments": {
       "path": "README.md"
     }
   }
   ```

3. **list_files** - List directory contents
   ```json
   {
     "name": "list_files",
     "arguments": {
       "directory": "."
     }
   }
   ```

## Configuration

The server can be configured using `config/mcp_config.json`:

```json
{
  "server": {
    "name": "testing-mcp-server",
    "version": "0.1.0"
  },
  "tools": {
    "enabled": ["read_file", "list_files", "echo"]
  }
}
```

## Development

### Code Formatting

```bash
# Format code with Black
python -m black src tests examples

# Check formatting
python -m black --check src tests examples
```

### Linting

```bash
# Run flake8 linting
python -m flake8 src tests examples

# Run mypy type checking
python -m mypy src
```

### Adding New Tools

1. Add tool definition to `MCPServer._register_default_tools()`
2. Implement tool handler method
3. Add test cases in `tests/test_mcp_server.py`
4. Update documentation

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the repository root directory
   - Check that virtual environment is activated
   - Verify all dependencies are installed

2. **Test Failures**
   - Check Python version (3.8+ required)
   - Ensure all required packages are installed
   - Run tests with `-v` flag for detailed output

3. **Permission Errors**
   - On Windows, run terminal as administrator if needed
   - Check file permissions for test files

### Getting Help

- Check the [Issues](https://github.com/AH289/Testing-MCP/issues) page
- Review the [MCP Specification](https://spec.modelcontextprotocol.io/)
- Run tests with verbose output: `python scripts/run_tests.py --all --verbose`

## Next Steps

1. Explore the example scripts to understand MCP concepts
2. Run the validation suite on your own MCP tools
3. Contribute additional test cases or tools
4. Check out the [MCP documentation](https://modelcontextprotocol.io/) for advanced usage
