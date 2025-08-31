#!/usr/bin/env python3
"""Test Runner for MCP Validation Suite"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import time

from .validator import MCPValidator, ValidationLevel, ToolValidationResult
from .discovery import ToolDiscovery
from .reporter import ValidationReporter

logger = logging.getLogger(__name__)

@dataclass
class ValidationSuiteResult:
    """Complete validation suite results."""
    total_tools: int
    passed_tools: int
    failed_tools: int
    tool_results: List[ToolValidationResult]
    execution_time: float
    overall_compliance_score: float

class ValidationTestRunner:
    """Orchestrates the complete MCP validation process."""
    
    def __init__(self, server, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.server = server
        self.validation_level = validation_level
        self.validator = MCPValidator(server, validation_level)
        self.discovery = ToolDiscovery(server)
        self.reporter = ValidationReporter()
    
    async def run_full_validation(self, 
                                 tool_filter: Optional[List[str]] = None,
                                 generate_report: bool = True) -> ValidationSuiteResult:
        """Run complete validation suite on all or filtered tools."""
        logger.info("Starting MCP validation suite")
        start_time = time.time()
        
        # Discover available tools
        tools = await self.discovery.discover_tools()
        
        # Filter tools if specified
        if tool_filter:
            tools = [tool for tool in tools if tool.get("name") in tool_filter]
        
        logger.info(f"Found {len(tools)} tools to validate")
        
        # Validate each tool
        tool_results = []
        for tool in tools:
            try:
                result = await self.validator.validate_tool(tool)
                tool_results.append(result)
                
                status = "✅ PASSED" if result.overall_passed else "❌ FAILED"
                logger.info(f"{status} {result.tool_name} (Score: {result.compliance_score:.1f}%)")
                
            except Exception as e:
                logger.error(f"Validation failed for tool {tool.get('name', 'unknown')}: {e}")
                # Create a failed result for the tool
                tool_results.append(ToolValidationResult(
                    tool_name=tool.get("name", "unknown"),
                    overall_passed=False,
                    test_results=[],
                    compliance_score=0.0,
                    execution_time=0.0
                ))
        
        # Calculate overall results
        execution_time = time.time() - start_time
        passed_tools = sum(1 for r in tool_results if r.overall_passed)
        failed_tools = len(tool_results) - passed_tools
        
        # Calculate overall compliance score
        if tool_results:
            overall_compliance_score = sum(r.compliance_score for r in tool_results) / len(tool_results)
        else:
            overall_compliance_score = 0.0
        
        suite_result = ValidationSuiteResult(
            total_tools=len(tool_results),
            passed_tools=passed_tools,
            failed_tools=failed_tools,
            tool_results=tool_results,
            execution_time=execution_time,
            overall_compliance_score=overall_compliance_score
        )
        
        # Generate report if requested
        if generate_report:
            await self.reporter.generate_report(suite_result)
        
        logger.info(f"Validation complete: {passed_tools}/{len(tool_results)} tools passed")
        return suite_result
    
    async def run_tool_validation(self, tool_name: str) -> Optional[ToolValidationResult]:
        """Run validation on a specific tool."""
        tools = await self.discovery.discover_tools()
        
        target_tool = None
        for tool in tools:
            if tool.get("name") == tool_name:
                target_tool = tool
                break
        
        if not target_tool:
            logger.error(f"Tool '{tool_name}' not found")
            return None
        
        return await self.validator.validate_tool(target_tool)
    
    async def run_continuous_validation(self, 
                                      interval_seconds: int = 300,
                                      max_iterations: Optional[int] = None) -> None:
        """Run validation continuously at specified intervals."""
        logger.info(f"Starting continuous validation (interval: {interval_seconds}s)")
        
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            try:
                logger.info(f"Running validation iteration {iteration + 1}")
                result = await self.run_full_validation(generate_report=False)
                
                # Log summary
                logger.info(f"Iteration {iteration + 1} complete: "
                           f"{result.passed_tools}/{result.total_tools} passed, "
                           f"score: {result.overall_compliance_score:.1f}%")
                
                # Wait for next iteration
                if max_iterations is None or iteration + 1 < max_iterations:
                    await asyncio.sleep(interval_seconds)
                
                iteration += 1
                
            except KeyboardInterrupt:
                logger.info("Continuous validation stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in validation iteration {iteration + 1}: {e}")
                await asyncio.sleep(interval_seconds)
                iteration += 1
    
    async def benchmark_tools(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark tool performance over multiple iterations."""
        logger.info(f"Starting tool benchmark ({iterations} iterations)")
        
        tools = await self.discovery.discover_tools()
        benchmark_results = {}
        
        for tool in tools:
            tool_name = tool.get("name")
            logger.info(f"Benchmarking tool: {tool_name}")
            
            execution_times = []
            success_count = 0
            
            for i in range(iterations):
                try:
                    start_time = time.time()
                    result = await self.validator.validate_tool(tool)
                    execution_time = time.time() - start_time
                    
                    execution_times.append(execution_time)
                    if result.overall_passed:
                        success_count += 1
                        
                except Exception as e:
                    logger.warning(f"Benchmark iteration {i+1} failed for {tool_name}: {e}")
                    execution_times.append(float('inf'))
            
            # Calculate statistics
            valid_times = [t for t in execution_times if t != float('inf')]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                min_time = min(valid_times)
                max_time = max(valid_times)
            else:
                avg_time = min_time = max_time = 0.0
            
            benchmark_results[tool_name] = {
                "iterations": iterations,
                "success_count": success_count,
                "success_rate": success_count / iterations * 100,
                "avg_execution_time": avg_time,
                "min_execution_time": min_time,
                "max_execution_time": max_time,
                "execution_times": execution_times
            }
        
        return benchmark_results
    
    def set_validation_level(self, level: ValidationLevel) -> None:
        """Change validation strictness level."""
        self.validation_level = level
        self.validator = MCPValidator(self.server, level)
        logger.info(f"Validation level set to: {level.value}")
