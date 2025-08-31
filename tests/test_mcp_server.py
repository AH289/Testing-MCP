#!/usr/bin/env python3
"""Unit tests for MCP Server implementation"""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path
from src.mcp_server import MCPServer

class TestMCPServer:
    """Test cases for MCP Server functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = MCPServer("test-server")
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test server initialization."""
        request = {
            "method": "initialize",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        assert "protocolVersion" in response
        assert "capabilities" in response
        assert "serverInfo" in response
        assert response["serverInfo"]["name"] == "test-server"
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test tools listing."""
        request = {
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        assert "tools" in response
        assert len(response["tools"]) > 0
        
        tool_names = [tool["name"] for tool in response["tools"]]
        assert "read_file" in tool_names
        assert "list_files" in tool_names
        assert "echo" in tool_names
    
    @pytest.mark.asyncio
    async def test_echo_tool(self):
        """Test echo tool functionality."""
        request = {
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Hello, MCP!"
                }
            }
        }
        
        response = await self.server.handle_request(request)
        
        assert "content" in response
        assert len(response["content"]) > 0
        assert "Echo: Hello, MCP!" in response["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_read_file_tool(self):
        """Test read_file tool with temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = "This is a test file for MCP testing."
            f.write(test_content)
            temp_path = f.name
        
        try:
            request = {
                "method": "tools/call",
                "params": {
                    "name": "read_file",
                    "arguments": {
                        "path": temp_path
                    }
                }
            }
            
            response = await self.server.handle_request(request)
            
            assert "content" in response
            assert test_content in response["content"][0]["text"]
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        """Test read_file tool with non-existent file."""
        request = {
            "method": "tools/call",
            "params": {
                "name": "read_file",
                "arguments": {
                    "path": "/nonexistent/file.txt"
                }
            }
        }
        
        response = await self.server.handle_request(request)
        
        assert "content" in response
        assert "Error: File not found" in response["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_list_files_tool(self):
        """Test list_files tool."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            (Path(temp_dir) / "test1.txt").write_text("test")
            (Path(temp_dir) / "test2.txt").write_text("test")
            (Path(temp_dir) / "subdir").mkdir()
            
            request = {
                "method": "tools/call",
                "params": {
                    "name": "list_files",
                    "arguments": {
                        "directory": temp_dir
                    }
                }
            }
            
            response = await self.server.handle_request(request)
            
            assert "content" in response
            content = response["content"][0]["text"]
            assert "[FILE] test1.txt" in content
            assert "[FILE] test2.txt" in content
            assert "[DIR] subdir" in content
    
    @pytest.mark.asyncio
    async def test_unknown_method(self):
        """Test handling of unknown methods."""
        request = {
            "method": "unknown/method",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32601
    
    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool."""
        request = {
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        
        response = await self.server.handle_request(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32602

if __name__ == "__main__":
    pytest.main([__file__])
