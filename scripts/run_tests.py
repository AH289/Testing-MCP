#!/usr/bin/env python3
"""Test runner script for MCP Testing Repository"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n=== {description} ===")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run MCP tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--examples", action="store_true", help="Run example scripts")
    parser.add_argument("--lint", action="store_true", help="Run linting checks")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # If no specific tests requested, run all
    if not any([args.unit, args.integration, args.examples, args.lint]):
        args.all = True
    
    success = True
    
    # Change to repository root
    repo_root = Path(__file__).parent.parent
    print(f"Repository root: {repo_root}")
    
    # Run unit tests
    if args.unit or args.all:
        cmd = ["python", "-m", "pytest", "tests/test_mcp_server.py"]
        if args.verbose:
            cmd.append("-v")
        if not run_command(cmd, "Unit Tests"):
            success = False
    
    # Run integration tests
    if args.integration or args.all:
        cmd = ["python", "-m", "pytest", "tests/test_integration.py"]
        if args.verbose:
            cmd.append("-v")
        if not run_command(cmd, "Integration Tests"):
            success = False
    
    # Run example scripts
    if args.examples or args.all:
        examples = [
            ("examples/basic_client.py", "Basic Client Example"),
            ("examples/tool_validation.py", "Tool Validation Example")
        ]
        
        for script, description in examples:
            if not run_command(["python", script], description):
                success = False
    
    # Run linting
    if args.lint or args.all:
        lint_commands = [
            (["python", "-m", "flake8", "src", "tests", "examples"], "Flake8 Linting"),
            (["python", "-m", "black", "--check", "src", "tests", "examples"], "Black Formatting Check"),
            (["python", "-m", "mypy", "src"], "MyPy Type Checking")
        ]
        
        for cmd, description in lint_commands:
            # Skip if tools not available
            try:
                subprocess.run([cmd[2], "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"\nSkipping {description} - tool not installed")
                continue
            
            if not run_command(cmd, description):
                success = False
    
    # Print summary
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
