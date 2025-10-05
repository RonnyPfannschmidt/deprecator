"""Tests for rich display utilities."""

from __future__ import annotations

import pytest
from conftest import (
    get_test_deprecator,
    run_with_console_capture,
)
from rich.table import Table

from deprecator._rich_display import (
    _get_warning_type_display_name,
    create_deprecations_table,
    print_deprecations_table,
)
from deprecator.ux import get_warning_types, print_deprecations


class TestCreateDeprecationsTable:
    """Test the create_deprecations_table function."""

    def test_empty_deprecator(self) -> None:
        """Test with a deprecator that has no tracked deprecations."""
        deprecator = get_test_deprecator("test-package", "1.0.0")

        table = create_deprecations_table(deprecator)

        assert isinstance(table, Table)
        assert table.title == "Deprecations for test-package (v1.0.0)"
        assert len(table.rows) == 0

    def test_custom_title(self) -> None:
        """Test with a custom title."""
        deprecator = get_test_deprecator("test-package", "1.0.0")
        custom_title = "My Custom Deprecations"

        table = create_deprecations_table(deprecator, title=custom_title)

        assert table.title == custom_title

    def test_single_deprecation(self) -> None:
        """Test with a single tracked deprecation."""
        deprecator = get_test_deprecator("test-package", "1.0.0")

        # Create a deprecation
        deprecator.define(
            "This function is deprecated", gone_in="2.0.0", warn_in="1.5.0"
        )

        table = create_deprecations_table(deprecator)

        assert len(table.rows) == 0  # no active deprecations
        # Check that the table was created successfully
        assert table.title == "Deprecations for test-package (v1.0.0)"

    def test_multiple_deprecations_different_types(self) -> None:
        """Test with multiple deprecations of different types."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        # Pending deprecation (warn_in > current_version)
        deprecator.define(
            "This will be deprecated",
            gone_in="3.0.0",
            warn_in="2.0.0",
        )

        # Active deprecation (warn_in <= current_version < gone_in)
        deprecator.define(
            "This is deprecated",
            gone_in="2.0.0",
            warn_in="1.0.0",
        )

        # Expired deprecation (gone_in <= current_version)
        deprecator.define(
            "This should error",
            gone_in="1.0.0",
            warn_in="0.5.0",
        )

        table = create_deprecations_table(deprecator)

        assert len(table.rows) == 2
        # Verify table was created successfully with the right title
        assert table.title is not None and "test-package" in str(table.title)

    def test_warning_type_filtering_single_type(self) -> None:
        """Test filtering by a single warning type."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        # Create different types of deprecations
        deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Filter for only pending warnings
        table = create_deprecations_table(
            deprecator,
            warning_types=get_warning_types(pending=True, active=False, expired=False),
        )

        assert len(table.rows) == 1

    def test_warning_type_filtering_multiple_types(self) -> None:
        """Test filtering by multiple warning types."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        # Create different types of deprecations
        deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Filter for active warnings (deprecation + expired)
        table = create_deprecations_table(
            deprecator,
            warning_types=get_warning_types(pending=False, active=True, expired=True),
        )

        assert len(table.rows) == 2

    def test_no_importable_name(self) -> None:
        """Test deprecation (importable names no longer tracked)."""
        deprecator = get_test_deprecator("test-package", "1.6.0")

        deprecator.define(
            "This deprecation works fine",
            gone_in="2.0.0",
            warn_in="1.5.0",
        )

        table = create_deprecations_table(deprecator)

        assert len(table.rows) == 1


class TestPrintDeprecationsTable:
    """Test the print_deprecations_table function."""

    def test_print_with_custom_console(self) -> None:
        """Test printing with a custom console."""
        deprecator = get_test_deprecator("test-package", "1.0.0")
        deprecator.define("Test deprecation", gone_in="2.0.0", warn_in="1.5.0")

        # Should not raise an exception and should produce output
        output = run_with_console_capture(print_deprecations_table, deprecator)
        assert "test-package" in output

    def test_print_with_default_console(self) -> None:
        """Test printing with default console."""
        deprecator = get_test_deprecator("test-package", "1.0.0")
        deprecator.define("Test deprecation", gone_in="2.0.0", warn_in="1.5.0")

        # Should not raise an exception and should produce output
        output = run_with_console_capture(print_deprecations_table, deprecator)
        assert "test-package" in output

    def test_print_with_filtering(self) -> None:
        """Test printing with warning type filtering."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")

        output = run_with_console_capture(
            print_deprecations_table,
            deprecator,
            warning_types=get_warning_types(pending=True, active=False, expired=False),
        )
        assert "Pending" in output


