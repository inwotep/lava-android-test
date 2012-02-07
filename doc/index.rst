=======================
LAVA Test Documentation
=======================

LAVA Test is a wrapper framework exposing unified API and command line
interface for running arbitrary tests and storing the results in a structured
manner.

LAVA Test is a part of the LAVA stack and can be used with other LAVA
components, most notably the dispatcher (for setting up the test environment
and controlling execution of multiple tests) and the dashboard (for storing

.. seealso:: To learn more about LAVA see https://launchpad.net/lava

Indices and tables
==================

.. toctree::
    :maxdepth: 2
    
    installation.rst
    usage.rst
    tests.rst
    reference.rst
    changes.rst
    todo.rst

Features
========

* Ability to enumerate, install, run and remove tests on a Linux-based system.
* Support for benchmarks as well as pass/fail tests.
* Support for capturing environment information such as installed software and
  hardware information and recording that in a machine-readable manner.
* Store results in raw form (log files) as well as Linaro Dashboard Bundle
  format that can be uploaded to the LAVA Dashboard for archiving and analysis.
* Extensible API for adding new tests (:class:`~lava_test.api.core.ITest`) or even
  collections of tests (:class:`~lava_test.api.core.ITestProvider`).
* Ever-growing collection of freely available and generic tests and benchmarks 

Quickstart
==========

This example will run on Ubuntu Lucid and beyond::

 $ sudo add-apt-repository ppa:linaro-validation/ppa
 $ sudo apt-get update
 $ sudo apt-get install lava-test
 $ lava-test install stream
 $ lava-test run stream

.. seealso:: For a more thorough description see :ref:`usage`
.. seealso:: For detailed installation istructions see :ref:`installation`

Latest documentation
====================

This documentation my be out of date, we try to make sure that all the latest
and greatest releases are always documented on http://lava-test.readthedocs.org/


Source code, bugs and patches
=============================

The project is maintained on Launchpad at http://launchpad.net/lava-test/.

You can get the source code with bazaar using ``bzr branch lp:lava-test``.
Patches can be submitted using Launchpad merge proposals (for introduction to
this and topic see https://help.launchpad.net/Code/Review).

Please report all bugs at https://bugs.launchpad.net/lava-test/+filebug.

Most of the team is usually available in ``#linaro`` on ``irc.freenode.net``.
Feel free to drop by to chat and ask questions.


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
