"""Integration tests for documentation examples.

This module verifies that the example code in docs/examples/ works correctly.
"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def examples_dir() -> Path:
    """Get the path to the docs/examples directory."""
    return Path(__file__).parent.parent / "docs" / "examples"


def run_python(
    *args: str,
    code: str | None = None,
    cwd: Path | None = None,
    expect_success: bool = True,
    capture_warnings: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run Python code or module with common settings.

    Args:
        *args: Command-line arguments to pass to Python
        code: Python code to run with -c (mutually exclusive with module args)
        cwd: Working directory for the subprocess
        expect_success: Whether to assert the process succeeds (returncode == 0)
        capture_warnings: Whether to include -W always flag

    Returns:
        The completed process result

    Raises:
        AssertionError: If expect_success=True and the process fails
    """
    cmd = [sys.executable]

    if capture_warnings:
        cmd.extend(["-W", "always"])

    if code is not None:
        cmd.extend(["-c", code])
    else:
        cmd.extend(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if expect_success:
        assert result.returncode == 0, (
            f"Command failed with exit code {result.returncode}:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    return result


class TestExampleTests:
    """Run the existing test files in docs/examples/."""

    def test_test_deprecation_py(self, examples_dir: Path) -> None:
        """Run test_deprecation.py which tests basic_deprecation.py."""
        result = run_python(
            "-m",
            "pytest",
            "test_deprecation.py",
            "-xvs",
            cwd=examples_dir,
            capture_warnings=False,
        )
        assert "2 passed" in result.stdout

    def test_complete_test_py(self, examples_dir: Path) -> None:
        """Run complete_test.py which tests decorator_usage.py and package_setup.py."""
        result = run_python(
            "-m",
            "pytest",
            "complete_test.py",
            "-xvs",
            cwd=examples_dir,
            capture_warnings=False,
        )
        assert "2 passed" in result.stdout


class TestMissingExamples:
    """Test the examples that don't have dedicated test files."""

    def test_manual_warning_example(self, examples_dir: Path) -> None:
        """Test manual_warning.py by running it with different parameters."""
        # Test with old logic (should warn)
        result = run_python(
            code="""
from manual_warning import complex_deprecation
result = complex_deprecation(use_old_logic=True)
assert result == "old result"
""",
            cwd=examples_dir,
        )
        assert "old_feature is deprecated" in result.stderr

        # Test with new logic (should not warn)
        result = run_python(
            code="""
from manual_warning import complex_deprecation
result = complex_deprecation(use_old_logic=False)
assert result == "new result"
""",
            cwd=examples_dir,
        )
        assert "old_feature is deprecated" not in result.stderr

    def test_class_deprecation_example(self, examples_dir: Path) -> None:
        """Test class_deprecation.py by instantiating the classes."""
        # Test LegacyProcessor (should warn)
        result = run_python(
            code="""
from class_deprecation import LegacyProcessor
obj = LegacyProcessor()
""",
            cwd=examples_dir,
        )
        assert "old_feature is deprecated" in result.stderr

        # Test ModernProcessor (should not warn)
        result = run_python(
            code="""
from class_deprecation import ModernProcessor
obj = ModernProcessor()
""",
            cwd=examples_dir,
        )
        assert "old_feature is deprecated" not in result.stderr


class TestPackageSetup:
    """Test that package_setup.py works correctly."""

    def test_package_setup_defines_deprecations(self, examples_dir: Path) -> None:
        """Verify package_setup.py defines the expected deprecations."""
        result = run_python(
            code="""
from package_setup import OLD_FEATURE_DEPRECATION, PROCESS_DATA_DEPRECATION
expected1 = "old_feature is deprecated, use new_feature instead"
expected2 = "process_data() is deprecated, use transform_data() instead"
assert str(OLD_FEATURE_DEPRECATION) == expected1
assert str(PROCESS_DATA_DEPRECATION) == expected2
print("Package setup verified")
""",
            cwd=examples_dir,
            capture_warnings=False,
        )
        assert "Package setup verified" in result.stdout
