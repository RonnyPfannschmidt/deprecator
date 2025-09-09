"""Tests for rich display utilities."""

from __future__ import annotations

from packaging.version import Version
from rich.console import Console
from rich.table import Table

from deprecator._deprecator import Deprecator
from deprecator._rich_display import (
    ACTIVE_WARNINGS,
    ALL_WARNING_TYPES,
    PENDING_WARNINGS,
    _get_warning_type_display_name,
    create_deprecations_table,
    print_deprecations_table,
)
from deprecator._warnings import (
    PerPackagePendingDeprecationWarning,
)
from deprecator.ux import print_deprecations


class TestCreateDeprecationsTable:
    """Test the create_deprecations_table function."""

    def test_empty_deprecator(self) -> None:
        """Test with a deprecator that has no tracked deprecations."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )

        table = create_deprecations_table(deprecator)

        assert isinstance(table, Table)
        assert table.title == "Deprecations for test-package (v1.0.0)"
        assert len(table.rows) == 0

    def test_custom_title(self) -> None:
        """Test with a custom title."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )
        custom_title = "My Custom Deprecations"

        table = create_deprecations_table(deprecator, title=custom_title)

        assert table.title == custom_title

    def test_single_deprecation(self) -> None:
        """Test with a single tracked deprecation."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )

        # Create a deprecation
        warning = deprecator.define(
            "This function is deprecated",
            gone_in="2.0.0",
            warn_in="1.5.0",
        )

        table = create_deprecations_table(deprecator)

        assert len(table.rows) == 1
        # Check that the table was created successfully
        assert table.title == "Deprecations for test-package (v1.0.0)"

    def test_multiple_deprecations_different_types(self) -> None:
        """Test with multiple deprecations of different types."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Pending deprecation (warn_in > current_version)
        pending = deprecator.define(
            "This will be deprecated",
            gone_in="3.0.0",
            warn_in="2.0.0",
        )

        # Active deprecation (warn_in <= current_version < gone_in)
        active = deprecator.define(
            "This is deprecated",
            gone_in="2.0.0",
            warn_in="1.0.0",
        )

        # Expired deprecation (gone_in <= current_version)
        expired = deprecator.define(
            "This should error",
            gone_in="1.0.0",
            warn_in="0.5.0",
        )

        table = create_deprecations_table(deprecator)

        assert len(table.rows) == 3
        # Verify table was created successfully with the right title
        assert "test-package" in table.title

    def test_warning_type_filtering_single_type(self) -> None:
        """Test filtering by a single warning type."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create different types of deprecations
        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        expired = deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Filter for only pending warnings
        table = create_deprecations_table(
            deprecator, warning_types={PerPackagePendingDeprecationWarning}
        )

        assert len(table.rows) == 1

    def test_warning_type_filtering_multiple_types(self) -> None:
        """Test filtering by multiple warning types."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create different types of deprecations
        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        expired = deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        # Filter for active warnings (deprecation + expired)
        table = create_deprecations_table(deprecator, warning_types=ACTIVE_WARNINGS)

        assert len(table.rows) == 2

    def test_no_importable_name(self) -> None:
        """Test deprecation without importable name."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )

        warning = deprecator.define(
            "This has no importable name",
            gone_in="2.0.0",
            warn_in="1.5.0",
            # No importable_name parameter
        )

        table = create_deprecations_table(deprecator)

        assert len(table.rows) == 1


class TestPrintDeprecationsTable:
    """Test the print_deprecations_table function."""

    def test_print_with_custom_console(self) -> None:
        """Test printing with a custom console."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )
        deprecator.define("Test deprecation", gone_in="2.0.0", warn_in="1.5.0")

        # Create a console that captures output
        console = Console(file=None, width=120)

        # This should not raise an exception
        print_deprecations_table(deprecator, console=console)

    def test_print_with_default_console(self) -> None:
        """Test printing with default console."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )
        deprecator.define("Test deprecation", gone_in="2.0.0", warn_in="1.5.0")

        # This should not raise an exception
        print_deprecations_table(deprecator)

    def test_print_with_filtering(self) -> None:
        """Test printing with warning type filtering."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")

        console = Console(file=None, width=120)
        with console.capture() as capture:
            # Should not raise an exception
            print_deprecations_table(
                deprecator, warning_types=PENDING_WARNINGS, console=console
            )

        assert "Pending" in capture.get()


