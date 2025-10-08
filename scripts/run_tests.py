#!/usr/bin/env python3
"""
Faith Dive Test Runner
Comprehensive test runner with different test categories and reporting
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description):
    """Run a command and handle output."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def run_unit_tests():
    """Run unit tests only."""
    cmd = [
        "poetry", "run", "pytest", 
        "-m", "unit",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running Unit Tests")


def run_integration_tests():
    """Run integration tests only."""
    cmd = [
        "poetry", "run", "pytest", 
        "-m", "integration",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running Integration Tests")


def run_api_tests():
    """Run API tests only."""
    cmd = [
        "poetry", "run", "pytest", 
        "-m", "api",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running API Tests")


def run_performance_tests():
    """Run performance tests only."""
    cmd = [
        "poetry", "run", "pytest", 
        "-m", "performance",
        "--tb=short",
        "-v",
        "--durations=20"
    ]
    return run_command(cmd, "Running Performance Tests")


def run_all_tests():
    """Run all tests with coverage."""
    cmd = [
        "poetry", "run", "pytest",
        "--cov=backend",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running All Tests with Coverage")


def run_quick_tests():
    """Run quick tests (excluding slow and performance tests)."""
    cmd = [
        "poetry", "run", "pytest",
        "-m", "not slow and not performance",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running Quick Tests")


def run_parallel_tests():
    """Run tests in parallel using pytest-xdist."""
    cmd = [
        "poetry", "run", "pytest",
        "-n", "auto",
        "--tb=short",
        "-v"
    ]
    return run_command(cmd, "Running Tests in Parallel")


def run_benchmark_tests():
    """Run benchmark tests only."""
    cmd = [
        "poetry", "run", "pytest", 
        "-m", "benchmark",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-columns=min,max,mean,stddev,rounds,iterations",
        "-v"
    ]
    return run_command(cmd, "Running Benchmark Tests")


def generate_coverage_report():
    """Generate detailed coverage report."""
    print(f"\n{'='*60}")
    print(f"📊 Generating Coverage Report")
    print(f"{'='*60}")
    
    # Run tests with coverage
    cmd = [
        "poetry", "run", "pytest",
        "--cov=backend",
        "--cov-report=html:htmlcov",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing",
        "--cov-fail-under=85",
        "--tb=no",
        "-q"
    ]
    
    success = run_command(cmd, "Generating Coverage")
    
    if success:
        html_report = project_root / "htmlcov" / "index.html"
        if html_report.exists():
            print(f"\n📈 HTML Coverage Report: {html_report}")
        
        xml_report = project_root / "coverage.xml"
        if xml_report.exists():
            print(f"📈 XML Coverage Report: {xml_report}")
    
    return success


def lint_and_format():
    """Run linting and formatting checks."""
    success = True
    
    # Run flake8 if available
    try:
        cmd = ["poetry", "run", "flake8", "backend", "tests"]
        success &= run_command(cmd, "Running Flake8 Linting")
    except:
        print("⚠️  Flake8 not available, skipping linting")
    
    # Run mypy if available
    try:
        cmd = ["poetry", "run", "mypy", "backend"]
        success &= run_command(cmd, "Running MyPy Type Checking")
    except:
        print("⚠️  MyPy not available, skipping type checking")
    
    return success


def install_dependencies():
    """Install test dependencies."""
    cmd = ["poetry", "install", "--with", "dev"]
    return run_command(cmd, "Installing Dependencies")


def main():
    parser = argparse.ArgumentParser(
        description="Faith Dive Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py --all              # Run all tests
  python scripts/run_tests.py --quick            # Run quick tests only
  python scripts/run_tests.py --unit             # Run unit tests only
  python scripts/run_tests.py --api              # Run API tests only
  python scripts/run_tests.py --performance      # Run performance tests
  python scripts/run_tests.py --coverage         # Generate coverage report
  python scripts/run_tests.py --parallel         # Run tests in parallel
  python scripts/run_tests.py --benchmark        # Run benchmark tests
  python scripts/run_tests.py --install          # Install dependencies
        """
    )
    
    parser.add_argument("--all", action="store_true", help="Run all tests with coverage")
    parser.add_argument("--quick", action="store_true", help="Run quick tests (no slow/performance)")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark tests only")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--lint", action="store_true", help="Run linting and formatting")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🧪 Faith Dive Test Runner")
    print(f"📁 Project root: {project_root}")
    
    success = True
    
    if args.install:
        success &= install_dependencies()
    
    if args.lint:
        success &= lint_and_format()
    
    if args.unit:
        success &= run_unit_tests()
    elif args.integration:
        success &= run_integration_tests()
    elif args.api:
        success &= run_api_tests()
    elif args.performance:
        success &= run_performance_tests()
    elif args.benchmark:
        success &= run_benchmark_tests()
    elif args.parallel:
        success &= run_parallel_tests()
    elif args.coverage:
        success &= generate_coverage_report()
    elif args.quick:
        success &= run_quick_tests()
    elif args.all:
        success &= run_all_tests()
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()