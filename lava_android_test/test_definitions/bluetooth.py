# copyright (C) 2012 Linaro Limited
#
# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This test helps validating basic bluetooth functionality by executing the
Android BluetoothTestRunner tests.

**URL:** http://android.git.linaro.org/gitweb?p=platform/frameworks/base.git;a=blob;f=core/tests/bluetoothtests/src/android/bluetooth/BluetoothTestRunner.java;

**Default options:** None
"""

import lava_android_test.testdef

test_name = 'bluetooth'

cmd = ("am instrument -r -e enable_iterations 2 -e discoverable_iterations 2"
       " -e scan_iterations 2 -e enable_pan_iterations 2 -e pair_iterations 1 "
       " -e device_address $(OPTIONS) "
       " -w com.android.bluetooth.tests/android.bluetooth.BluetoothTestRunner")
RUN_ADB_SHELL_STEPS = [cmd]

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                adbshell_steps=RUN_ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidInstrumentTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser)
