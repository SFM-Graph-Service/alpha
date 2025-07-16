#!/usr/bin/env python3
"""
Core Module Analysis Script

This script analyzes core modules to identify:
1. Stub methods (methods that just raise NotImplementedError, pass, or return None)
2. Partially implemented methods (methods with TODO comments or incomplete logic)
3. Unused methods (methods that are never called within the codebase)
4. Incomplete methods (methods that don't handle all expected cases)

Usage:
    python core_analysis.py
"""

import ast
import os
import re
import json
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MethodInfo:
    """Information about a method in a module."""
    name: str
    module: str
    file_path: str
    line_number: int
    is_stub: bool = False
    is_partially_implemented: bool = False
    is_unused: bool = False
    is_incomplete: bool = False
    issues: List[str] = None
    docstring: Optional[str] = None
    parameters: List[str] = None
    return_annotation: Optional[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.parameters is None:
            self.parameters = []


class CoreModuleAnalyzer:
    """Analyzes core modules for problematic methods."""
    
    def __init__(self, core_dir: str = "core"):
        self.core_dir = Path(core_dir)
        self.methods: Dict[str, MethodInfo] = {}
        self.method_calls: Set[str] = set()
        self.all_files: List[Path] = []
        
        # Patterns for identifying stub methods
        self.stub_patterns = [
            r'raise\s+NotImplementedError',
            r'^\s*pass\s*$',
            r'^\s*\.\.\.\s*$',
            r'return\s+None\s*$',
            r'^\s*return\s*$'
        ]
        
        # Patterns for identifying partially implemented methods
        self.todo_patterns = [
            r'#\s*TODO',
            r'#\s*FIXME',
            r'#\s*HACK',
            r'#\s*XXX',
            r'#\s*STUB',
            r'#\s*PLACEHOLDER'
        ]
        
        # Patterns for identifying incomplete methods
        self.incomplete_patterns = [
            r'if\s+False:',
            r'if\s+True:',
            r'assert\s+False',
            r'raise\s+Exception\s*\(',
            r'print\s*\(',  # Debug prints often indicate incomplete code
        ]

    def find_all_python_files(self) -> List[Path]:
        """Find all Python files in the core directory."""
        python_files = []
        for root, dirs, files in os.walk(self.core_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    python_files.append(Path(root) / file)
        return python_files

    def parse_file(self, file_path: Path) -> Optional[ast.Module]:
        """Parse a Python file and return AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ast.parse(content)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def extract_method_info(self, node: ast.FunctionDef, file_path: Path, module_name: str) -> MethodInfo:
        """Extract information about a method."""
        method_info = MethodInfo(
            name=node.name,
            module=module_name,
            file_path=str(file_path),
            line_number=node.lineno
        )
        
        # Extract docstring
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            method_info.docstring = node.body[0].value.value
        
        # Extract parameters
        for arg in node.args.args:
            method_info.parameters.append(arg.arg)
        
        # Extract return annotation
        if node.returns:
            method_info.return_annotation = ast.unparse(node.returns)
        
        return method_info

    def analyze_method_body(self, node: ast.FunctionDef, file_path: Path) -> List[str]:
        """Analyze method body for issues."""
        issues = []
        
        # Get the source code for the method
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get method lines
            method_lines = lines[node.lineno - 1:node.end_lineno]
            method_source = ''.join(method_lines)
            
            # Check for stub patterns
            for pattern in self.stub_patterns:
                if re.search(pattern, method_source, re.MULTILINE):
                    issues.append(f"Stub method - matches pattern: {pattern}")
            
            # Check for TODO patterns
            for pattern in self.todo_patterns:
                if re.search(pattern, method_source, re.IGNORECASE):
                    issues.append(f"Partially implemented - contains: {pattern}")
            
            # Check for incomplete patterns
            for pattern in self.incomplete_patterns:
                if re.search(pattern, method_source, re.MULTILINE):
                    issues.append(f"Potentially incomplete - contains: {pattern}")
            
            # Check if method has minimal implementation
            non_comment_lines = [line.strip() for line in method_lines 
                               if line.strip() and not line.strip().startswith('#')]
            
            # Remove def line and docstring
            body_lines = non_comment_lines[1:]  # Skip def line
            if body_lines and body_lines[0].startswith('"""') or body_lines[0].startswith("'''"):
                # Skip docstring lines
                in_docstring = True
                quote_char = body_lines[0][:3]
                i = 0
                while i < len(body_lines) and in_docstring:
                    if quote_char in body_lines[i] and i > 0:
                        in_docstring = False
                    i += 1
                body_lines = body_lines[i:]
            
            # Check if method has very minimal implementation
            if len(body_lines) <= 1:
                if not body_lines or body_lines[0] in ['pass', 'return', 'return None', '...']:
                    issues.append("Minimal implementation - only pass/return/ellipsis")
            
        except Exception as e:
            issues.append(f"Error analyzing method body: {e}")
        
        return issues

    def collect_method_calls(self, tree: ast.Module) -> Set[str]:
        """Collect all method calls in the AST."""
        calls = set()
        
        class CallVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
                self.generic_visit(node)
        
        visitor = CallVisitor()
        visitor.visit(tree)
        return calls

    def analyze_module(self, file_path: Path) -> Dict[str, MethodInfo]:
        """Analyze a single module for problematic methods."""
        module_methods = {}
        
        # Parse the file
        tree = self.parse_file(file_path)
        if not tree:
            return module_methods
        
        # Get module name
        module_name = str(file_path.relative_to(self.core_dir)).replace('/', '.').replace('.py', '')
        
        # Collect method calls for unused method detection
        calls_in_module = self.collect_method_calls(tree)
        self.method_calls.update(calls_in_module)
        
        # Find all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_info = self.extract_method_info(node, file_path, module_name)
                
                # Analyze method body for issues
                issues = self.analyze_method_body(node, file_path)
                method_info.issues = issues
                
                # Set flags based on issues
                method_info.is_stub = any('Stub method' in issue for issue in issues)
                method_info.is_partially_implemented = any('Partially implemented' in issue for issue in issues)
                method_info.is_incomplete = any('Potentially incomplete' in issue for issue in issues)
                
                full_method_name = f"{module_name}.{node.name}"
                module_methods[full_method_name] = method_info
                self.methods[full_method_name] = method_info
        
        return module_methods

    def detect_unused_methods(self):
        """Detect unused methods by checking if they're called anywhere."""
        # Get all method names (without module prefix)
        method_names = set()
        for full_name, method_info in self.methods.items():
            method_names.add(method_info.name)
        
        # Check which methods are never called
        for full_name, method_info in self.methods.items():
            method_name = method_info.name
            
            # Skip magic methods and common special methods
            if (method_name.startswith('__') and method_name.endswith('__')) or \
               method_name in ['setUp', 'tearDown', 'test_', 'main']:
                continue
            
            # Check if method is called anywhere
            if method_name not in self.method_calls:
                method_info.is_unused = True
                method_info.issues.append("Unused method - not called anywhere in codebase")

    def analyze_all_modules(self) -> Dict[str, Dict[str, MethodInfo]]:
        """Analyze all core modules."""
        self.all_files = self.find_all_python_files()
        results = {}
        
        print(f"Found {len(self.all_files)} Python files to analyze...")
        
        # First pass: collect all methods and calls
        for file_path in self.all_files:
            print(f"Analyzing {file_path}...")
            module_methods = self.analyze_module(file_path)
            if module_methods:
                results[str(file_path)] = module_methods
        
        # Second pass: detect unused methods
        print("Detecting unused methods...")
        self.detect_unused_methods()
        
        return results

    def generate_report(self, results: Dict[str, Dict[str, MethodInfo]]) -> str:
        """Generate a comprehensive report."""
        report = []
        report.append("# Core Module Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary statistics
        total_methods = len(self.methods)
        stub_methods = sum(1 for m in self.methods.values() if m.is_stub)
        partial_methods = sum(1 for m in self.methods.values() if m.is_partially_implemented)
        unused_methods = sum(1 for m in self.methods.values() if m.is_unused)
        incomplete_methods = sum(1 for m in self.methods.values() if m.is_incomplete)
        
        report.append(f"## Summary Statistics")
        report.append(f"- Total methods analyzed: {total_methods}")
        report.append(f"- Stub methods: {stub_methods}")
        report.append(f"- Partially implemented methods: {partial_methods}")
        report.append(f"- Unused methods: {unused_methods}")
        report.append(f"- Potentially incomplete methods: {incomplete_methods}")
        report.append("")
        
        # Detailed findings by category
        categories = [
            ("Stub Methods", lambda m: m.is_stub),
            ("Partially Implemented Methods", lambda m: m.is_partially_implemented),
            ("Unused Methods", lambda m: m.is_unused),
            ("Potentially Incomplete Methods", lambda m: m.is_incomplete)
        ]
        
        for category_name, filter_func in categories:
            report.append(f"## {category_name}")
            report.append("-" * len(category_name))
            
            filtered_methods = [m for m in self.methods.values() if filter_func(m)]
            
            if not filtered_methods:
                report.append("No methods found in this category.")
            else:
                for method in sorted(filtered_methods, key=lambda x: (x.module, x.name)):
                    report.append(f"### {method.module}.{method.name}")
                    report.append(f"- **File:** {method.file_path}")
                    report.append(f"- **Line:** {method.line_number}")
                    if method.parameters:
                        report.append(f"- **Parameters:** {', '.join(method.parameters)}")
                    if method.return_annotation:
                        report.append(f"- **Return Type:** {method.return_annotation}")
                    if method.docstring:
                        report.append(f"- **Docstring:** {method.docstring[:100]}...")
                    report.append("- **Issues:**")
                    for issue in method.issues:
                        report.append(f"  - {issue}")
                    report.append("")
            
            report.append("")
        
        # Module-by-module breakdown
        report.append("## Module-by-Module Breakdown")
        report.append("-" * 30)
        
        for file_path, module_methods in results.items():
            module_name = Path(file_path).stem
            report.append(f"### {module_name}")
            
            problematic_methods = [m for m in module_methods.values() 
                                 if m.is_stub or m.is_partially_implemented or 
                                    m.is_unused or m.is_incomplete]
            
            if not problematic_methods:
                report.append("No problematic methods found.")
            else:
                for method in sorted(problematic_methods, key=lambda x: x.name):
                    flags = []
                    if method.is_stub:
                        flags.append("STUB")
                    if method.is_partially_implemented:
                        flags.append("PARTIAL")
                    if method.is_unused:
                        flags.append("UNUSED")
                    if method.is_incomplete:
                        flags.append("INCOMPLETE")
                    
                    report.append(f"- **{method.name}** [{', '.join(flags)}] (Line {method.line_number})")
                    for issue in method.issues:
                        report.append(f"  - {issue}")
            
            report.append("")
        
        return "\n".join(report)

    def save_report(self, report: str, filename: str = "core_analysis_report.md"):
        """Save the report to a file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {filename}")

    def save_json_data(self, filename: str = "core_analysis_data.json"):
        """Save the analysis data as JSON for further processing."""
        data = {}
        for full_name, method_info in self.methods.items():
            data[full_name] = {
                'name': method_info.name,
                'module': method_info.module,
                'file_path': method_info.file_path,
                'line_number': method_info.line_number,
                'is_stub': method_info.is_stub,
                'is_partially_implemented': method_info.is_partially_implemented,
                'is_unused': method_info.is_unused,
                'is_incomplete': method_info.is_incomplete,
                'issues': method_info.issues,
                'docstring': method_info.docstring,
                'parameters': method_info.parameters,
                'return_annotation': method_info.return_annotation
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"JSON data saved to {filename}")


def main():
    """Main function to run the analysis."""
    print("Starting Core Module Analysis...")
    
    analyzer = CoreModuleAnalyzer()
    results = analyzer.analyze_all_modules()
    
    print("\nGenerating report...")
    report = analyzer.generate_report(results)
    
    print("\nSaving report...")
    analyzer.save_report(report)
    analyzer.save_json_data()
    
    print("\nAnalysis complete!")
    print(f"Analyzed {len(analyzer.methods)} methods across {len(results)} modules")


if __name__ == "__main__":
    main()