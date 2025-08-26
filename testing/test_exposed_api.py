import importlib.metadata

from packaging.version import Version

import deprecator


def test_for_package() -> None:
    dep = deprecator.for_package("deprecator")

    assert isinstance(dep, deprecator._deprecator.Deprecator)

    assert dep.package_name == "deprecator"
    assert dep.current_version == Version(importlib.metadata.version("deprecator"))
