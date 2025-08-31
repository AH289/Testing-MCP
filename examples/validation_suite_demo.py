#!/usr/bin/env python3
"""MCP Validation Suite Demo"""

import asyncio
import logging
from src.mcp_server import MCPServer
from src.validation import MCPValidator, ValidationTestRunner, ValidationLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_validation_demo():
    """Demonstrate the MCP Validation Suite capabilities."""
    print("=== MCP Validation Suite Demo ===")
    
    # Create server instance
    server = MCPServer("validation-demo-server")
    
    # Create validation test runner
    runner = ValidationTestRunner(server, ValidationLevel.STANDARD)
    
    print("\n1. Running full validation suite...")
    
    # Run complete validation
    suite_result = await runner.run_full_validation()
    
    print(f"\n2. Validation Results Summary:")
    print(f"   - Total tools validated: {suite_result.total_tools}")
    print(f"   - Tools passed: {suite_result.passed_tools}")
    print(f"   - Tools failed: {suite_result.failed_tools}")
    print(f"   - Overall compliance score: {suite_result.overall_compliance_score:.1f}%")
    print(f"   - Total execution time: {suite_result.execution_time:.2f}s")
    
    # Show detailed results for each tool
    print(f"\n3. Detailed Tool Results:")
    for tool_result in suite_result.tool_results:
        status = "PASSED" if tool_result.overall_passed else "FAILED"
        print(f"\n   Tool: {tool_result.tool_name} - {status}")
        print(f"   Compliance Score: {tool_result.compliance_score:.1f}%")
        print(f"   Execution Time: {tool_result.execution_time:.3f}s")
        
        # Show failed tests
        failed_tests = [t for t in tool_result.test_results if not t.passed]
        if failed_tests:
            print(f"   Failed Tests:")
            for test in failed_tests:
                print(f"     - {test.test_name}: {test.message}")
        
        # Show warnings
        warning_tests = [t for t in tool_result.test_results if t.severity == "warning" and t.passed]
        if warning_tests:
            print(f"   Warnings:")
            for test in warning_tests:
                print(f"     - {test.test_name}: {test.message}")
    
    # Demonstrate single tool validation
    print(f"\n4. Single Tool Validation Demo (echo tool):")
    echo_result = await runner.run_tool_validation("echo")
    if echo_result:
        print(f"   Echo tool validation: {'PASSED' if echo_result.overall_passed else 'FAILED'}")
        print(f"   Compliance score: {echo_result.compliance_score:.1f}%")
        
        for test in echo_result.test_results:
            status = "✅" if test.passed else "❌"
            if test.severity == "warning":
                status = "⚠️"
            print(f"   {status} {test.test_name}: {test.message}")
    
    # Demonstrate different validation levels
    print(f"\n5. Validation Level Comparison:")
    
    for level in [ValidationLevel.BASIC, ValidationLevel.STANDARD, ValidationLevel.STRICT]:
        runner.set_validation_level(level)
        level_result = await runner.run_tool_validation("echo")
        
        if level_result:
            print(f"   {level.value.upper()}: Score {level_result.compliance_score:.1f}%, "
                  f"Tests: {len(level_result.test_results)}, "
                  f"Time: {level_result.execution_time:.3f}s")
    
    # Demonstrate benchmarking
    print(f"\n6. Performance Benchmark (3 iterations):")
    benchmark_results = await runner.benchmark_tools(iterations=3)
    
    for tool_name, stats in benchmark_results.items():
        print(f"   {tool_name}:")
        print(f"     Success Rate: {stats['success_rate']:.1f}%")
        print(f"     Avg Time: {stats['avg_execution_time']:.3f}s")
        print(f"     Min/Max: {stats['min_execution_time']:.3f}s / {stats['max_execution_time']:.3f}s")
    
    print(f"\n=== Demo completed successfully! ===")
    print(f"\nCheck the 'validation_reports' directory for detailed HTML and JSON reports.")

if __name__ == "__main__":
    asyncio.run(run_validation_demo())
