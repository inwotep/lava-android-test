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
Drives big.LITTLE test scripts that are pre-intalled on Linaro Android
builds of big.LITTLE

**URL:** https://wiki.linaro.org/Platform/Android/AndroidOnFastModels

**Default options:** None
"""

import lava_android_test.testdef

test_name = 'big_LITTLE'

DEFAULT_OPTIONS='-a'

INSTALL_STEPS_ADB_PRE = []
ADB_SHELL_STEPS = ['run_stress_switcher_tests.sh $(OPTIONS)']
PATTERN = "(?P<test_case_id>.*-*)\s+:\s+(?P<result>(PASS|FAIL))"

inst = lava_android_test.testdef.AndroidTestInstaller(
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidTestParser(PATTERN)
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser,
                                    default_options=DEFAULT_OPTIONS)
