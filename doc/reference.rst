.. _reference:

=========
Reference
=========

.. _command_reference:

Command Reference
=================

.. automodule:: lava_android_test.commands
    :members:

.. todo::

    * Describe basic commands
    * Describe arguments and options to each command in detail

Pathnames and files
===================

LAVA Android Test uses the following files:

* ``/tmp/lava-android-test/`` -- temporary directory to put temporary files of each lava-android-test instance.

.. _code_reference:

Code reference
==============

.. todo::

    * Describe general code layout
    * Describe key API integration points (on a separate page if needed for clarity)
    * Provide an example test and walk the reader through the meaning of each part

Abstract Interfaces
^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_android_test.api
    :members:

Test definitions and test providers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_android_test.test_definitions
    :members:

Test components (installers, runners and parsers)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_android_test.testdef
    :members:

Core Modules
^^^^^^^^^^^^

.. automodule:: lava_android_test.config
    :members:

Environment Scanners
^^^^^^^^^^^^^^^^^^^^

.. automodule:: lava_android_test.hwprofile
    :members:

.. automodule:: lava_android_test.swprofile
    :members:

Utilities
^^^^^^^^^

.. automodule:: lava_android_test.utils
    :members:

