"""Implementation of the 'deprecator init' command."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Confirm

RED_CROSS = "[red bold]:cross_mark:"
GREEN_CHECK = "[green bold]:heavy_check_mark:"
YELLOW_WARN = "[yellow bold]:warning:"


def read_pyproject_toml(path: Path) -> dict[str, Any] | None:
    """Read and parse pyproject.toml file.

    Args:
        path: Path to the pyproject.toml file

    Returns:
        Parsed pyproject.toml data or None if not found/invalid
    """
    if not path.exists():
        return None

    try:
        if sys.version_info >= (3, 11):
            import tomllib

            with open(path, "rb") as f:
                data: dict[str, Any] = tomllib.load(f)
                return data
        else:
            try:
                import tomli as tomllib
            except ImportError:
                # tomli not available, return None to indicate we can't parse
                return None

            with open(path, "rb") as f:
                data: dict[str, Any] = tomllib.load(f)
                return data
    except Exception:
        return None


def get_package_info(pyproject_data: dict[str, Any]) -> tuple[str, str] | None:
    """Extract package name and import name from pyproject.toml.

    Args:
        pyproject_data: Parsed pyproject.toml data

    Returns:
        Tuple of (package_name, import_name) or None if not found
    """
    project = pyproject_data.get("project", {})
    package_name: str | None = project.get("name")

    if not package_name:
        return None

    # Try to determine the import name
    # First check tool.setuptools.packages
    tool: dict[str, Any] = pyproject_data.get("tool", {})
    setuptools: dict[str, Any] = tool.get("setuptools", {})
    packages: list[str] | None | object = setuptools.get("packages")

    if packages and isinstance(packages, list) and packages:
        # Use the first package as the import name
        import_name = packages[0]
        assert isinstance(import_name, str)
    else:
        # Fall back to package name, replacing hyphens with underscores
        import_name = package_name.replace("-", "_")

    return package_name, import_name


def create_deprecations_module(
    import_name: str, package_name: str, target_path: Path
) -> str:
    """Create the _deprecations.py module content.

    Args:
        import_name: The Python import name for the package
        package_name: The distribution package name
        target_path: Path where the module will be created

    Returns:
        The generated module content
    """
    content = f'''"""Deprecation definitions for {package_name}."""

from __future__ import annotations

from deprecator import for_package

# Create the deprecator instance for this package
deprecator = for_package(__package__)

# Example deprecation definition
# Replace this with your actual deprecations
EXAMPLE_DEPRECATION = deprecator.define(
    "This is an example deprecation - replace with your actual deprecation message",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

# You can use deprecations as decorators:
# @EXAMPLE_DEPRECATION.apply
# def deprecated_function():
#     pass

# Or emit warnings manually:
# def some_function():
#     EXAMPLE_DEPRECATION.warn()
'''
    return content


def add_entrypoint_to_pyproject(
    pyproject_path: Path, package_name: str, import_name: str
) -> bool:
    """Add deprecator entrypoint to pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml
        package_name: The distribution package name
        import_name: The Python import name

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read existing content
        with open(pyproject_path) as f:
            content = f.read()

        # Check if entrypoint already exists
        if "deprecator.deprecator" in content:
            return True  # Already configured

        # Find where to add the entrypoint
        entrypoint_section = f'''
[project.entry-points."deprecator.deprecator"]
{package_name} = "{import_name}._deprecations:deprecator"
'''

        # Check if there's already a [project.entry-points section
        if "[project.entry-points" in content:
            # Add after the last entry-points section
            lines = content.splitlines()
            insert_index = -1
            for i, line in enumerate(lines):
                if line.startswith("[project.entry-points"):
                    # Find the end of this section
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith("[") or j == len(lines) - 1:
                            insert_index = j
                            break

            if insert_index > 0:
                lines.insert(insert_index, entrypoint_section.strip())
                content = "\n".join(lines)
        else:
            # Add at the end of file
            content = content.rstrip() + "\n" + entrypoint_section

        # Write updated content
        with open(pyproject_path, "w") as f:
            f.write(content)

        return True
    except Exception:
        return False


