#!/usr/bin/env python3
"""Validation Reporter for MCP Validation Suite"""

import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import time
from datetime import datetime

from .test_runner import ValidationSuiteResult
from .validator import ToolValidationResult, ValidationResult

logger = logging.getLogger(__name__)

class ValidationReporter:
    """Generates comprehensive validation reports in multiple formats."""
    
    def __init__(self, output_dir: str = "validation_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_report(self, 
                            suite_result: ValidationSuiteResult,
                            formats: List[str] = None) -> Dict[str, str]:
        """Generate validation reports in specified formats."""
        if formats is None:
            formats = ["console", "json", "html"]
        
        report_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for format_type in formats:
            try:
                if format_type == "console":
                    self._generate_console_report(suite_result)
                elif format_type == "json":
                    file_path = await self._generate_json_report(suite_result, timestamp)
                    report_files["json"] = str(file_path)
                elif format_type == "html":
                    file_path = await self._generate_html_report(suite_result, timestamp)
                    report_files["html"] = str(file_path)
                elif format_type == "markdown":
                    file_path = await self._generate_markdown_report(suite_result, timestamp)
                    report_files["markdown"] = str(file_path)
                else:
                    logger.warning(f"Unknown report format: {format_type}")
            
            except Exception as e:
                logger.error(f"Failed to generate {format_type} report: {e}")
        
        return report_files
    
    def _generate_console_report(self, suite_result: ValidationSuiteResult) -> None:
        """Generate a console-friendly validation report."""
        print("\n" + "=" * 60)
        print("🔧 MCP VALIDATION SUITE REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📊 SUMMARY")
        print(f"   Total Tools: {suite_result.total_tools}")
        print(f"   Passed: {suite_result.passed_tools} ✅")
        print(f"   Failed: {suite_result.failed_tools} ❌")
        print(f"   Success Rate: {(suite_result.passed_tools/suite_result.total_tools*100):.1f}%")
        print(f"   Overall Compliance Score: {suite_result.overall_compliance_score:.1f}%")
        print(f"   Execution Time: {suite_result.execution_time:.2f}s")
        
        # Tool Results
        print(f"\n🛠️  TOOL RESULTS")
        for tool_result in suite_result.tool_results:
            status = "✅" if tool_result.overall_passed else "❌"
            print(f"   {status} {tool_result.tool_name:<20} Score: {tool_result.compliance_score:5.1f}% Time: {tool_result.execution_time:.3f}s")
        
        # Detailed Failures
        failed_tools = [r for r in suite_result.tool_results if not r.overall_passed]
        if failed_tools:
            print(f"\n❌ FAILED TOOLS DETAILS")
            for tool_result in failed_tools:
                print(f"\n   Tool: {tool_result.tool_name}")
                failed_tests = [t for t in tool_result.test_results if not t.passed]
                for test in failed_tests:
                    print(f"     ❌ {test.test_name}: {test.message}")
        
        # Performance Summary
        if suite_result.tool_results:
            avg_tool_time = sum(r.execution_time for r in suite_result.tool_results) / len(suite_result.tool_results)
            fastest_tool = min(suite_result.tool_results, key=lambda r: r.execution_time)
            slowest_tool = max(suite_result.tool_results, key=lambda r: r.execution_time)
            
            print(f"\n⚡ PERFORMANCE")
            print(f"   Average Tool Validation Time: {avg_tool_time:.3f}s")
            print(f"   Fastest: {fastest_tool.tool_name} ({fastest_tool.execution_time:.3f}s)")
            print(f"   Slowest: {slowest_tool.tool_name} ({slowest_tool.execution_time:.3f}s)")
        
        print("\n" + "=" * 60)
    
    async def _generate_json_report(self, 
                                  suite_result: ValidationSuiteResult, 
                                  timestamp: str) -> Path:
        """Generate a JSON validation report."""
        report_data = {
            "metadata": {
                "timestamp": timestamp,
                "generation_time": datetime.now().isoformat(),
                "report_version": "1.0"
            },
            "summary": {
                "total_tools": suite_result.total_tools,
                "passed_tools": suite_result.passed_tools,
                "failed_tools": suite_result.failed_tools,
                "success_rate": (suite_result.passed_tools / suite_result.total_tools * 100) if suite_result.total_tools > 0 else 0,
                "overall_compliance_score": suite_result.overall_compliance_score,
                "execution_time": suite_result.execution_time
            },
            "tools": []
        }
        
        # Add detailed tool results
        for tool_result in suite_result.tool_results:
            tool_data = {
                "name": tool_result.tool_name,
                "passed": tool_result.overall_passed,
                "compliance_score": tool_result.compliance_score,
                "execution_time": tool_result.execution_time,
                "tests": []
            }
            
            for test_result in tool_result.test_results:
                test_data = {
                    "name": test_result.test_name,
                    "passed": test_result.passed,
                    "message": test_result.message,
                    "severity": test_result.severity,
                    "execution_time": test_result.execution_time,
                    "details": test_result.details
                }
                tool_data["tests"].append(test_data)
            
            report_data["tools"].append(tool_data)
        
        # Write to file
        file_path = self.output_dir / f"validation_report_{timestamp}.json"
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"JSON report generated: {file_path}")
        return file_path
    
    async def _generate_html_report(self, 
                                  suite_result: ValidationSuiteResult, 
                                  timestamp: str) -> Path:
        """Generate an HTML validation report."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Validation Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .tool-results {{ margin-bottom: 30px; }}
        .tool {{ margin-bottom: 20px; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; }}
        .tool-header {{ padding: 15px; background: #f8f9fa; display: flex; justify-content: space-between; align-items: center; }}
        .tool-name {{ font-weight: bold; font-size: 1.1em; }}
        .status-pass {{ color: #28a745; }}
        .status-fail {{ color: #dc3545; }}
        .test-results {{ padding: 15px; }}
        .test {{ margin-bottom: 10px; padding: 10px; border-left: 4px solid #ddd; background: #f9f9f9; }}
        .test-pass {{ border-left-color: #28a745; }}
        .test-fail {{ border-left-color: #dc3545; }}
        .test-warning {{ border-left-color: #ffc107; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); transition: width 0.3s; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 MCP Validation Suite Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{suite_result.total_tools}</div>
                <div class="metric-label">Total Tools</div>
            </div>
            <div class="metric">
                <div class="metric-value status-pass">{suite_result.passed_tools}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value status-fail">{suite_result.failed_tools}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{(suite_result.passed_tools/suite_result.total_tools*100):.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{suite_result.overall_compliance_score:.1f}%</div>
                <div class="metric-label">Compliance Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">{suite_result.execution_time:.2f}s</div>
                <div class="metric-label">Execution Time</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {suite_result.overall_compliance_score}%"></div>
        </div>
        
        <div class="tool-results">
            <h2>Tool Validation Results</h2>
"""
        
        # Add tool results
        for tool_result in suite_result.tool_results:
            status_class = "status-pass" if tool_result.overall_passed else "status-fail"
            status_icon = "✅" if tool_result.overall_passed else "❌"
            
            html_content += f"""
            <div class="tool">
                <div class="tool-header">
                    <div class="tool-name">{status_icon} {tool_result.tool_name}</div>
                    <div class="{status_class}">Score: {tool_result.compliance_score:.1f}%</div>
                </div>
                <div class="test-results">
"""
            
            # Add test results
            for test_result in tool_result.test_results:
                test_class = "test-pass" if test_result.passed else "test-fail"
                if test_result.severity == "warning":
                    test_class = "test-warning"
                
                test_icon = "✅" if test_result.passed else "❌"
                if test_result.severity == "warning":
                    test_icon = "⚠️"
                
                html_content += f"""
                    <div class="test {test_class}">
                        <strong>{test_icon} {test_result.test_name}</strong><br>
                        {test_result.message}<br>
                        <small>Execution time: {test_result.execution_time:.3f}s</small>
                    </div>
"""
            
            html_content += """
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        # Write to file
        file_path = self.output_dir / f"validation_report_{timestamp}.html"
        with open(file_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {file_path}")
        return file_path
    
    async def _generate_markdown_report(self, 
                                      suite_result: ValidationSuiteResult, 
                                      timestamp: str) -> Path:
        """Generate a Markdown validation report."""
        md_content = f"""# MCP Validation Suite Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Report ID:** {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| Total Tools | {suite_result.total_tools} |
