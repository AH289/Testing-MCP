#!/usr/bin/env python3
"""Tool Validation Example"""

import asyncio
import json
from typing import Dict, List, Any
from src.mcp_server import MCPServer

class ToolValidator:
    """Validates MCP tools against their schemas."""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.validation_results = []
    
    async def validate_all_tools(self) -> Dict[str, Any]:
        """Validate all tools in the server."""
        print("=== MCP Tool Validation ===")
        
        # Get list of tools
        list_request = {
            "method": "tools/list",
            "params": {}
        }
        
        list_response = await self.server.handle_request(list_request)
        tools = list_response.get("tools", [])
        
        print(f"\nFound {len(tools)} tools to validate")
        
        results = {
            "total_tools": len(tools),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for tool in tools:
            tool_name = tool["name"]
            print(f"\nValidating tool: {tool_name}")
            
            validation_result = await self._validate_tool(tool)
            results["details"].append(validation_result)
            
            if validation_result["passed"]:
                results["passed"] += 1
                print(f"  ✅ {tool_name} - PASSED")
            else:
                results["failed"] += 1
                print(f"  ❌ {tool_name} - FAILED")
                for error in validation_result["errors"]:
                    print(f"     - {error}")
        
        return results
    
    async def _validate_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single tool."""
        tool_name = tool["name"]
        errors = []
        
        # Check required fields
        required_fields = ["name", "description", "inputSchema"]
        for field in required_fields:
            if field not in tool:
                errors.append(f"Missing required field: {field}")
        
        # Validate input schema
        if "inputSchema" in tool:
            schema = tool["inputSchema"]
            if not isinstance(schema, dict):
                errors.append("inputSchema must be an object")
            elif "type" not in schema:
                errors.append("inputSchema missing 'type' field")
        
        # Test tool execution with valid inputs
        if not errors:
            execution_result = await self._test_tool_execution(tool)
            if not execution_result["success"]:
                errors.extend(execution_result["errors"])
        
        return {
            "tool_name": tool_name,
            "passed": len(errors) == 0,
            "errors": errors
        }
    
    async def _test_tool_execution(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Test tool execution with sample inputs."""
        tool_name = tool["name"]
        errors = []
        
        # Define test cases for each tool
        test_cases = {
            "echo": {
                "message": "test message"
            },
            "list_files": {
                "directory": "."
            },
            "read_file": {
                "path": "README.md"
            }
        }
        
        if tool_name in test_cases:
            try:
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": test_cases[tool_name]
                    }
                }
                
                response = await self.server.handle_request(request)
                
                if "error" in response:
                    errors.append(f"Tool execution failed: {response['error']['message']}")
                elif "content" not in response:
                    errors.append("Tool response missing 'content' field")
                elif not isinstance(response["content"], list):
                    errors.append("Tool response 'content' must be a list")
                
            except Exception as e:
                errors.append(f"Tool execution threw exception: {str(e)}")
        
        return {
            "success": len(errors) == 0,
            "errors": errors
        }

async def run_validation_example():
    """Run tool validation example."""
    # Create server and validator
    server = MCPServer("validation-server")
    validator = ToolValidator(server)
    
    # Run validation
    results = await validator.validate_all_tools()
    
    # Print summary
    print("\n=== Validation Summary ===")
    print(f"Total tools: {results['total_tools']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] > 0:
        print("\nFailed tools:")
        for detail in results['details']:
            if not detail['passed']:
                print(f"  - {detail['tool_name']}")
                for error in detail['errors']:
                    print(f"    * {error}")
    
    success_rate = (results['passed'] / results['total_tools']) * 100 if results['total_tools'] > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_validation_example())
