"""Test the 'deprecator init' command functionality."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from rich.console import Console

from deprecator._init_command import (
    add_entrypoint_to_pyproject,
    create_deprecations_module,
    get_package_info,
    init_deprecator,
    read_pyproject_toml,
)


def test_read_pyproject_toml(tmp_path: Path) -> None:
    """Test reading and parsing pyproject.toml."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"
version = "0.1.0"

[tool.setuptools]
packages = ["test_package"]
""")

    data = read_pyproject_toml(pyproject_path)
    assert data is not None
    assert data["project"]["name"] == "test-package"
    assert data["project"]["version"] == "0.1.0"


def test_read_pyproject_toml_not_found(tmp_path: Path) -> None:
    """Test reading non-existent pyproject.toml."""
    non_existent = tmp_path / "missing.toml"
    data = read_pyproject_toml(non_existent)
    assert data is None


def test_get_package_info(tmp_path: Path) -> None:
    """Test extracting package info from pyproject data."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"
version = "0.1.0"

[tool.setuptools]
packages = ["test_package"]
""")

    data = read_pyproject_toml(pyproject_path)
    assert data is not None

    package_info = get_package_info(data)
    assert package_info is not None
    package_name, import_name = package_info
    assert package_name == "test-package"
    assert import_name == "test_package"


def test_get_package_info_hyphenated_name(tmp_path: Path) -> None:
    """Test package info extraction with hyphenated package name."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "my-hyphenated-package"
""")

    data = read_pyproject_toml(pyproject)
    assert data is not None

    package_info = get_package_info(data)
    assert package_info is not None
    package_name, import_name = package_info
    assert package_name == "my-hyphenated-package"
    assert import_name == "my_hyphenated_package"


def test_create_deprecations_module() -> None:
    """Test creating the _deprecations.py module content."""
    content = create_deprecations_module(
        import_name="test_package",
        package_name="test-package",
        target_path=Path("/tmp/test"),
    )

    assert "from deprecator import for_package" in content
    assert "deprecator = for_package(__package__)" in content
    assert "EXAMPLE_DEPRECATION = deprecator.define(" in content
    assert 'warn_in="2.0.0"' in content
    assert 'gone_in="3.0.0"' in content
    assert "@EXAMPLE_DEPRECATION.apply" in content


def test_add_entrypoint_to_pyproject(tmp_path: Path) -> None:
    """Test adding entrypoint to pyproject.toml."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"
version = "0.1.0"

[tool.setuptools]
packages = ["test_package"]
""")

    # Add entrypoint
    success = add_entrypoint_to_pyproject(
        pyproject_path, package_name="test-package", import_name="test_package"
    )
    assert success

    # Check the file was updated
    content = pyproject_path.read_text()
    assert '[project.entry-points."deprecator.deprecator"]' in content
    assert 'test-package = "test_package._deprecations:deprecator"' in content

    # Adding again should still succeed (idempotent)
    success = add_entrypoint_to_pyproject(
        pyproject_path, package_name="test-package", import_name="test_package"
    )
    assert success


def test_add_entrypoint_with_existing_entrypoints(tmp_path: Path) -> None:
    """Test adding entrypoint when other entry-points already exist."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"

[project.entry-points."other.entrypoint"]
something = "module:attr"
""")

    success = add_entrypoint_to_pyproject(
        pyproject_path, package_name="test-package", import_name="test_package"
    )
    assert success

    content = pyproject_path.read_text()
    assert '[project.entry-points."deprecator.deprecator"]' in content
    assert 'test-package = "test_package._deprecations:deprecator"' in content
    # Original entrypoint should still be there
    assert '[project.entry-points."other.entrypoint"]' in content


def test_init_deprecator_full_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test the full init_deprecator flow."""
    # Create project structure
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"
version = "0.1.0"

[tool.setuptools]
packages = ["test_package"]
""")

    # Create package directory
    package_dir = tmp_path / "test_package"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("")

    # Change to the project directory
    monkeypatch.chdir(tmp_path)

    # Create a console with no interactivity (for testing)
    console = Console(force_terminal=False, force_interactive=False)

    # Run init
    init_deprecator(console)

    # Check that _deprecations.py was created
    deprecations_file = tmp_path / "test_package" / "_deprecations.py"
    assert deprecations_file.exists()

    content = deprecations_file.read_text()
    assert "deprecator = for_package(__package__)" in content
    assert "EXAMPLE_DEPRECATION" in content

    # Check that pyproject.toml was updated
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    assert "deprecator.deprecator" in pyproject_content
    assert 'test-package = "test_package._deprecations:deprecator"' in pyproject_content


def test_init_deprecator_src_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test init with src/ layout."""
    # Create project with src layout
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"

[tool.setuptools]
packages = ["test_package"]
""")

    # Create src/package directory
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    package_dir = src_dir / "test_package"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("")

    # Change to project directory
    monkeypatch.chdir(tmp_path)

    console = Console(force_terminal=False, force_interactive=False)
    init_deprecator(console)

    # Check that file was created in src/test_package
    deprecations_file = src_dir / "test_package" / "_deprecations.py"
    assert deprecations_file.exists()


def test_init_deprecator_no_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test init when pyproject.toml doesn't exist."""
    monkeypatch.chdir(tmp_path)

    console = Console(force_terminal=False, force_interactive=False)

    with pytest.raises(SystemExit) as exc_info:
        init_deprecator(console)

    assert exc_info.value.code == 2


def test_init_deprecator_invalid_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test init with invalid pyproject.toml."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("invalid toml {{{")

    monkeypatch.chdir(tmp_path)

    console = Console(force_terminal=False, force_interactive=False)

    with pytest.raises(SystemExit) as exc_info:
        init_deprecator(console)

    assert exc_info.value.code == 2


def test_init_deprecator_no_package_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test init when package name cannot be determined."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[tool.something]
value = "test"
""")

    monkeypatch.chdir(tmp_path)

    console = Console(force_terminal=False, force_interactive=False)

    with pytest.raises(SystemExit) as exc_info:
        init_deprecator(console)

    assert exc_info.value.code == 2


def test_init_deprecator_package_dir_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test init when package directory doesn't exist."""
    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"
""")

    monkeypatch.chdir(tmp_path)

    console = Console(force_terminal=False, force_interactive=False)

    with pytest.raises(SystemExit) as exc_info:
        init_deprecator(console)

    assert exc_info.value.code == 2


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="Test for Python < 3.11")
def test_init_deprecator_tomli_not_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test init when tomli is not available (Python < 3.11)."""
    # Mock tomli import to fail
    import builtins

    original_import = builtins.__import__

    def mock_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "tomli":
            raise ImportError("No module named 'tomli'")
        return original_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", mock_import)

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text("""
[project]
name = "test-package"
""")

    monkeypatch.chdir(tmp_path)

    console = Console(force_terminal=False, force_interactive=False)

    with pytest.raises(SystemExit) as exc_info:
        init_deprecator(console)

    assert exc_info.value.code == 2
