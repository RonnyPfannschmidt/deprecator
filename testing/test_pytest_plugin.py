"""Tests for the deprecator pytest plugin."""

from __future__ import annotations

import pytest


def test_expired_deprecation_causes_session_failure(pytester: pytest.Pytester) -> None:
    """Test that expired deprecations cause session failure."""
    # Create a test file with an expired deprecation
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_expired_warning():
            deprecator = Deprecator.for_package("test-package", Version("2.0.0"))
            expired_warning = deprecator.define(
                "This is expired",
                warn_in="1.0.0",
                gone_in="1.5.0"
            )
            expired_warning.warn()
    """)

    # Run pytest and check that session fails due to expired deprecation
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)
    # The test itself passes but session should fail due to expired deprecation
    assert result.ret == pytest.ExitCode.TESTS_FAILED


def test_expired_deprecation_with_error_flag_causes_test_failure(
    pytester: pytest.Pytester,
) -> None:
    """Test that expired deprecations cause test failure with --deprecator-error."""
    # Create a test file with an expired deprecation
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_expired_warning():
            deprecator = Deprecator.for_package("test-package", Version("2.0.0"))
            expired_warning = deprecator.define(
                "This is expired",
                warn_in="1.0.0",
                gone_in="1.5.0"
            )
            expired_warning.warn()
    """)

    # Run pytest with --deprecator-error flag
    result = pytester.runpytest("-v", "--deprecator-error")
    result.assert_outcomes(failed=1)
    assert result.ret == pytest.ExitCode.TESTS_FAILED


def test_active_deprecation_does_not_cause_failure(pytester: pytest.Pytester) -> None:
    """Test that active deprecations do not cause failures."""
    # Create a test file with an active deprecation
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_active_warning():
            deprecator = Deprecator.for_package("test-package", Version("1.2.0"))
            active_warning = deprecator.define(
                "This is active",
                warn_in="1.0.0",
                gone_in="2.0.0"
            )
            active_warning.warn()
    """)

    # Run pytest - should pass normally
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK


def test_pending_deprecation_does_not_cause_failure(pytester: pytest.Pytester) -> None:
    """Test that pending deprecations do not cause failures."""
    # Create a test file with a pending deprecation
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_pending_warning():
            deprecator = Deprecator.for_package("test-package", Version("0.5.0"))
            pending_warning = deprecator.define(
                "This is pending",
                warn_in="1.0.0",
                gone_in="2.0.0"
            )
            pending_warning.warn()
    """)

    # Run pytest - should pass normally
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1)
    assert result.ret == pytest.ExitCode.OK


def test_github_annotations_flag_outputs_warnings(pytester: pytest.Pytester) -> None:
    """Test that --deprecator-github-annotations outputs GitHub annotations."""
    # Create a test file with both pending and expired deprecations
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_warnings():
            deprecator = Deprecator.for_package("test-package", Version("1.5.0"))

            # Pending deprecation
            pending_warning = deprecator.define(
                "This is pending",
                warn_in="2.0.0",
                gone_in="3.0.0"
            )
            pending_warning.warn()

            # Expired deprecation
            expired_warning = deprecator.define(
                "This is expired",
                warn_in="1.0.0",
                gone_in="1.2.0"
            )
            expired_warning.warn()
    """)

    # Run pytest with GitHub annotations flag
    result = pytester.runpytest("-v", "--deprecator-github-annotations")

    # Check that GitHub annotations are in the output
    assert "::warning" in result.stdout.str()
    assert "::error" in result.stdout.str()
    assert "This is pending" in result.stdout.str()
    assert "This is expired" in result.stdout.str()


def test_github_annotations_auto_enabled_in_github_actions(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that GitHub annotations are auto-enabled in GitHub Actions CI."""
    # Create a test file with a pending deprecation
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_pending_warning():
            deprecator = Deprecator.for_package("test-package", Version("0.5.0"))
            pending_warning = deprecator.define(
                "This is pending",
                warn_in="1.0.0",
                gone_in="2.0.0"
            )
            pending_warning.warn()
    """)

    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    # Run pytest with GitHub Actions environment variable set
    result = pytester.runpytest_subprocess("-v", "--deprecator-github-annotations")

    # Check that GitHub annotations are in the output
    result.stdout.fnmatch_lines(
        [
            "::warning file=*/test_github_annotations_auto_enabled_in_github_actions.py"
            ",line=11,title=deprecation::This is pending"
        ]
    )


def test_no_github_annotations_without_flag_or_ci(pytester: pytest.Pytester) -> None:
    """Test that no GitHub annotations are output without flag or CI environment."""
    # Create a test file with a pending deprecation
    pytester.makepyfile("""
        from deprecator._deprecator import Deprecator
        from packaging.version import Version

        def test_pending_warning():
            deprecator = Deprecator.for_package("test-package", Version("0.5.0"))
            pending_warning = deprecator.define(
                "This is pending",
                warn_in="1.0.0",
                gone_in="2.0.0"
            )
            pending_warning.warn()
    """)

    # Run pytest without any special flags or CI environment
    result = pytester.runpytest("-v")

    # Check that no GitHub annotations are in the output
    assert "::warning" not in result.stdout.str()
    assert "::error" not in result.stdout.str()
