Version History
***************

.. _version_0_15:

Version 0.15
============
* Add support for canvas test in methanol
* fix hostshell-workload test for upstream builds

.. _version_0_14:

Version 0.14
============
* added private test support for bigLITTLE workload suite

.. _version_0_13:

Version 0.13
============
* update git URL for methanol
* delete the copy media files source because this is done with the android_install_cts_medias action

.. _version_0_12:

Version 0.12
============
* add sched_tests.py
* add task_placement test
* fixes to sdcard mount and vellamo tests

.. _version_0_11:

Version 0.11
============
* methanol test fix
* add support the android black box harness

.. _version_0_10:

Version 0.10
============
* update to methanol
* add MonkeyRunner Parser

.. _version_0_9_1:

Version 0.9.1
=============
* Fix bug 1037936 caused by revno 189.3.18

.. _version_0_9:

Version 0.9
===========
* Make mmtest logs less verbose.
* Wait longer for wifi to turn off.
* add extract-attachments sub command
* big_LITTLE: add support for selecting testsuite through $(OPTIONS)
* add methanol test

.. _version_0_8:

Version 0.8
===========
* added a test wrapper to make it easier to add shell script type tests
* updated CTS to use latest Google version
* added wifi connection test
* updates to pm-qa

.. _version_0_7:

Version 0.7
===========

* add a test to disable android wallpaper
* input method service test
* monkey runner updates
* pm-qa test support
* big-LITTLE test support

.. _version_0_6:

Version 0.6
===========

* added new sleep test
* added a hello world example test
* increase number of repeats for skia benchmark
* update URL's for test data in some tests

.. _version_0_5:

Version 0.5
===========

* new tests:
  * cache-coherency
  * iozone
  * memtester
* support running monkeyrunner tests

.. _version_0_4:

Version 0.4
===========
* new wifi test
* update bluetooth test
* update test bundle format to 1.3

.. _version_0_3:

Version 0.3
===========
* new tjbench test
* new bluetooth test
* remove dependency on linaro_json

.. _version_0_2:

Version 0.2
===========
* new gator test
* update mmtest script
* Bug #962094: error occurred when no parser specified for run-custom command
* Bug #962096: the test_id generated is longer than 64

.. _version_0_0.10:

Version 0.0.10
==============
* new CTS test
* new v8 test
* new skia test
* new glmark2 test
* add support for install option
* add support for multiple ids for delete and parse commands
* remove external tools

.. _version_0_0.9:

Version 0.0.9
=============
* add unit test
* fix LP: #902161 by removing dependency on pexpect.

.. _version_0_0.8:

Version 0.0.8
=============
* fix the logical of makedirs Bug LP:#891326
* modify mmtest to use the built-in MediaFramework

.. _version_0_0.7:

Version 0.0.7
=============
* add new mmtest for Multimedia Test

.. _version_0_0.6:

Version 0.0.6
=============
* fix install options to go through install method rather than test loader

.. _version_0_0.5:

Version 0.0.5
=============
* add support for install option of install subcommand
* change monkey to always return 0

.. _version_0_0.4:

Version 0.0.4
=============
* update for 0xbench's package name modification

.. _version_0_0.3:

Version 0.0.3
=============
* add function to collect package information and screen shot after test
* add support for two more instances to be executed simultaneously
* add check for the existence of adb conmmand
* modify MANIFEST.in to make files in test_definitions be installed successfully

.. _version_0_0.1:

Version 0.0.1
=============

* Initial release