| Passed | {suite_result.passed_tools} ✅ |
| Failed | {suite_result.failed_tools} ❌ |
| Success Rate | {(suite_result.passed_tools/suite_result.total_tools*100):.1f}% |
| Overall Compliance Score | {suite_result.overall_compliance_score:.1f}% |
| Execution Time | {suite_result.execution_time:.2f}s |

## Tool Results

"""
        
        # Add tool results
        for tool_result in suite_result.tool_results:
            status = "✅ PASSED" if tool_result.overall_passed else "❌ FAILED"
            
            md_content += f"""### {status} {tool_result.tool_name}

**Compliance Score:** {tool_result.compliance_score:.1f}%  
**Execution Time:** {tool_result.execution_time:.3f}s

#### Test Results

"""
            
            for test_result in tool_result.test_results:
                test_status = "✅" if test_result.passed else "❌"
                if test_result.severity == "warning":
                    test_status = "⚠️"
                
                md_content += f"- {test_status} **{test_result.test_name}**: {test_result.message}\n"
            
            md_content += "\n"
        
        # Write to file
        file_path = self.output_dir / f"validation_report_{timestamp}.md"
        with open(file_path, 'w') as f:
            f.write(md_content)
        
        logger.info(f"Markdown report generated: {file_path}")
        return file_path
    
    def generate_summary_stats(self, suite_result: ValidationSuiteResult) -> Dict[str, Any]:
        """Generate summary statistics from validation results."""
        if not suite_result.tool_results:
            return {}
        
        # Test statistics
        all_tests = []
        for tool_result in suite_result.tool_results:
            all_tests.extend(tool_result.test_results)
        
        test_stats = {
            "total_tests": len(all_tests),
            "passed_tests": sum(1 for t in all_tests if t.passed),
            "failed_tests": sum(1 for t in all_tests if not t.passed),
            "test_success_rate": (sum(1 for t in all_tests if t.passed) / len(all_tests) * 100) if all_tests else 0
        }
        
        # Performance statistics
        execution_times = [r.execution_time for r in suite_result.tool_results]
        perf_stats = {
            "avg_tool_time": sum(execution_times) / len(execution_times),
            "min_tool_time": min(execution_times),
            "max_tool_time": max(execution_times),
            "total_execution_time": suite_result.execution_time
        }
        
        # Severity breakdown
        severity_counts = {}
        for test in all_tests:
            severity = test.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "test_statistics": test_stats,
            "performance_statistics": perf_stats,
            "severity_breakdown": severity_counts,
            "compliance_distribution": {
                "excellent": sum(1 for r in suite_result.tool_results if r.compliance_score >= 90),
                "good": sum(1 for r in suite_result.tool_results if 70 <= r.compliance_score < 90),
                "fair": sum(1 for r in suite_result.tool_results if 50 <= r.compliance_score < 70),
                "poor": sum(1 for r in suite_result.tool_results if r.compliance_score < 50)
            }
        }
