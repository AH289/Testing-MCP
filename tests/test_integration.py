#!/usr/bin/env python3
"""Integration tests for MCP Server"""

import asyncio
import pytest
import json
from src.mcp_server import MCPServer

class TestMCPIntegration:
    """Integration test cases for MCP Server."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = MCPServer("integration-test-server")
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete MCP workflow: initialize -> list tools -> call tool."""
        # Step 1: Initialize
        init_request = {
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_response = await self.server.handle_request(init_request)
        assert "protocolVersion" in init_response
        
        # Step 2: List tools
        list_request = {
            "method": "tools/list",
            "params": {}
        }
        
        list_response = await self.server.handle_request(list_request)
        assert "tools" in list_response
        assert len(list_response["tools"]) > 0
        
        # Step 3: Call echo tool
        echo_request = {
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Integration test successful!"
                }
            }
        }
        
        echo_response = await self.server.handle_request(echo_request)
        assert "content" in echo_response
        assert "Integration test successful!" in echo_response["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self):
        """Test calling multiple tools in sequence."""
        # Call echo tool
        echo_request = {
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"message": "First call"}
            }
        }
        
        echo_response = await self.server.handle_request(echo_request)
        assert "Echo: First call" in echo_response["content"][0]["text"]
        
        # Call list_files tool
        list_request = {
            "method": "tools/call",
            "params": {
                "name": "list_files",
                "arguments": {"directory": "."}
            }
        }
        
        list_response = await self.server.handle_request(list_request)
        assert "content" in list_response
        
        # Call echo tool again
        echo_request2 = {
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"message": "Second call"}
            }
        }
        
        echo_response2 = await self.server.handle_request(echo_request2)
        assert "Echo: Second call" in echo_response2["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling in various scenarios."""
        # Test unknown method
        unknown_request = {
            "method": "invalid/method",
            "params": {}
        }
        
        unknown_response = await self.server.handle_request(unknown_request)
        assert "error" in unknown_response
        
        # Test invalid tool call
        invalid_tool_request = {
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }
        
        invalid_tool_response = await self.server.handle_request(invalid_tool_request)
        assert "error" in invalid_tool_response
        
        # Verify server still works after errors
        echo_request = {
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"message": "Still working!"}
            }
        }
        
        echo_response = await self.server.handle_request(echo_request)
        assert "Echo: Still working!" in echo_response["content"][0]["text"]

if __name__ == "__main__":
    pytest.main([__file__])