class TestWarningTypeDisplayName:
    """Test the _get_warning_type_display_name function."""

    def test_pending_deprecation_warning(self) -> None:
        """Test display name for pending deprecation warning."""
        deprecator = get_test_deprecator("test-package", "1.0.0")
        warning = deprecator.define("Test", gone_in="3.0.0", warn_in="2.0.0")

        display_name = _get_warning_type_display_name(warning)
        assert display_name == "Pending"

    def test_deprecation_warning(self) -> None:
        """Test display name for deprecation warning."""
        deprecator = get_test_deprecator("test-package", "1.5.0")
        warning = deprecator.define("Test", gone_in="2.0.0", warn_in="1.0.0")

        display_name = _get_warning_type_display_name(warning)
        assert display_name == "Warning"

    def test_expired_deprecation_warning(self) -> None:
        """Test display name for expired deprecation warning."""
        deprecator = get_test_deprecator("test-package", "2.0.0")
        warning = deprecator.define("Test", gone_in="1.5.0", warn_in="1.0.0")

        display_name = _get_warning_type_display_name(warning)
        assert display_name == "Error"


class TestUXPrintDeprecations:
    """Test the public ux.print_deprecations function."""

    def test_print_deprecations_all_types(self) -> None:
        """Test printing all types of deprecations."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        # Create different types of deprecations
        deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Should not raise an exception and should show active and expired types
        output = run_with_console_capture(print_deprecations, deprecator)
        assert "test-package" in output
        assert "Active" in output  # This should be shown as Warning
        assert "Expired" in output  # This should be shown as Error

    def test_print_deprecations_pending_only(self) -> None:
        """Test printing only pending deprecations."""
        deprecator = get_test_deprecator("test-package", "0.5.0")  # Earlier version

        # Create different types of deprecations
        deprecator.define("Pending", gone_in="3.0.0", warn_in="1.0.0")  # Future warning
        deprecator.define("Active", gone_in="2.0.0", warn_in="0.1.0")  # Current warning
        deprecator.define("Expired", gone_in="0.3.0", warn_in="0.1.0")  # Past expiry

        # Should show only pending deprecations
        output = run_with_console_capture(
            print_deprecations, deprecator, pending=True, active=False, expired=False
        )
        assert "Pending" in output

    def test_print_deprecations_active_only(self) -> None:
        """Test printing only active deprecations."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        # Create different types of deprecations
        deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Should show only active deprecations
        output = run_with_console_capture(
            print_deprecations, deprecator, pending=False, active=True, expired=False
        )
        assert "Active" in output

    def test_print_deprecations_expired_only(self) -> None:
        """Test printing only expired deprecations."""
        deprecator = get_test_deprecator("test-package", "1.5.0")

        # Create different types of deprecations
        deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Should show only expired deprecations
        output = run_with_console_capture(
            print_deprecations, deprecator, pending=False, active=False, expired=True
        )
        assert "Expired" in output

    def test_print_deprecations_none_selected(self) -> None:
        """Test printing when no deprecation types are selected."""

        with pytest.raises(TypeError):
            get_warning_types(pending=False, active=False, expired=False)

    def test_print_deprecations_default_console(self) -> None:
        """Test printing with default console."""
        deprecator = get_test_deprecator("test-package", "1.0.0")
        deprecator.define("Test deprecation", gone_in="2.0.0", warn_in="1.5.0")

        # Should not raise an exception and should produce output
        output = run_with_console_capture(print_deprecations, deprecator)
        assert "test-package" in output


class TestIntegrationWithRealPackage:
    """Integration tests using the actual deprecator package."""

    def test_with_deprecator_package(self) -> None:
        """Test with the actual deprecator package."""
        from deprecator import for_package

        # Get deprecator for the actual package
        dep = for_package("deprecator")

        # Add some test deprecations
        dep.define(
            "Integration test deprecation",
            gone_in="999.0.0",
            warn_in="998.0.0",
        )

        table = create_deprecations_table(
            dep,
            warning_types=get_warning_types(pending=True, active=True, expired=True),
        )

        assert isinstance(table, Table)
        assert table.title is not None and "deprecator" in str(table.title)
        # Should have at least our test deprecation
        assert len(table.rows) >= 1

    def test_filtering_with_real_package(self) -> None:
        """Test filtering with the actual deprecator package."""
        from deprecator import for_package

        dep = for_package("deprecator")

        # Add deprecations of different types
        dep.define("Pending test", gone_in="999.0.0", warn_in="998.0.0")

        # Test filtering
        pending_table = create_deprecations_table(
            dep,
            warning_types=get_warning_types(pending=True, active=False, expired=False),
        )
        all_table = create_deprecations_table(
            dep,
            warning_types=get_warning_types(pending=True, active=True, expired=True),
        )

        # Pending table should have fewer or equal rows than all table
        assert len(pending_table.rows) <= len(all_table.rows)

    def test_ux_print_deprecations_with_real_package(self) -> None:
        """Test the ux.print_deprecations function with real package."""
        from deprecator import for_package

        dep = for_package("deprecator")

        # Add some test deprecations
        dep.define("UX test deprecation", gone_in="999.0.0", warn_in="998.0.0")

        output = run_with_console_capture(print_deprecations, dep, pending=True)
        print(output)  # Keep debug print for now
        assert "UX test deprecation" in output, "not found, see print output"
