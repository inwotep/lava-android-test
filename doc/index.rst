=======================
LAVA Android Test Documentation
=======================

LAVA Android Test is a wrapper framework exposing unified API and command line
interface for running arbitrary tests and storing the results in a structured
manner.

LAVA Android Test is a part of the LAVA stack and can be used with other LAVA
components, most notably the dispatcher (for setting up the test environment
and controlling execution of multiple tests) and the dashboard (for storing)

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
* Support for capturing android environment information such as installed packages and
  hardware information and recording that in a machine-readable manner.
* Store results in raw form (log files) as well as Linaro Dashboard Bundle
  format that can be uploaded to the LAVA Dashboard for archiving and analysis.
* Extensible API for adding new tests (:class:`~lava_android_test.api.ITest`)
* Ever-growing collection of freely available and generic tests and benchmarks 

Quickstart
==========

This example will run on Ubuntu Lucid and beyond.  we should better to install it 
in an virtual environment, so that it will not mess up with the system environment::

 $ virtualenv ${workspace}                 ### create the virtual environment
 $ source ${workspace}/bin/activate        ### enter the virtual environment
 $ pip install --upgrade lava-android-test ### install the latest package to the the virtual environment
 $ lava-android-test install monkey        ### install the test named monkey
 $ lava-android-test run monkey            ### run the monkey test
 $ virtualenv ${workspace}                 ### exit the virtual environment

.. seealso:: For a more thorough description see :ref:`usage`
.. seealso:: For detailed installation istructions see :ref:`installation`

Latest documentation
====================

This documentation may be out of date, we try to make sure that all the latest
and greatest releases are always documented on http://lava-android-test.readthedocs.org/


Source code, bugs and patches
=============================

The project is maintained on Launchpad at http://launchpad.net/lava-android-test/.

You can get the source code with bazaar using ``bzr branch lp:lava-android-test``.
Patches can be submitted using Launchpad merge proposals (for introduction to
this and topic see https://help.launchpad.net/Code/Review).

Please report all bugs at https://bugs.launchpad.net/lava-android-test/+filebug.

Most of the team is usually available in ``#linaro`` on ``irc.freenode.net``.
Feel free to drop by to chat and ask questions.


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
