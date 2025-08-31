#!/usr/bin/env python3
"""Core MCP Validation Engine"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation strictness levels."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"

@dataclass
class ValidationResult:
    """Result of a validation test."""
    test_name: str
    passed: bool
    message: str
    details: Dict[str, Any]
    execution_time: float
    severity: str = "info"  # info, warning, error, critical

@dataclass
class ToolValidationResult:
    """Complete validation result for a tool."""
    tool_name: str
    overall_passed: bool
    test_results: List[ValidationResult]
    compliance_score: float
    execution_time: float

class MCPValidator:
    """Comprehensive MCP Tool Validation Engine."""
    
    def __init__(self, server, validation_level: ValidationLevel = ValidationLevel.STANDARD):
        self.server = server
        self.validation_level = validation_level
        self.test_registry = {}
        self._register_core_tests()
    
    def _register_core_tests(self):
        """Register core validation tests."""
        self.test_registry = {
            "schema_validation": self._validate_tool_schema,
            "protocol_compliance": self._validate_protocol_compliance,
            "execution_test": self._validate_tool_execution,
            "error_handling": self._validate_error_handling,
            "performance_test": self._validate_performance,
            "security_check": self._validate_security,
            "input_validation": self._validate_input_handling
        }
    
    async def validate_tool(self, tool: Dict[str, Any]) -> ToolValidationResult:
        """Validate a single MCP tool comprehensively."""
        tool_name = tool.get("name", "unknown")
        logger.info(f"Starting validation for tool: {tool_name}")
        
        start_time = time.time()
        test_results = []
        
        # Run all registered tests
        for test_name, test_func in self.test_registry.items():
            try:
                result = await test_func(tool)
                test_results.append(result)
                
                if result.severity == "critical" and not result.passed:
                    logger.error(f"Critical failure in {test_name} for {tool_name}")
                    break  # Stop on critical failures
                    
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
                test_results.append(ValidationResult(
                    test_name=test_name,
                    passed=False,
                    message=f"Test threw exception: {str(e)}",
                    details={"exception": str(e)},
                    execution_time=0.0,
                    severity="error"
                ))
        
        # Calculate overall results
        execution_time = time.time() - start_time
        passed_tests = sum(1 for r in test_results if r.passed)
        total_tests = len(test_results)
        compliance_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        overall_passed = all(r.passed or r.severity in ["info", "warning"] for r in test_results)
        
        return ToolValidationResult(
            tool_name=tool_name,
            overall_passed=overall_passed,
            test_results=test_results,
            compliance_score=compliance_score,
            execution_time=execution_time
        )
    
    async def _validate_tool_schema(self, tool: Dict[str, Any]) -> ValidationResult:
        """Validate tool schema compliance."""
        start_time = time.time()
        errors = []
        
        # Required fields check
        required_fields = ["name", "description", "inputSchema"]
        for field in required_fields:
            if field not in tool:
                errors.append(f"Missing required field: {field}")
        
        # Schema structure validation
        if "inputSchema" in tool:
            schema = tool["inputSchema"]
            if not isinstance(schema, dict):
                errors.append("inputSchema must be an object")
            else:
                if "type" not in schema:
                    errors.append("inputSchema missing 'type' field")
                if schema.get("type") == "object" and "properties" not in schema:
                    errors.append("Object schema missing 'properties' field")
        
        # Name validation
        if "name" in tool:
            name = tool["name"]
            if not isinstance(name, str) or not name.strip():
                errors.append("Tool name must be a non-empty string")
            elif not name.replace("_", "").replace("-", "").isalnum():
                errors.append("Tool name should only contain alphanumeric characters, hyphens, and underscores")
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            test_name="schema_validation",
            passed=len(errors) == 0,
            message="Schema validation passed" if len(errors) == 0 else f"Schema validation failed: {'; '.join(errors)}",
            details={"errors": errors, "tool_schema": tool},
            execution_time=execution_time,
            severity="critical" if errors else "info"
        )
    
    async def _validate_protocol_compliance(self, tool: Dict[str, Any]) -> ValidationResult:
        """Validate MCP protocol compliance."""
        start_time = time.time()
        issues = []
        
        # Check if tool follows MCP naming conventions
        tool_name = tool.get("name", "")
        if "/" in tool_name:
            issues.append("Tool names should not contain forward slashes (use underscores or hyphens)")
        
        # Validate description quality
        description = tool.get("description", "")
        if len(description) < 10:
            issues.append("Tool description should be at least 10 characters long")
        elif len(description) > 200:
            issues.append("Tool description should be concise (under 200 characters)")
        
        # Check for proper input schema structure
        schema = tool.get("inputSchema", {})
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            for prop_name, prop_def in properties.items():
                if not isinstance(prop_def, dict):
                    issues.append(f"Property '{prop_name}' definition must be an object")
                elif "description" not in prop_def:
                    issues.append(f"Property '{prop_name}' missing description")
        
        execution_time = time.time() - start_time
        severity = "warning" if issues else "info"
        
        return ValidationResult(
            test_name="protocol_compliance",
            passed=len(issues) == 0,
            message="Protocol compliance passed" if len(issues) == 0 else f"Protocol issues found: {'; '.join(issues)}",
            details={"issues": issues},
            execution_time=execution_time,
            severity=severity
        )
    
    async def _validate_tool_execution(self, tool: Dict[str, Any]) -> ValidationResult:
        """Test tool execution with sample inputs."""
        start_time = time.time()
        tool_name = tool.get("name")
        
        # Generate test inputs based on schema
        test_cases = self._generate_test_inputs(tool)
        
        execution_results = []
        for test_case in test_cases:
            try:
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": test_case["input"]
                    }
                }
                
                response = await self.server.handle_request(request)
                
                success = "error" not in response and "content" in response
                execution_results.append({
                    "test_case": test_case["description"],
                    "success": success,
                    "response": response
                })
                
            except Exception as e:
                execution_results.append({
                    "test_case": test_case["description"],
                    "success": False,
                    "error": str(e)
                })
        
        execution_time = time.time() - start_time
        successful_executions = sum(1 for r in execution_results if r["success"])
        total_executions = len(execution_results)
        
        passed = successful_executions > 0  # At least one test case should pass
        
        return ValidationResult(
            test_name="execution_test",
            passed=passed,
            message=f"Execution test: {successful_executions}/{total_executions} test cases passed",
            details={"execution_results": execution_results},
            execution_time=execution_time,
            severity="error" if not passed else "info"
        )
    
    async def _validate_error_handling(self, tool: Dict[str, Any]) -> ValidationResult:
        """Test tool error handling with invalid inputs."""
        start_time = time.time()
        tool_name = tool.get("name")
        
        error_test_cases = [
            {"description": "Empty arguments", "input": {}},
            {"description": "Invalid argument types", "input": {"invalid_key": 12345}},
            {"description": "Missing required arguments", "input": {"wrong_field": "value"}}
        ]
        
        error_handling_results = []
        for test_case in error_test_cases:
            try:
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": test_case["input"]
                    }
                }
                
                response = await self.server.handle_request(request)
                
                # Good error handling should return structured error responses
                has_error = "error" in response
                error_has_code = has_error and "code" in response["error"]
                error_has_message = has_error and "message" in response["error"]
                
                proper_error_handling = has_error and error_has_code and error_has_message
                
                error_handling_results.append({
                    "test_case": test_case["description"],
                    "proper_error_handling": proper_error_handling,
                    "response": response
                })
                
            except Exception as e:
                error_handling_results.append({
                    "test_case": test_case["description"],
                    "proper_error_handling": False,
                    "exception": str(e)
                })
        
        execution_time = time.time() - start_time
        proper_errors = sum(1 for r in error_handling_results if r["proper_error_handling"])
        total_tests = len(error_handling_results)
        
        passed = proper_errors >= total_tests * 0.5  # At least 50% should handle errors properly
        
        return ValidationResult(
            test_name="error_handling",
            passed=passed,
            message=f"Error handling: {proper_errors}/{total_tests} cases handled properly",
            details={"error_handling_results": error_handling_results},
            execution_time=execution_time,
            severity="warning" if not passed else "info"
        )
    
    async def _validate_performance(self, tool: Dict[str, Any]) -> ValidationResult:
        """Test tool performance characteristics."""
        start_time = time.time()
        tool_name = tool.get("name")
        
        # Generate a simple test case
        test_cases = self._generate_test_inputs(tool)
        if not test_cases:
            return ValidationResult(
                test_name="performance_test",
                passed=True,
                message="Performance test skipped - no valid test cases",
                details={},
                execution_time=0.0,
                severity="info"
            )
        
        # Run performance test
        execution_times = []
        for _ in range(3):  # Run 3 times for average
            test_start = time.time()
            try:
                request = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": test_cases[0]["input"]
                    }
                }
                
                await self.server.handle_request(request)
                execution_times.append(time.time() - test_start)
                
            except Exception:
                execution_times.append(float('inf'))  # Mark as failed
        
        avg_execution_time = sum(t for t in execution_times if t != float('inf')) / len([t for t in execution_times if t != float('inf')]) if execution_times else 0
        
        # Performance thresholds
        excellent_threshold = 0.1  # 100ms
        good_threshold = 0.5      # 500ms
        acceptable_threshold = 2.0 # 2s
        
        if avg_execution_time <= excellent_threshold:
            performance_rating = "excellent"
        elif avg_execution_time <= good_threshold:
            performance_rating = "good"
        elif avg_execution_time <= acceptable_threshold:
            performance_rating = "acceptable"
        else:
            performance_rating = "poor"
        
        passed = avg_execution_time <= acceptable_threshold
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            test_name="performance_test",
            passed=passed,
            message=f"Performance: {performance_rating} (avg: {avg_execution_time:.3f}s)",
            details={
                "average_execution_time": avg_execution_time,
                "execution_times": execution_times,
                "performance_rating": performance_rating
            },
            execution_time=execution_time,
            severity="warning" if not passed else "info"
        )
    
    async def _validate_security(self, tool: Dict[str, Any]) -> ValidationResult:
        """Basic security validation checks."""
        start_time = time.time()
        security_issues = []
        
        tool_name = tool.get("name", "")
        description = tool.get("description", "")
        
        # Check for potentially dangerous operations in description
        dangerous_keywords = ["delete", "remove", "execute", "run", "shell", "command", "system"]
        found_keywords = [kw for kw in dangerous_keywords if kw.lower() in description.lower()]
        
        if found_keywords:
            security_issues.append(f"Tool description mentions potentially dangerous operations: {', '.join(found_keywords)}")
        
        # Check input schema for file path parameters
        schema = tool.get("inputSchema", {})
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            for prop_name, prop_def in properties.items():
                if "path" in prop_name.lower() or "file" in prop_name.lower():
                    if "description" not in prop_def or "validation" not in prop_def.get("description", "").lower():
                        security_issues.append(f"File/path parameter '{prop_name}' lacks security validation description")
        
        execution_time = time.time() - start_time
        
        # Security issues are warnings unless critical
        severity = "warning" if security_issues else "info"
        
        return ValidationResult(
            test_name="security_check",
            passed=len(security_issues) == 0,
            message="Security check passed" if len(security_issues) == 0 else f"Security concerns: {'; '.join(security_issues)}",
            details={"security_issues": security_issues},
            execution_time=execution_time,
            severity=severity
        )
    
    async def _validate_input_handling(self, tool: Dict[str, Any]) -> ValidationResult:
        """Validate input parameter handling."""
        start_time = time.time()
        issues = []
        
        schema = tool.get("inputSchema", {})
        
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            # Check if required fields are properly defined
            for req_field in required:
                if req_field not in properties:
                    issues.append(f"Required field '{req_field}' not defined in properties")
            
            # Check property definitions
            for prop_name, prop_def in properties.items():
                if "type" not in prop_def:
                    issues.append(f"Property '{prop_name}' missing type definition")
                if "description" not in prop_def:
                    issues.append(f"Property '{prop_name}' missing description")
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            test_name="input_validation",
            passed=len(issues) == 0,
            message="Input validation passed" if len(issues) == 0 else f"Input handling issues: {'; '.join(issues)}",
            details={"issues": issues},
            execution_time=execution_time,
            severity="warning" if issues else "info"
        )
    
    def _generate_test_inputs(self, tool: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test inputs based on tool schema."""
        tool_name = tool.get("name")
        schema = tool.get("inputSchema", {})
        
        # Predefined test cases for known tools
        known_test_cases = {
            "echo": [{"description": "Basic echo test", "input": {"message": "test message"}}],
            "read_file": [{"description": "Read README", "input": {"path": "README.md"}}],
            "list_files": [{"description": "List current directory", "input": {"directory": "."}}]
        }
        
        if tool_name in known_test_cases:
            return known_test_cases[tool_name]
        
        # Generate generic test cases based on schema
        test_cases = []
        
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            # Generate a basic test case with required fields
            test_input = {}
            for req_field in required:
                if req_field in properties:
                    prop_type = properties[req_field].get("type", "string")
                    if prop_type == "string":
                        test_input[req_field] = "test_value"
                    elif prop_type == "number":
                        test_input[req_field] = 42
                    elif prop_type == "boolean":
                        test_input[req_field] = True
                    else:
                        test_input[req_field] = "test_value"
            
            if test_input or not required:
                test_cases.append({
                    "description": "Generated test case",
                    "input": test_input
                })
        
        return test_cases
