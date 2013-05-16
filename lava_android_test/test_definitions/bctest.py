# Copyright (c) 2012 Linaro

# Author: Linaro Android Team <linaro-android@lists.linaro.org>
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
bctest test covers testing of a couple of binder IOCTLS.
We can think of it as a subset of "shell-binder" test,
which is much more exhaustive and is the main binder test to go for.
binder test "bctest" that is pre-intalled on Juice Android builds.

**URL:** http://android.git.linaro.org/gitweb?p=platform/frameworks/base.git;a=blob;f=cmds/servicemanager/bctest.c

**Default options:** "publish 1"
"""

import lava_android_test.config
import lava_android_test.testdef

test_name = 'bctest'

DEFAULT_OPTIONS = 'publish 1'

INSTALL_STEPS_ADB_PRE = []
ADB_SHELL_STEPS = ['bctest $(OPTIONS)']
PATTERN = "(?P<test_case_id>.*ioctl)\s(?P<result>(PASS|FAIL)?).*"

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