class TestWarningTypeDisplayName:
    """Test the _get_warning_type_display_name function."""

    def test_pending_deprecation_warning(self) -> None:
        """Test display name for pending deprecation warning."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )
        warning = deprecator.define("Test", gone_in="3.0.0", warn_in="2.0.0")

        display_name = _get_warning_type_display_name(warning)
        assert display_name == "Pending"

    def test_deprecation_warning(self) -> None:
        """Test display name for deprecation warning."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )
        warning = deprecator.define("Test", gone_in="2.0.0", warn_in="1.0.0")

        display_name = _get_warning_type_display_name(warning)
        assert display_name == "Warning"

    def test_expired_deprecation_warning(self) -> None:
        """Test display name for expired deprecation warning."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("2.0.0")
        )
        warning = deprecator.define("Test", gone_in="1.5.0", warn_in="1.0.0")

        display_name = _get_warning_type_display_name(warning)
        assert display_name == "Error"


class TestUXPrintDeprecations:
    """Test the public ux.print_deprecations function."""

    def test_print_deprecations_all_types(self) -> None:
        """Test printing all types of deprecations."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create different types of deprecations
        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        expired = deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        console = Console(file=None, width=120)

        # Should not raise an exception
        print_deprecations(deprecator, console=console)

    def test_print_deprecations_pending_only(self) -> None:
        """Test printing only pending deprecations."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create different types of deprecations
        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        expired = deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        console = Console(file=None, width=120)

        # Should not raise an exception
        print_deprecations(
            deprecator, console=console, pending=True, active=False, expired=False
        )

    def test_print_deprecations_active_only(self) -> None:
        """Test printing only active deprecations."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create different types of deprecations
        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        expired = deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        console = Console(file=None, width=120)

        # Should not raise an exception
        print_deprecations(
            deprecator, console=console, pending=False, active=True, expired=False
        )

    def test_print_deprecations_expired_only(self) -> None:
        """Test printing only expired deprecations."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create different types of deprecations
        pending = deprecator.define("Pending", gone_in="3.0.0", warn_in="2.0.0")
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")
        expired = deprecator.define("Expired", gone_in="1.0.0", warn_in="0.5.0")

        console = Console(file=None, width=120)

        # Should not raise an exception
        print_deprecations(
            deprecator, console=console, pending=False, active=False, expired=True
        )

    def test_print_deprecations_none_selected(self) -> None:
        """Test printing when no deprecation types are selected."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.5.0")
        )

        # Create a deprecation
        active = deprecator.define("Active", gone_in="2.0.0", warn_in="1.0.0")

        console = Console(file=None, width=120)

        # Should not raise an exception and should show a message
        print_deprecations(
            deprecator, console=console, pending=False, active=False, expired=False
        )

    def test_print_deprecations_default_console(self) -> None:
        """Test printing with default console."""
        deprecator = Deprecator.for_package(
            "test-package", _package_version=Version("1.0.0")
        )
        deprecator.define("Test deprecation", gone_in="2.0.0", warn_in="1.5.0")

        # Should not raise an exception
        print_deprecations(deprecator)


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
            importable_name="deprecator.test_function",
        )

        table = create_deprecations_table(dep)

        assert isinstance(table, Table)
        assert "deprecator" in table.title
        # Should have at least our test deprecation
        assert len(table.rows) >= 1

    def test_filtering_with_real_package(self) -> None:
        """Test filtering with the actual deprecator package."""
        from deprecator import for_package

        dep = for_package("deprecator")

        # Add deprecations of different types
        dep.define("Pending test", gone_in="999.0.0", warn_in="998.0.0")

        # Test filtering
        pending_table = create_deprecations_table(dep, warning_types=PENDING_WARNINGS)
        all_table = create_deprecations_table(dep, warning_types=ALL_WARNING_TYPES)

        # Pending table should have fewer or equal rows than all table
        assert len(pending_table.rows) <= len(all_table.rows)

    def test_ux_print_deprecations_with_real_package(self) -> None:
        """Test the ux.print_deprecations function with real package."""
        from deprecator import for_package

        dep = for_package("deprecator")

        # Add some test deprecations
        dep.define("UX test deprecation", gone_in="999.0.0", warn_in="998.0.0")

        console = Console(file=None, width=120)
        with console.capture() as capture:
            # Should not raise an exception
            print_deprecations(dep, console=console)

        assert "UX test deprecation" in capture.get()
