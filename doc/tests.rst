.. _test:

===============
Supported Tests
===============

The following tests are currently supported in LAVA Android Test:

 * `0xbench`_
 * `bctest`_
 * `big_LITTLE`_
 * `blackbox`_
 * `bluetooth`_
 * `busybox`_
 * `cache_coherency`_
 * `commands`_
 * `command-example`_
 * `command-linaro_android_kernel_test`_
 * `command-tjunittest`_
 * `cts`_
 * `gatortest`_
 * `glmark2`_
 * `helloworld`_
 * `hostshells`_
 * `hostshell-connect-lab-wifi`_
 * `hostshell-example`_
 * `hostshell-sdcard-mounted`_
 * `hostshell-workload`_
 * `ime`_
 * `install_prep_4bench`_
 * `instruments`_
 * `instrument-example`_
 * `iozone`_
 * `memtester`_
 * `methanol`_
 * `mmtest`_
 * `monkey`_
 * `monkey_long_run`_
 * `pm_qa`_
 * `sched_tests`_
 * `shells`_
 * `shell-binder`_
 * `shell-dalvik-vm-unit-tests`_
 * `shell-example`_
 * `skia`_
 * `sleep`_
 * `task_placement`_
 * `tjbench`_
 * `usbhardware`_
 * `v8`_
 * `monkeyrunner(system)`_
 * `monkeyrunner(third-party-benchmarks)`_

0xbench
+++++++
.. automodule:: lava_android_test.test_definitions.0xbench

bctest
++++++
.. automodule:: lava_android_test.test_definitions.bctest

big_LITTLE
++++++++++
.. automodule:: lava_android_test.test_definitions.big_LITTLE

blackbox
++++++++
.. automodule:: lava_android_test.test_definitions.blackbox

bluetooth
+++++++++
.. automodule:: lava_android_test.test_definitions.bluetooth

busybox
+++++++
.. automodule:: lava_android_test.test_definitions.busybox

cache_coherency
+++++++++++++++
.. automodule:: lava_android_test.test_definitions.cache_coherency

commands
++++++++
.. automodule:: lava_android_test.test_definitions.commands

command-example
+++++++++++++++
.. automodule:: lava_android_test.test_definitions.commands.example

command-linaro_android_kernel_test
++++++++++++++++++++++++++++++++++
.. automodule:: lava_android_test.test_definitions.commands.linaro_android_kernel_test

command-tjunittest
++++++++++++++++++
.. automodule:: lava_android_test.test_definitions.commands.tjunittest

cts
+++
.. automodule:: lava_android_test.test_definitions.cts

gatortest
+++++++++
.. automodule:: lava_android_test.test_definitions.gatortest

glmark2
+++++++
.. automodule:: lava_android_test.test_definitions.glmark2

helloworld
++++++++++
.. automodule:: lava_android_test.test_definitions.helloworld

hostshells
++++++++++
.. automodule:: lava_android_test.test_definitions.hostshells

hostshell-connect-lab-wifi
++++++++++++++++++++++++++
Try to connect the wifi in lava-lab for other tests, also can be used to test if the wifi works

**URL:** None

**Default options:** None

hostshell-example
+++++++++++++++++
Example for how to integrate test which is a host shell script into lava-android-test

**URL:** None

**Default options:** None

hostshell-sdcard-mounted
++++++++++++++++++++++++
Check if the sdcard is mounted when the android booted up by check the output of mount command

**URL:** None

**Default options:** None

hostshell-workload
++++++++++++++++++
Test of Automatic Workload Automation for big LITTLE Systems from ARM

**URL:** https://linaro-private.git.linaro.org/gitweb?p=workload-automation.git;a=summary 

**Default options:** None

ime
+++
.. automodule:: lava_android_test.test_definitions.ime

install_prep_4bench
+++++++++++++++++++
.. automodule:: lava_android_test.test_definitions.install_prep_4bench

instruments
+++++++++++
.. automodule:: lava_android_test.test_definitions.instruments

instrument-example
++++++++++++++++++
.. automodule:: lava_android_test.test_definitions.instruments.example

iozone
++++++
.. automodule:: lava_android_test.test_definitions.iozone

memtester
+++++++++
.. automodule:: lava_android_test.test_definitions.memtester

methanol
++++++++
.. automodule:: lava_android_test.test_definitions.methanol

mmtest
++++++
.. automodule:: lava_android_test.test_definitions.mmtest

monkey
++++++
.. automodule:: lava_android_test.test_definitions.monkey

monkey_long_run
+++++++++++++++
.. automodule:: lava_android_test.test_definitions.monkey_long_run

pm_qa
+++++
.. automodule:: lava_android_test.test_definitions.pm_qa

sched_tests
+++++++++++
.. automodule:: lava_android_test.test_definitions.sched_tests

shells
++++++
.. automodule:: lava_android_test.test_definitions.shells

shell-binder
++++++++++++
Measures the rate at which a short binder IPC operation can be
performed.  The operation consists of the client sending a parcel
that contains two integers.  For each parcel that the server
receives, it adds the two integers and sends the sum back to
the client.

**URL:** http://android.git.linaro.org/gitweb?p=platform/system/extras.git;a=blob;f=tests/binder/benchmarks/binderAddInts.cpp;hb=HEAD

**Default options:** None

shell-dalvik-vm-unit-tests
++++++++++++++++++++++++++
Run the unit tests for dalvik vm.

**URL:** http://android.git.linaro.org/gitweb?p=platform/dalvik.git;a=blob;f=unit-tests/dvmHumanReadableDescriptor_test.cpp;h=89ca85c39e575a2f90f38d5fdc5aa07879a0f3e7;hb=HEAD 

**Default options:** None

shell-example
+++++++++++++
Example for how to integrate test which is a shell script into lava-android-test

**URL:** None

**Default options:** None

skia
++++
.. automodule:: lava_android_test.test_definitions.skia

sleep
+++++
.. automodule:: lava_android_test.test_definitions.sleep

task_placement
++++++++++++++
.. automodule:: lava_android_test.test_definitions.task_placement

tjbench
+++++++
.. automodule:: lava_android_test.test_definitions.tjbench

usbhardware
+++++++++++
.. automodule:: lava_android_test.test_definitions.usbhardware

v8
++
.. automodule:: lava_android_test.test_definitions.v8

monkeyrunner(system)
++++++++++++++++++++
Run some system tests with the monkeyrunner scripts.
but this part should be recreated with uiautomator scripts

**URL:** http://android.git.linaro.org/gitweb?p=test/linaro/android/system.git;a=summary

**Default options:** None

monkeyrunner(third-party-benchmarks)
++++++++++++++++++++++++++++++++++++
Support for run the third party benchmark applications automatically,
and collect the test result automatically.
The supported third party benchmark applications include:
andebench/antutu/caffeinemark/geekbench/glbenchmark/linpack/nbench/quadrant/vellamo

**URL of apks:** https://linaro-private.git.linaro.org/gitweb?p=people/yongqinliu/benchmark-apks.git;a=summary

**URL of scripts:** http://android.git.linaro.org/gitweb?p=platform/external/thirdparty-benchmarks.git;a=summary

**Default options:** None

