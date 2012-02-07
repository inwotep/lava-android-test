.. _reference:

=========
Reference
=========

.. _command_reference:

Command Reference
=================

.. automodule:: lava_test.commands
    :members:

.. todo::

    * Describe basic commands
    * Describe arguments and options to each command in detail

Pathnames and files
===================

LAVA Test uses the following files:

* ``$XDG_CONFIG_HOME/lava_test/`` -- configuration files
* ``$XDG_DATA_HOME/lava_test/installed-tests`` -- installed test programs
* ``$XDG_DATA_HOME/lava_test/results`` -- artifacts of running tests
* ``$XDG_CACHE_HOME/lava_test/`` -- download cache

.. _code_reference:

Code reference
==============

.. todo::

    * Describe general code layout
    * Describe key API integration points (on a separate page if needed for clarity)
    * Provide an example test and walk the reader through the meaning of each part

Abstract Interfaces
^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_test.api.core
    :members:

.. automodule:: lava_test.api.delegates
    :members:

.. automodule:: lava_test.api.observers
    :members:

Test definitions and test providers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_test.core.providers
    :members:

.. automodule:: lava_test.core.tests
    :members:

Test components (installers, runners and parsers)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_test.core.installers
    :members:

.. automodule:: lava_test.core.runners
    :members:

.. automodule:: lava_test.core.parsers
    :members:

Core Modules
^^^^^^^^^^^^

.. automodule:: lava_test.core.artifacts
    :members:

.. automodule:: lava_test.core.config
    :members:

Environment Scanners
^^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_test.core.hwprofile
    :members:

.. automodule:: lava_test.core.swprofile
    :members:

Utilities
^^^^^^^^^

.. automodule:: lava_test.utils
    :members:

.. automodule:: lava_test.extcmd
    :members:


