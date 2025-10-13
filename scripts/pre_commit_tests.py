#!/usr/bin/env python3
"""
Pre-commit test runner for Faith Dive

This script runs comprehensive tests before code changes are committed,
designed to catch the types of integration issues we've encountered.

Usage:
    poetry run python scripts/pre_commit_tests.py
    
Or set it up as a git hook:
    ln -s ../../scripts/pre_commit_tests.py .git/hooks/pre-commit
"""

import subprocess
import sys
import os
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def run_command(cmd, description, critical=True):
    """Run a command and handle output."""
    print(f"{BLUE}Running: {description}{RESET}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✅ {description} - PASSED{RESET}")
            if result.stdout.strip():
                print("Output:", result.stdout.strip()[:200] + ("..." if len(result.stdout.strip()) > 200 else ""))
            return True
        else:
            print(f"{RED}❌ {description} - FAILED{RESET}")
            print("Error:", result.stderr.strip())
            if result.stdout.strip():
                print("Output:", result.stdout.strip())
                
            if critical:
                return False
            else:
                print(f"{YELLOW}⚠️  Non-critical failure, continuing...{RESET}")
                return True
                
    except Exception as e:
        print(f"{RED}❌ {description} - ERROR: {e}{RESET}")
        return False if critical else True

def main():
    """Run all pre-commit tests."""
    print(f"{BLUE}{'='*60}")
    print(f"🚀 Faith Dive Pre-Commit Test Suite")
    print(f"{'='*60}{RESET}")
    
    tests_passed = 0
    total_tests = 0
    
    # Test categories with their importance
    test_suites = [
        # Critical tests - must pass
        ("Import and Syntax Checks", [
            ("poetry run python -c 'from backend.main import app; print(\"✅ Main app imports successfully\")'", "Main app import test"),
            ("poetry run python -c 'from backend.services.bible_api import bible_api_service; print(\"✅ Bible service imports successfully\")'", "Bible service import test"),
        ], True),
        
        # Core functionality tests - must pass
        ("Verse Reference Parsing Tests", [
            ("poetry run python -c \"from backend.services.bible_api import bible_api_service; s = bible_api_service; assert s._parse_verse_reference('John 3') == ('John', '3', None); print('✅ John 3 parsing')\"", "John 3 parsing regression test"),
            ("poetry run python -c \"from backend.services.bible_api import bible_api_service; s = bible_api_service; assert s._parse_verse_reference('John 3:16') == ('John', '3', '16'); print('✅ John 3:16 parsing')\"", "John 3:16 parsing test"),
            ("poetry run python -c \"from backend.services.bible_api import bible_api_service; s = bible_api_service; assert s._parse_verse_reference('1 John 3') == ('1 John', '3', None); print('✅ 1 John 3 parsing')\"", "1 John 3 parsing test"),
        ], True),
        
        # Search logic tests - must pass  
        ("Search Logic Tests", [
            ("poetry run python -c \"from backend.services.bible_api import bible_api_service; s = bible_api_service; assert s._is_verse_reference('John 3') == True; print('✅ John 3 detection')\"", "Verse reference detection"),
            ("poetry run python -c \"from backend.services.bible_api import bible_api_service; s = bible_api_service; assert s._is_verse_reference('love faith hope') == False; print('✅ Text query detection')\"", "Text query detection"),
        ], True),
        
        # Integration tests - must pass
        ("API Integration Tests", [
            ("poetry run pytest tests/test_verse_reference_integration.py::TestVerseReferenceIntegration::test_verse_reference_parsing_accuracy -v", "Comprehensive parsing tests"),
            ("poetry run pytest tests/test_verse_reference_integration.py::TestVerseReferenceIntegration::test_john_3_does_not_return_1_john_regression -v", "John 3 regression test"),
            ("poetry run pytest tests/test_verse_reference_integration.py::TestApplicationSmokeTests -v", "Application smoke tests"),
        ], True),
        
        # Performance tests - should pass but not critical
        ("Performance Tests", [
            ("poetry run pytest tests/test_verse_reference_integration.py::TestSearchPerformance::test_parsing_performance -v", "Parsing performance test"),
        ], False),
        
        # Full test suite - should pass but not blocking
        ("Full Test Suite", [
            ("poetry run pytest tests/ -x --tb=short -q", "Full test suite"),
        ], False),
    ]
    
    overall_success = True
    
    for suite_name, tests, is_critical in test_suites:
        print(f"\n{BLUE}📋 {suite_name}{RESET}")
        print("-" * 40)
        
        suite_success = True
        for cmd, description in tests:
            total_tests += 1
            success = run_command(cmd, description, is_critical)
            
            if success:
                tests_passed += 1
            elif is_critical:
                suite_success = False
                overall_success = False
            
            print()  # Add spacing between tests
        
        if suite_success:
            print(f"{GREEN}✅ {suite_name} - ALL PASSED{RESET}")
        else:
            print(f"{RED}❌ {suite_name} - SOME FAILURES{RESET}")
            if is_critical:
                print(f"{RED}🚨 Critical test suite failed - blocking commit{RESET}")
    
    # Summary
    print(f"\n{BLUE}{'='*60}")
    print(f"📊 Test Summary")
    print(f"{'='*60}{RESET}")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {tests_passed/total_tests*100:.1f}%")
    
    if overall_success:
        print(f"{GREEN}🎉 All critical tests passed - commit approved!{RESET}")
        return 0
    else:
        print(f"{RED}🚫 Critical tests failed - fix issues before committing{RESET}")
        print(f"{YELLOW}💡 Run individual tests to debug:{RESET}")
        print(f"  poetry run pytest tests/test_verse_reference_integration.py -v")
        print(f"  poetry run python -c 'from backend.main import app'")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)