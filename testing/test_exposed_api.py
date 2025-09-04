import importlib.metadata

from packaging.version import Version

import deprecator
from deprecator._types import PackageName


def test_for_package() -> None:
    dep = deprecator.for_package("deprecator")

    assert isinstance(dep, deprecator._deprecator.Deprecator)

    assert dep.name == PackageName("deprecator")
    assert dep.current_version == Version(importlib.metadata.version("deprecator"))
