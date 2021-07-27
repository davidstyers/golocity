========================
Contributing to Golocity
========================

Thank you for your interest in contributing! The following
is a guide to set up your local development environment.

Poetry
------

We use `poetry <https://github.com/sdispater/poetry>`_ to manage dependencies, to
get started follow these steps:

.. code-block:: console

    git clone https://github.com/davidstyers/golocity
    cd golocity
    poetry install
    poetry run pytest

Pre-Commit
----------

We have a configuration for
`pre-commit <https://github.com/pre-commit/pre-commit>`_ to add the hook run the
following command:

.. code-block:: console

    pre-commit install
