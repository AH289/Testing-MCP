#!/usr/bin/env python3
"""Basic MCP Client Example"""

import asyncio
import json
from src.mcp_server import MCPServer

async def run_client_example():
    """Demonstrate basic MCP client-server interaction."""
    print("=== MCP Client Example ===")
    
    # Create server instance
    server = MCPServer("example-server")
    
    # Initialize server
    print("\n1. Initializing server...")
    init_request = {
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "example-client",
                "version": "1.0.0"
            }
        }
    }
    
    init_response = await server.handle_request(init_request)
    print(f"Server initialized: {init_response['serverInfo']['name']}")
    
    # List available tools
    print("\n2. Listing available tools...")
    list_request = {
        "method": "tools/list",
        "params": {}
    }
    
    list_response = await server.handle_request(list_request)
    print("Available tools:")
    for tool in list_response["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test echo tool
    print("\n3. Testing echo tool...")
    echo_request = {
        "method": "tools/call",
        "params": {
            "name": "echo",
            "arguments": {
                "message": "Hello from MCP client!"
            }
        }
    }
    
    echo_response = await server.handle_request(echo_request)
    print(f"Echo response: {echo_response['content'][0]['text']}")
    
    # Test list_files tool
    print("\n4. Testing list_files tool...")
    list_files_request = {
        "method": "tools/call",
        "params": {
            "name": "list_files",
            "arguments": {
                "directory": "."
            }
        }
    }
    
    list_files_response = await server.handle_request(list_files_request)
    print("Files in current directory:")
    print(list_files_response['content'][0]['text'])
    
    # Test read_file tool with README
    print("\n5. Testing read_file tool...")
    read_file_request = {
        "method": "tools/call",
        "params": {
            "name": "read_file",
            "arguments": {
                "path": "README.md"
            }
        }
    }
    
    read_file_response = await server.handle_request(read_file_request)
    content = read_file_response['content'][0]['text']
    if "Error" not in content:
        print(f"README.md content (first 100 chars): {content[:100]}...")
    else:
        print(f"Read file result: {content}")
    
    print("\n=== Example completed successfully! ===")

if __name__ == "__main__":
    asyncio.run(run_client_example())
