#!/usr/bin/env python3
"""MCP Validation Suite Runner Script"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server import MCPServer
from validation import ValidationTestRunner, ValidationLevel

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def main():
    """Main validation runner function."""
    parser = argparse.ArgumentParser(description="MCP Validation Suite Runner")
    parser.add_argument("--tool", "-t", help="Validate specific tool only")
    parser.add_argument("--level", "-l", 
                       choices=["basic", "standard", "strict"],
                       default="standard",
                       help="Validation strictness level")
    parser.add_argument("--format", "-f",
                       choices=["console", "json", "html", "markdown"],
                       action="append",
                       help="Report format(s) to generate")
    parser.add_argument("--output", "-o",
                       default="validation_reports",
                       help="Output directory for reports")
    parser.add_argument("--benchmark", "-b",
                       type=int,
                       help="Run benchmark with specified iterations")
    parser.add_argument("--continuous", "-c",
                       type=int,
                       help="Run continuous validation with interval in seconds")
    parser.add_argument("--max-iterations",
                       type=int,
                       help="Maximum iterations for continuous mode")
    parser.add_argument("--verbose", "-v",
                       action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Create server and runner
    server = MCPServer("validation-runner-server")
    
    # Set validation level
    level_map = {
        "basic": ValidationLevel.BASIC,
        "standard": ValidationLevel.STANDARD,
        "strict": ValidationLevel.STRICT
    }
    validation_level = level_map[args.level]
    
    runner = ValidationTestRunner(server, validation_level)
    
    # Set output directory
    runner.reporter.output_dir = Path(args.output)
    runner.reporter.output_dir.mkdir(exist_ok=True)
    
    try:
        if args.benchmark:
            # Run benchmark
            logger.info(f"Running benchmark with {args.benchmark} iterations")
            results = await runner.benchmark_tools(args.benchmark)
            
            print("\n=== BENCHMARK RESULTS ===")
            for tool_name, stats in results.items():
                print(f"\n{tool_name}:")
                print(f"  Success Rate: {stats['success_rate']:.1f}%")
                print(f"  Average Time: {stats['avg_execution_time']:.3f}s")
                print(f"  Min/Max Time: {stats['min_execution_time']:.3f}s / {stats['max_execution_time']:.3f}s")
        
        elif args.continuous:
            # Run continuous validation
            logger.info(f"Starting continuous validation (interval: {args.continuous}s)")
            await runner.run_continuous_validation(
                interval_seconds=args.continuous,
                max_iterations=args.max_iterations
            )
        
        elif args.tool:
            # Validate specific tool
            logger.info(f"Validating tool: {args.tool}")
            result = await runner.run_tool_validation(args.tool)
            
            if result:
                status = "PASSED" if result.overall_passed else "FAILED"
                print(f"\nTool '{args.tool}' validation: {status}")
                print(f"Compliance Score: {result.compliance_score:.1f}%")
                print(f"Execution Time: {result.execution_time:.3f}s")
                
                print("\nTest Results:")
                for test in result.test_results:
                    status_icon = "✅" if test.passed else "❌"
                    if test.severity == "warning":
                        status_icon = "⚠️"
                    print(f"  {status_icon} {test.test_name}: {test.message}")
            else:
                print(f"Tool '{args.tool}' not found")
                sys.exit(1)
        
        else:
            # Run full validation suite
            logger.info("Running full validation suite")
            
            # Set report formats
            formats = args.format if args.format else ["console", "json", "html"]
            
            # Run validation
            suite_result = await runner.run_full_validation()
            
            # Generate additional reports if requested
            if any(fmt != "console" for fmt in formats):
                report_files = await runner.reporter.generate_report(suite_result, formats)
                
                print("\nGenerated Reports:")
                for format_type, file_path in report_files.items():
                    print(f"  {format_type.upper()}: {file_path}")
    
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
