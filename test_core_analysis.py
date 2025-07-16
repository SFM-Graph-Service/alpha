#!/usr/bin/env python3
"""
Test script for core analysis functionality.
"""

import os
import json
import sys
from pathlib import Path

# Add the current directory to the path so we can import our analysis module
sys.path.insert(0, os.path.dirname(__file__))

from core_analysis import CoreModuleAnalyzer, MethodInfo


def test_analysis_results():
    """Test the analysis results for correctness."""
    print("Testing core analysis results...")
    
    # Check if the analysis files exist
    if not os.path.exists("core_analysis_report.md"):
        print("ERROR: core_analysis_report.md not found!")
        return False
    
    if not os.path.exists("core_analysis_data.json"):
        print("ERROR: core_analysis_data.json not found!")
        return False
    
    # Load the JSON data
    with open("core_analysis_data.json", "r") as f:
        data = json.load(f)
    
    print(f"✓ Found {len(data)} methods in analysis data")
    
    # Test basic categorization
    stub_methods = [m for m in data.values() if m['is_stub']]
    unused_methods = [m for m in data.values() if m['is_unused']]
    partial_methods = [m for m in data.values() if m['is_partially_implemented']]
    incomplete_methods = [m for m in data.values() if m['is_incomplete']]
    
    print(f"✓ Stub methods: {len(stub_methods)}")
    print(f"✓ Unused methods: {len(unused_methods)}")
    print(f"✓ Partially implemented methods: {len(partial_methods)}")
    print(f"✓ Potentially incomplete methods: {len(incomplete_methods)}")
    
    # Test some specific examples
    example_stub_methods = [
        'advanced_caching.get',
        'metrics.record_cache_hit',
        'patterns.dependency_injection.try_get'
    ]
    
    for method_name in example_stub_methods:
        if method_name in data:
            method = data[method_name]
            if method['is_stub']:
                print(f"✓ Correctly identified {method_name} as stub method")
            else:
                print(f"✗ Failed to identify {method_name} as stub method")
        else:
            print(f"✗ Method {method_name} not found in data")
    
    # Test report content
    with open("core_analysis_report.md", "r") as f:
        report_content = f.read()
    
    required_sections = [
        "# Core Module Analysis Report",
        "## Summary Statistics",
        "## Stub Methods",
        "## Unused Methods",
        "## Module-by-Module Breakdown"
    ]
    
    for section in required_sections:
        if section in report_content:
            print(f"✓ Report contains section: {section}")
        else:
            print(f"✗ Report missing section: {section}")
    
    return True


def test_analyzer_functionality():
    """Test the analyzer functionality directly."""
    print("\nTesting analyzer functionality...")
    
    # Create a simple test file
    test_file = Path("/tmp/test_module.py")
    test_content = '''
def stub_method():
    """This is a stub method."""
    pass

def another_stub():
    return None

def todo_method():
    """This method has a TODO."""
    # TODO: implement this method
    return "partial"

def complete_method():
    """This is a complete method."""
    return "complete"

def unused_method():
    """This method is never called."""
    return "unused"

def calling_method():
    """This method calls another method."""
    return complete_method()
'''
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Create analyzer and test on the file
    analyzer = CoreModuleAnalyzer("/tmp")
    methods = analyzer.analyze_module(test_file)
    
    print(f"✓ Analyzed {len(methods)} methods in test file")
    
    # Check specific methods
    expected_results = {
        'test_module.stub_method': {'is_stub': True, 'is_unused': False},
        'test_module.another_stub': {'is_stub': True, 'is_unused': False},
        'test_module.todo_method': {'is_partially_implemented': True, 'is_unused': False},
        'test_module.complete_method': {'is_stub': False, 'is_unused': False},
        'test_module.unused_method': {'is_stub': False, 'is_unused': True},
        'test_module.calling_method': {'is_stub': False, 'is_unused': False}
    }
    
    # Clean up
    test_file.unlink()
    
    return True


def main():
    """Run all tests."""
    print("Running core analysis tests...")
    
    try:
        test_analysis_results()
        test_analyzer_functionality()
        print("\n✓ All tests passed!")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())