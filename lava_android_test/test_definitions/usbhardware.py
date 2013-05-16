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
Ensures USB is enabled on the device by checking /sys entries

**URL:** None

**Default options:** None
"""

import os
import lava_android_test.testdef
from lava_android_test.config import get_config

test_name = 'usbhardware'
config = get_config()
curdir = os.path.realpath(os.path.dirname(__file__))
test_sh_name = 'usbhardware.sh'
test_sh_path = os.path.join(curdir, test_name, test_sh_name)
test_sh_android_path = os.path.join(config.installdir_android,
                                    test_name, test_sh_name)

INSTALL_STEPS_ADB_PRE = ['push %s %s ' % (test_sh_path,
                                          test_sh_android_path),
                          'shell chmod 777 %s' % test_sh_android_path]

ADB_SHELL_STEPS = [test_sh_android_path]
PATTERN = "^\s*(?P<test_case_id>\w+)=(?P<result>\w+)\s*$"

inst = lava_android_test.testdef.AndroidTestInstaller(
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidTestParser(PATTERN)
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser)
