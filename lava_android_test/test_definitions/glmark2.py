# Copyright (C) 2010-2012 Linaro Limited

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
import os
import lava_android_test.testdef
from lava_android_test.config import get_config

test_name = 'glmark2'
config = get_config()
curdir = os.path.realpath(os.path.dirname(__file__))
test_sh_name = 'glmark2.sh'
test_sh_path = os.path.join(curdir, test_name, test_sh_name)
RUN_STEPS_HOST_PRE = ['/bin/bash %s $(SERIAL)' % test_sh_path]

#I/glmark2 ( 1818): [texture] texture-filter=nearest: FPS: 8
PATTERN = "^\s*I/glmark2\s*\(.+\):\s+\[\w+\]\s+(?P<test_case_id>\S+):\s+FPS:\s+(?P<measurement>\d+)\s*$"

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                    steps_host_pre=RUN_STEPS_HOST_PRE)
parser = lava_android_test.testdef.AndroidTestParser(PATTERN,
                                        appendall={'units':'FPS'})
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser)
