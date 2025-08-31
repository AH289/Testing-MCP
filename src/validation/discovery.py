#!/usr/bin/env python3
"""Tool Discovery for MCP Validation Suite"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class ToolDiscovery:
    """Discovers and catalogs available MCP tools."""
    
    def __init__(self, server):
        self.server = server
        self._tool_cache = None
        self._cache_timestamp = None
    
    async def discover_tools(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Discover all available tools from the MCP server."""
        if use_cache and self._tool_cache is not None:
            logger.debug("Using cached tool list")
            return self._tool_cache
        
        logger.info("Discovering available MCP tools")
        
        try:
            # Request tools list from server
            request = {
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.server.handle_request(request)
            
            if "error" in response:
                logger.error(f"Error discovering tools: {response['error']}")
                return []
            
            tools = response.get("tools", [])
            logger.info(f"Discovered {len(tools)} tools")
            
            # Cache the results
            self._tool_cache = tools
            import time
            self._cache_timestamp = time.time()
            
            return tools
            
        except Exception as e:
            logger.error(f"Exception during tool discovery: {e}")
            return []
    
    async def get_tool_details(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool."""
        tools = await self.discover_tools()
        
        for tool in tools:
            if tool.get("name") == tool_name:
                return tool
        
        return None
    
    async def categorize_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize tools by their functionality."""
        tools = await self.discover_tools()
        categories = {
            "file_operations": [],
            "data_processing": [],
            "communication": [],
            "system_tools": [],
            "utility": [],
            "unknown": []
        }
        
        for tool in tools:
            tool_name = tool.get("name", "").lower()
            description = tool.get("description", "").lower()
            
            # Categorize based on name and description keywords
            if any(keyword in tool_name or keyword in description 
                   for keyword in ["file", "read", "write", "list", "directory"]):
                categories["file_operations"].append(tool)
            elif any(keyword in tool_name or keyword in description 
                     for keyword in ["process", "transform", "parse", "convert"]):
                categories["data_processing"].append(tool)
            elif any(keyword in tool_name or keyword in description 
                     for keyword in ["send", "receive", "message", "email", "http"]):
                categories["communication"].append(tool)
            elif any(keyword in tool_name or keyword in description 
                     for keyword in ["system", "execute", "run", "command"]):
                categories["system_tools"].append(tool)
            elif any(keyword in tool_name or keyword in description 
                     for keyword in ["echo", "test", "validate", "check"]):
                categories["utility"].append(tool)
            else:
                categories["unknown"].append(tool)
        
        return categories
    
    async def analyze_tool_complexity(self) -> Dict[str, Dict[str, Any]]:
        """Analyze the complexity of each tool based on its schema."""
        tools = await self.discover_tools()
        complexity_analysis = {}
        
        for tool in tools:
            tool_name = tool.get("name")
            schema = tool.get("inputSchema", {})
            
            # Calculate complexity metrics
            complexity_score = 0
            metrics = {
                "parameter_count": 0,
                "required_parameters": 0,
                "nested_objects": 0,
                "has_arrays": False,
                "complexity_level": "simple"
            }
            
            if schema.get("type") == "object":
                properties = schema.get("properties", {})
                required = schema.get("required", [])
                
                metrics["parameter_count"] = len(properties)
                metrics["required_parameters"] = len(required)
                
                # Check for nested complexity
                for prop_name, prop_def in properties.items():
                    if isinstance(prop_def, dict):
                        prop_type = prop_def.get("type")
                        if prop_type == "object":
                            metrics["nested_objects"] += 1
                            complexity_score += 2
                        elif prop_type == "array":
                            metrics["has_arrays"] = True
                            complexity_score += 1
                        else:
                            complexity_score += 0.5
            
            # Determine complexity level
            if complexity_score <= 2:
                metrics["complexity_level"] = "simple"
            elif complexity_score <= 5:
                metrics["complexity_level"] = "moderate"
            else:
                metrics["complexity_level"] = "complex"
            
            metrics["complexity_score"] = complexity_score
            complexity_analysis[tool_name] = metrics
        
        return complexity_analysis
    
    async def generate_tool_registry(self) -> Dict[str, Any]:
        """Generate a comprehensive tool registry with metadata."""
        tools = await self.discover_tools()
        categories = await self.categorize_tools()
        complexity = await self.analyze_tool_complexity()
        
        registry = {
            "metadata": {
                "total_tools": len(tools),
                "discovery_timestamp": self._cache_timestamp,
                "categories": {cat: len(tools_list) for cat, tools_list in categories.items()}
            },
            "tools": {},
            "categories": categories,
            "complexity_analysis": complexity
        }
        
        # Add detailed tool information
        for tool in tools:
            tool_name = tool.get("name")
            registry["tools"][tool_name] = {
                "definition": tool,
                "category": self._get_tool_category(tool, categories),
                "complexity": complexity.get(tool_name, {}),
                "validation_ready": self._is_validation_ready(tool)
            }
        
        return registry
    
    def _get_tool_category(self, tool: Dict[str, Any], categories: Dict[str, List]) -> str:
        """Determine which category a tool belongs to."""
        for category, tools_list in categories.items():
            if tool in tools_list:
                return category
        return "unknown"
    
    def _is_validation_ready(self, tool: Dict[str, Any]) -> bool:
        """Check if a tool has sufficient information for validation."""
        required_fields = ["name", "description", "inputSchema"]
        return all(field in tool for field in required_fields)
    
    async def refresh_cache(self) -> None:
        """Force refresh of the tool cache."""
        self._tool_cache = None
        self._cache_timestamp = None
        await self.discover_tools(use_cache=False)
        logger.info("Tool cache refreshed")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache state."""
        return {
            "cached_tools": len(self._tool_cache) if self._tool_cache else 0,
            "cache_timestamp": self._cache_timestamp,
            "cache_age_seconds": (time.time() - self._cache_timestamp) if self._cache_timestamp else None
        }
