.. _usage:

=====
Usage
=====

Workflow Overview
=================

LAVA Android Test can be used in several different ways. Most notably those are
standalone (without the LAVA dispatcher) and managed (when LAVA Android Test is
installed and controlled by the LAVA dispatcher).

Standalone usage
^^^^^^^^^^^^^^^^

In standalone mode a human operator installs LAVA Android Test on some device
(development board, laptop or other computer or a virtual machine), installs
the tests that are to be executed and then executes them manually (by manually
running LAVA Android test, the actual tests are non-interactive).

Using LAVA to develop and run new tests
+++++++++++++++++++++++++++++++++++++++

This mode is useful for test development (adding new tests, developing custom
tests especially tailored for LAVA, etc.). Here the typical cycle depends on
how the tests is wrapped for usage by LAVA and what the test developer is
focusing on.

While developing the actual test the typical set of commands might look like
this::

 $ lava-android-test install my-custom-test
 $ lava-android-test run my-custom-test
 $ lava-android-test uninstall my-custom-test

Here the developer could observe changes to the test program (that is
presumably compiled and copied somewhere by the install stage).

Using LAVA to analyze test results
++++++++++++++++++++++++++++++++++

Developing the test is only half of the story. The other half is developing
LAVA Android Test integration code, most importantly the artefact parser / analyzer.
This part has to be implemented in python (unlike the test program that can be
implemented in any language and technology). Here the developer is focusing on
refining the parser to see if the outcome is as indented. Assuming that earlier
the developer ran the test at least once and wrote down the result identifier
the set of commands one might use is::

 $ lava-android-test parse my-custom-test

The result id is used to locate leftovers from running that specific test 
at some previous point in time.

By default parse will print the bundle to standard output for inspection. 
It should be redirected to a pager for easier verification.

.. note::

    While the syntax of the bundle created with `lava-test parse` is always
    correct (or, if the parser does something really, really strange, a
    detailed error is reported) the actual contents may not be what you
    intended it to be. Parsers are ultimately fragile as they mostly deal with
    unstructured or semi-structured free-form text that most test programs seem
    to produce. The ultimate goal of a developer should be to produce
    unambiguous, machine readable format. This level of integration would allow
    to wrap a whole class of tests in one go (such as all xUnit-XML speaking
    test frameworks).

Usage with the dispatcher
^^^^^^^^^^^^^^^^^^^^^^^^^

The dispatcher is useful for automating LAVA Test environment setup, describing
test scenarios (the list of tests to invoke) and finally storing the results in
the LAVA dashboard.

Typically this mode is based on the following sequence of commands:
  
#. Install lava-android-test along with the required dependencies.
#. Install the test or tests. 
#. Run, parse and store in one.

Here the whole setup is non-interactive and at the end the dispatcher can copy
the output bundle for additional processing.

Automation considerations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. _wrapping_existing_test_or_benchmark:

Wrapping existing test or benchmark
===================================

LAVA Android Test can be extended in several different ways. There is no best method,
each has some pros and cons. In general we welcome any freely redistributable,
generic tests. Those enrich the LAVA ecosystem and by providing useful
out-of-the-box features to our users.

Technically all tests are hidden behind a set of abstract interfaces that tell
LAVA Android Test what to do in response to operator or dispatcher actions. The primary
interface is :class:`~lava_android_test.api.ITest` and the three principal
methods: :meth:`~lava_android_test.api.ITest`,
:meth:`~lava_android_test.api.ITest`,
:meth:`~lava_android_test.api.ITest`.

In practice it is usually much easier to instantiate our pluggable delegate
test (:class:`lava_android_test.testdef.Test`) and define the three delegates that
know how to install, run and parse. Again for each step we have a base class
that can be easily customized or even used directly as is.  Those classes are
:class:`~lava_android_test.testdef.TestInstaller`,
:class:`~lava_android_test.testdef.TestRunner` and
:class:`~lava_android_test.testdef.TestParser`. They all implement well-defined
interfaces so if you wish to customize them you should become familiar with 
the API requirements first.

Contributing new tests to LAVA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The most direct way to add a new test is to contribute patches to LAVA Android Test
itself. This method will simply add a new test definition to the collection of
available tests.

This method is recommended for generic tests that rarely change and are
suitable for wide variety of hardware and software for android.

The advantage is that those tests can be invoked out of the box and will be
maintained by the LAVA team. The disadvantage is that all changes to those
tests need to follow Linaro development work flow, get reviewed and finally
merged. Depending on your situation this may be undesired.

.. todo::

    Describe how tests are discovered, loaded and used. It would be
    nice to have a tutorial that walks the user through wrapping a
    simple pass/fail test. 
'
