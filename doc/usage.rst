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
(laptop or computer or a virtual machine), installs the tests that are to be 
executed and then executes them manually (by manually running LAVA Android test, 
the actual tests are non-interactive).

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
the developer ran the test at least once and wrote down the result identifier.
The set of commands one might use is::

 $ lava-android-test parse result-id

The result id is used to locate leftovers from running that specific test 
at some previous point in time.

By default parse will print the bundle to standard output for inspection. 
It should be redirected to a page for easier verification.

.. note::

    While the syntax of the bundle created with `lava-android-test parse` is always
    correct (or, if the parser does something really, really strange, a
    detailed error is reported), the actual contents may not be what you
    intended it to be. Parsers are ultimately fragile as they mostly deal with
    unstructured or semi-structured free-form text that most test programs seem
    to produce. The ultimate goal of a developer should be to produce
    unambiguous, machine readable format. This level of integration would allow
    to wrap a whole class of tests in one go (such as all xUnit-XML speaking
    test frameworks).

Usage with the dispatcher
^^^^^^^^^^^^^^^^^^^^^^^^^

The dispatcher is useful for automating LAVA Android Test environment setup, describing
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
methods: :meth:`~lava_android_test.api.ITest.install`,
:meth:`~lava_android_test.api.ITest.run`,
:meth:`~lava_android_test.api.ITest.parse`.

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

Steps to integrate an Android test to LAVA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Checkout the lava-android-test

With the following command::

 bzr branch lp:lava-android-test

2. About wrapper script

If the test tools are just command that can be run on android system, 
and the output is well formatted, then congratulations, you can go
directly to step 6. You don't need to wrap script again.

3. About test scripts/tools

If the test tools has already been build into the android image or 
in the host image(normal Ubuntu image), then you won't need to define any
scripts for organizing the test tools, you can skip this step.

Otherwise, put the actual test tools in some place, normally they are 
in a sub directory of test_definitions, like the busybox test, i.e. 
the actual test tool is busybox_test.sh, and it is put in the 
lava_android_test/test_definitions/busybox directory.

.. note::
   In this case, we should modify the MANIFEST.in file in the root source directory. 
   Otherwise the contents in that directory won’t be installed into the system python library.
   Like:

   include lava_android_test/test_definitions/busybox/

4. Add a test wrapper script for your test into the test_definitions directory. 

The content of the wrapper script should be something like below,
Normally, you just need to redefine the red and bold part in the above::

   import os
   import lava_android_test.testdef

   test_name = 'test_sample'

   #linux commands that will be run on the host before INSTALL_STEPS_ADB_PRE"
   INSTALL_STEPS_HOST_PRE = []
   #adb commands that will be run before install apk file into android
   INSTALL_STEPS_ADB_PRE = []
   #APK file path list that will be intalled into android
   APKS= []
   #adb commands that will be run before install apk file into android
   INSTALL_STEPS_ADB_POST = []
   #linux commands that will be run on the host after INSTALL_STEPS_ADB_POST
   INSTALL_STEPS_HOST_POST = []

   #linux commands that will be run on the host before RUN_STEPS_ADB_PRE
   RUN_STEPS_HOST_PRE = []
   #adb commands that will be run before install apk file into android
   RUN_STEPS_ADB_PRE = []
   #commands that will be run on android
   ADB_SHELL_STEPS = []
   #adb commands that will be run before install apk file into android
   RUN_STEPS_ADB_POST = []
   #linux commands that will be run on the host after RUN_STEPS_ADB_POST
   RUN_STEPS_HOST_POST = []

   #pattern to parse the command output to generate the test result.
   PATTERN = "^\s*(?P<test_case_id>\w+)=(?P<result>\w+)\s*$"

   inst = lava_android_test.testdef.AndroidTestInstaller(steps_host_pre=INSTALL_STEPS_HOST_PRE,
                                                         steps_adb_pre=INSTALL_STEPS_ADB_PRE,
                                                         apks=APKS,
                                                         steps_adb_post=INSTALL_STEPS_ADB_POST,
                                                         steps_host_post=INSTALL_STEPS_HOST_POST)
   run = lava_android_test.testdef.AndroidTestRunner(steps_host_pre=RUN_STEPS_HOST_PRE,
                                                     steps_adb_pre=RUN_STEPS_ADB_PRE,
                                                     adbshell_steps=ADB_SHELL_STEPS,
                                                     steps_adb_post=RUN_STEPS_ADB_POST,
                                                     steps_host_post=RUN_STEPS_HOST_POST)
   parser = lava_android_test.testdef.AndroidTestParser(PATTERN)
   testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                   installer=inst,
                                                   runner=run,
                                                   parser=parser)


And in the command part, you can use "$(SERIAL)" to represent the device serial number, like::

   RUN_STEPS_HOST_POST = [ 'python %s/android-0xbenchmark/android_0xbenchmark_wait.py $(SERIAL)' % curdir]

and "$(OPTIONS)" to represent the option string passed from command line, like::

   INSTALL_STEPS_HOST_PRE = [ 'echo $(OPTION)']
   RUN_STEPS_HOST_PRE = [ 'echo $(OPTION)']

then you can run lava-android-test install -o "install options string" or lava-android-test run -O "run options string"

.. note::

   Because lava-android-test will be run on lava-lab, and there will be multiple devices connected simultaneously, 
   So we should consider to pass the device serial number for each test tools. 
   If the test tools is defined for steps_adb_pre/adbshell_steps/steps_adb_post, 
   then there is no need to pass the device serial number, lava-android-test will do this for you.


5. you can:

* use "lava-android-test list-tests" to check if the test wrapper created can be recognized,
* use "lava-android-test install ${test_name}" to install the test,
* use "lava-android-test run ${test_name}" to execute the test,
* use "lava-android-test show ${result_id}" to show the output the test executed,
* use "lava-android-test parse ${result_id}" to to generate the result bundle for the test executed.

Here is a blog about install/test lava-android-test that you can reference::

  http://www.linaro.org/linaro-blog/2011/12/01/local-lava-testing-of-android-ics/

6. Integrate Into Lava

When you have done the above steps and verified your test that works well, 
then you can integrate it in LAVA with the android-build. Here is a description about that::

  https://wiki.linaro.org/Platform/Android/AndroidBuild-LavaIntegration

7. Add Document

At last don’t forget to add an entry and some document in the doc/tests.rst file. Like::

   busybox
   +++++++
   .. automodule:: lava_android_test.test_definitions.busybox

Then the information will be listed in the below url:
   http://lava-android-test.readthedocs.org/en/latest/tests.html

8. Commit Modification

In lava-android-test directory, run the following commands::

   bzr launchpad-login ${your-lauchpad-id}
   bzr commit -m '${commit msg}
   bzr push lp:~${your-launchpad-id}/lava-android-test/${branch-name}

Then you can see your branch in the following page:
 https://code.launchpad.net/lava-android-test

Click your branch, and click the “Propose for merging” link in your branch page to submit a merge proposal. 
In the proposal page, please set Reviewer: to linaro-validation.

Adding Results Parsing
++++++++++++++++++++++

Because every test has its own way of displaying results, there is no common,
enforced way of interpreting the results from any given test. That means that
every test definition also has to define a parser so that LAVA Android Test can
understand how to pick out the most useful bits of information from the output.
What we've tried to do, is make this as simple as possible for the most common
cases, while providing the tools necessary to handle more complex output.

To start off, there are some fields you are always going to want to either pull
from the results, or define. For all tests:

* test_case_id - This is just a field that uniquely identifies the test. 
  This can contain letters, numbers, underscores, dashes, or periods. 
  If you use any illegal characters, they will automatically be dropped 
  by the TestParser base class before parsing the results. Spaces will be 
  automatically converted to underscores. If you wish to change this behaviour, 
  make sure that you either handle fixing the test_case_id in your parser, 
  or override the TestParser.fixids() method.
* result - result is simply the result of the test. This applies to both qualitative 
  as well as quantitative tests, and the meaning is specific to the test itself. 
  The valid values for result are: "pass", "fail", "skip", or "unknown".

For performance tests, you will also want to have the following two fields:

* measurement - the "score" or resulting measurement from the benchmark.
* units - a string defining the units represented by the measurement in some way 
  that will be meaningful to someone looking at the results later.

For results parsing, it's probably easier to look at some examples. Several
tests have already been defined in the lava-android-test test_definitions directory
that serve as useful examples.

Defining a simple test
++++++++++++++++++++++
 
**Example 1** The tjunittest example might look something like this::

   import os
   import lava_android_test.testdef

   test_name = 'tjunittest'

   #linux commands that will be run on the host before INSTALL_STEPS_ADB_PRE"
   INSTALL_STEPS_HOST_PRE = []
   #adb commands that will be run before install apk file into android
   INSTALL_STEPS_ADB_PRE = []
   #APK file path list that will be intalled into android
   APKS= []
   #adb commands that will be run before install apk file into android
   INSTALL_STEPS_ADB_POST = []
   #linux commands that will be run on the host after INSTALL_STEPS_ADB_POST
   INSTALL_STEPS_HOST_POST = []

   #linux commands that will be run on the host before RUN_STEPS_ADB_PRE
   RUN_STEPS_HOST_PRE = []
   #adb commands that will be run before install apk file into android
   RUN_STEPS_ADB_PRE = []
   #commands that will be run on android
   ADB_SHELL_STEPS = ['tjunittest']
   #adb commands that will be run before install apk file into android
   RUN_STEPS_ADB_POST = []
   #linux commands that will be run on the host after RUN_STEPS_ADB_POST
   RUN_STEPS_HOST_POST = []

   #pattern to parse the command output to generate the test result.
   PATTERN = "^\s*(?P<test_case_id>.+)\s+\.\.\.\s+(?P<result>\w+)\.\s+(?P<measurement>[\d\.]+)\s+(?P<units>\w+)\s*$"

   inst = lava_android_test.testdef.AndroidTestInstaller(steps_host_pre=INSTALL_STEPS_HOST_PRE,
                                                         steps_adb_pre=INSTALL_STEPS_ADB_PRE,
                                                         apks=APKS,
                                                         steps_adb_post=INSTALL_STEPS_ADB_POST,
                                                         steps_host_post=INSTALL_STEPS_HOST_POST)
   run = lava_android_test.testdef.AndroidTestRunner(steps_host_pre=RUN_STEPS_HOST_PRE,
                                                     steps_adb_pre=RUN_STEPS_ADB_PRE,
                                                     adbshell_steps=ADB_SHELL_STEPS,
                                                     steps_adb_post=RUN_STEPS_ADB_POST,
                                                     steps_host_post=RUN_STEPS_HOST_POST)
   parser = lava_android_test.testdef.AndroidTestParser(PATTERN)
   testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                   installer=inst,
                                                   runner=run,
                                                   parser=parser)

In this example, we just simply defined the tjunittest command in ADB_SHELL_STEPS variable,
and defined the PATTERN variable used by AndroidTestParser.

If you were to save this under the test_definitions directory as 'tjunittest.py', 
then run 'lava-android-test install tjunittest' and 'lava-android-test run tjunittest', 
you would have a test result with the result id shown to you.
And you can also run 'lava-android-test parse ${result_id}' to get the test result in the json format,
which you can submit to lava.

