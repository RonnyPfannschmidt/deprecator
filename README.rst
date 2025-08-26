Deprecator: A tool for deprecating older code.
----------------------------------------------

:Author:
	Anthony Long

:Version:
	0.1
	- Initial release.

What is Deprecator?
___________________

Deprecator is a decorator which helps you to document, and warn users of deprecations.

Installation
____________

.. code:: bash

    pip install deprecator

Usage
_____

.. code:: python

    from deprecator import deprecate

    def new_function():
        print("This is the new function")

    @deprecate(replacement=new_function)
    def old_function():
        print("This is the old function")

    # Using the deprecated function will show a warning
    old_function()
    # DeprecationWarning: old_function is deprecated; use new_function instead.

Development
___________

This project uses `uv <https://docs.astral.sh/uv/>`_ for dependency management and development workflows.

Quick Start:

.. code:: bash

    # Clone and setup
    git clone https://github.com/antlong/deprecator.git
    cd deprecator
    uv sync

    # Run tests
    uv run pytest

    # Run linting and formatting
    uv run ruff check .
    uv run ruff format .

    # Run type checking
    uv run mypy deprecator/

See ``CONTRIBUTING.md`` for detailed development instructions.
