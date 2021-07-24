========
Golocity
========

Summary
=======

    Golocity is a young project and while there is testing,
    there still may be bugs. Be sure and test thoroughly prior to use in a production environment.

**Golocity** is an easy to use CLI execution manager for the Golem Network.
It aims to convert and deploy your dockerized project on the Golem Network in
as little time as possible. It is perfect for developers who want to deploy
their preexisting projects on the Network or those who need a starting point
to harness all of the Network's features.

Installation
============

Golocity is available on ``PyPI``. This will install the latest stable version.

To install Golocity, simply use ``pip``:

.. code-block:: console

    pip install --user golocity


Getting Started
===============

Building the images
-------------------

Before your project can be deployed on the Network, we must first build the docker
image as well as the Golem virtual machine image. Before issuing the command, make
sure you have Docker installed and running on your computer.

To do so, use the ``build`` command:

.. code-block:: console

    golocity build /path/to/your/project

This will build the requisite images as well as create a ``.golocity``
directory in your projects directory. This directory holds configuration files needed
by Golocity as well as logs.

The build command also pushes the Golem virtual machine image to the Network's public
repository. To preform a dry-run, append the ``--info`` flag to the command.

Under the hood, Golocity parses your Dockerfile for ``ENTRYPOINT`` and ``CMD`` commands.
These commands currently are not supported in the Golem virtual machine format, so
Golocity removes them and manually calls them from within the ``deploy`` command. Don't
worry, Golocity will not alter your project files, it only operates on temporary copies.

Deploying to the Network
------------------------

Once you have successfully built and pushed the images, you are ready to deploy your
project on the Network! First, make sure you have the ``yagna`` daemon running on your
machine, for more information, refer to the `Golem Handbook.
<https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development/run-first-task-on-golem>`_

Now, deploying is one line away!

.. code-block:: console

    golocity deploy [budget]

Replace ``budget`` with the limit of what to spend while running the project. From here
Golocity will handle the rest. It will find the best provider and handle the output.

Contributing
=============

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
