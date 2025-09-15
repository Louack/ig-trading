#!/usr/bin/env python3
"""
Simple test runner script for IG Trading API tests.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner."""
    print("🧪 IG Trading API Test Runner")
    print("=" * 60)

    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Test commands to run
    test_commands = [
        ("python -m pytest api_gateway/tests/unit/ -v --tb=short", "Unit Tests"),
        (
            "python -m pytest api_gateway/tests/unit/ --cov=api_gateway --cov-report=term-missing",
            "Unit Tests with Coverage",
        ),
        (
            "python -m pytest api_gateway/tests/unit/test_validators.py -v",
            "Validator Tests Only",
        ),
        (
            "python -m pytest api_gateway/tests/unit/test_error_handling.py -v",
            "Error Handling Tests Only",
        ),
        (
            "python -m pytest api_gateway/tests/unit/test_rest_client.py -v",
            "REST Client Tests Only",
        ),
        ("python -m pytest api_gateway/tests/unit/test_auth.py -v", "Auth Tests Only"),
    ]

    success_count = 0
    total_count = len(test_commands)

    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"❌ {description} failed")

    print(f"\n{'=' * 60}")
    print(f"Test Summary: {success_count}/{total_count} test suites passed")
    print(f"{'=' * 60}")

    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
