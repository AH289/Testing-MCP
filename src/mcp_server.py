#!/usr/bin/env python3
"""Basic MCP Server Implementation for Testing"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """Basic MCP Server for testing file operations and tool validation."""
    
    def __init__(self, name: str = "test-mcp-server"):
        self.name = name
        self.tools = {}
        self.resources = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools for testing."""
        self.tools = {
            "read_file": {
                "name": "read_file",
                "description": "Read contents of a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            "list_files": {
                "name": "list_files",
                "description": "List files in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to list",
                            "default": "."
                        }
                    }
                }
            },
            "echo": {
                "name": "echo",
                "description": "Echo back the input message",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "tools/list":
                return {
                    "tools": list(self.tools.values())
                }
            elif method == "tools/call":
                return await self._call_tool(params)
            elif method == "initialize":
                return await self._initialize(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": self.name,
                "version": "0.1.0"
            }
        }
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Tool not found: {tool_name}"
                }
            }
        
        if tool_name == "read_file":
            return await self._read_file(arguments)
        elif tool_name == "list_files":
            return await self._list_files(arguments)
        elif tool_name == "echo":
            return await self._echo(arguments)
        
        return {
            "error": {
                "code": -32603,
                "message": f"Tool implementation not found: {tool_name}"
            }
        }
    
    async def _read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents."""
        try:
            file_path = Path(args["path"])
            if not file_path.exists():
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error: File not found: {file_path}"
                    }]
                }
            
            content = file_path.read_text(encoding='utf-8')
            return {
                "content": [{
                    "type": "text",
                    "text": content
                }]
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error reading file: {str(e)}"
                }]
            }
    
    async def _list_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List files in directory."""
        try:
            directory = Path(args.get("directory", "."))
            if not directory.exists():
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error: Directory not found: {directory}"
                    }]
                }
            
            files = []
            for item in directory.iterdir():
                files.append(f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}")
            
            return {
                "content": [{
                    "type": "text",
                    "text": "\n".join(sorted(files))
                }]
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error listing directory: {str(e)}"
                }]
            }
    
    async def _echo(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Echo back the message."""
        message = args.get("message", "")
        return {
            "content": [{
                "type": "text",
                "text": f"Echo: {message}"
            }]
        }

if __name__ == "__main__":
    server = MCPServer()
    print("MCP Test Server initialized successfully!")
    print(f"Available tools: {list(server.tools.keys())}")
