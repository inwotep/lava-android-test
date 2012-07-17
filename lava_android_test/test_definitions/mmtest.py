# Copyright (C) 2011-2012 Linaro Limited
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
Performs a test of multimedia functionality in Android by playing a variety
of different multimedia formats on Android.

**URL:** http://samplemedia.linaro.org/

**Default options:** None
"""

import os
import lava_android_test.testdef
from lava_android_test.utils import get_local_name
from lava_android_test.config import get_config

test_name = 'mmtest'
config = get_config()

site = 'http://samplemedia.linaro.org/'
local_name = get_local_name(site)
RUN_STEPS_HOST_PRE = [
        'wget --progress=dot -e dotbytes=1M -r -np -l 10 -R csv,txt,css,html,gif,pdf %s -P %s' % (site,
                                                           local_name),
        r'find  %s -type f -name "index*" -exec rm -f \{\} \;' % local_name,
        r'find  %s -type f -name "README" -exec rm -f \{\} \;' % local_name]

test_files_target_path = os.path.join(config.installdir_android,
                                    test_name, local_name)
RUN_STEPS_ADB_PRE = ['push %s %s' % (local_name, test_files_target_path)]
RUN_ADB_SHELL_STEPS = ['am instrument -r -e targetDir %s \
    -w com.android.mediaframeworktest/.MediaFrameworkTestRunner'
     % test_files_target_path,
    'rm -r %s' % (test_files_target_path)]

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                steps_host_pre=RUN_STEPS_HOST_PRE,
                                steps_adb_pre=RUN_STEPS_ADB_PRE,
                                adbshell_steps=RUN_ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidInstrumentTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser)
