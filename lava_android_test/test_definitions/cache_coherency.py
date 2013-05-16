# Copyright (c) 2012 Linaro

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
Stressapptest tries to maximize randomized traffic to memory from processor 
and I/O, with the intent of creating a realistic high load situation 
in order to test the existing hardware devices in a computer.
Used for cache-coherency testing on big.LITTLE here.

**URL:** http://android.git.linaro.org/gitweb?p=platform/external/stressapptest.git;a=summary 

**Default options:** None
"""
import lava_android_test.testdef

test_name = 'cache_coherency'

INSTALL_STEPS_ADB_PRE = []
ADB_SHELL_STEPS = ['stressapptest -M 16 --cc_test -s 10']
PATTERN = "^\s*(?P<test_case_id>Status?):\s+(?P<result>(PASS|FAIL)?)\s+-\s+"

inst = lava_android_test.testdef.AndroidTestInstaller(
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidTestParser(PATTERN)
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser)
