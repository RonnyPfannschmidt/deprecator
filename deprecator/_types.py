"""Type definitions for the deprecator package."""

from __future__ import annotations

from typing import NewType

# A package name used throughout the deprecator system
# Used for both framework names in registries and package names in deprecators
PackageName = NewType('PackageName', str)