def init_deprecator(console: Console) -> None:  # noqa: C901
    """Initialize deprecator for the current project.

    Args:
        console: Rich console for output
    """
    # Find pyproject.toml
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        console.print(f"{RED_CROSS} No pyproject.toml found in current directory")
        console.print("Please run this command from your project root directory")
        sys.exit(2)

    # Read pyproject.toml
    pyproject_data = read_pyproject_toml(pyproject_path)
    if not pyproject_data:
        console.print(f"{RED_CROSS} Failed to parse pyproject.toml")
        if sys.version_info < (3, 11):
            console.print(
                "For Python < 3.11, install with: pip install 'deprecator[cli]'"
            )
        sys.exit(2)

    # Extract package info
    package_info = get_package_info(pyproject_data)
    if not package_info:
        console.print(
            f"{RED_CROSS} Could not determine package name from pyproject.toml"
        )
        console.print(
            "Ensure your pyproject.toml has a [project] section with 'name' field"
        )
        sys.exit(2)

    package_name, import_name = package_info

    console.print(f"[bold]Initializing deprecator for package:[/bold] {package_name}")
    console.print(f"[bold]Import name:[/bold] {import_name}")
    console.print()

    # Check if package directory exists
    package_dir = Path(import_name)
    if not package_dir.exists() or not package_dir.is_dir():
        # Try common source layout
        src_package_dir = Path("src") / import_name
        if src_package_dir.exists() and src_package_dir.is_dir():
            package_dir = src_package_dir
        else:
            console.print(f"{RED_CROSS} Package directory '{import_name}' not found")
            console.print(
                "Please ensure your package structure matches the import name"
            )
            sys.exit(2)

    # Check if _deprecations.py already exists
    deprecations_file = package_dir / "_deprecations.py"
    if deprecations_file.exists():
        console.print(f"{YELLOW_WARN} File {deprecations_file} already exists")
        if not Confirm.ask("Do you want to overwrite it?", default=False):
            console.print("Skipping _deprecations.py creation")
        else:
            # Create the module
            content = create_deprecations_module(
                import_name, package_name, deprecations_file
            )
            deprecations_file.write_text(content)
            console.print(f"{GREEN_CHECK} Updated {deprecations_file}")
    else:
        # Create the module
        content = create_deprecations_module(
            import_name, package_name, deprecations_file
        )
        deprecations_file.write_text(content)
        console.print(f"{GREEN_CHECK} Created {deprecations_file}")

    # Add entrypoint to pyproject.toml
    console.print()
    console.print("[bold]Configuring entrypoint in pyproject.toml...[/bold]")

    if add_entrypoint_to_pyproject(pyproject_path, package_name, import_name):
        console.print(f"{GREEN_CHECK} Added deprecator entrypoint to pyproject.toml")
    else:
        console.print(f"{YELLOW_WARN} Failed to add entrypoint automatically")
        console.print("Please add the following to your pyproject.toml:")
        console.print()
        console.print('[project.entry-points."deprecator.deprecator"]')
        console.print(f'{package_name} = "{import_name}._deprecations:deprecator"')

    # Check for pytest and suggest plugin configuration
    if "pytest" in pyproject_data.get("tool", {}):
        console.print()
        console.print("[bold]Pytest detected![/bold]")
        console.print("To enable deprecator's pytest plugin, add to your test command:")
        console.print(
            "  pytest --deprecator-error  # Treat expired deprecations as errors"
        )
        console.print(
            "  pytest --deprecator-github-annotations  # GitHub Actions output"
        )

    console.print()
    console.print(
        f"{GREEN_CHECK} [bold green]Deprecator initialization complete![/bold green]"
    )
    console.print()
    console.print("Next steps:")
    console.print("1. Edit _deprecations.py to define your deprecations")
    console.print("2. Import and use deprecations in your code:")
    console.print("   from ._deprecations import EXAMPLE_DEPRECATION")
    console.print("3. Run 'deprecator show' to view all deprecations")
    console.print("4. Run 'deprecator validate-package' to validate configuration")
