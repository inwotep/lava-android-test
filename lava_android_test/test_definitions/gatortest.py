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
import os

import lava_android_test.testdef

curdir = os.path.realpath(os.path.dirname(__file__))
test_name = "gatortest"

RUN_STEPS_HOST_POST = ['python %s/gatortest/daemoncheck.py $(SERIAL)' % curdir,
                       'python %s/gatortest/modulecheck.py $(SERIAL)' % curdir]

PATTERN = "^\s*(?P<test_case_id>\w+)\s*=\s*(?P<result>\w+)\s*$"

parser = lava_android_test.testdef.AndroidTestParser(PATTERN)

run = lava_android_test.testdef.AndroidTestRunner(steps_host_post=RUN_STEPS_HOST_POST)

inst = lava_android_test.testdef.AndroidTestInstaller() # dummy installer

testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                runner=run,
                                                installer=inst,
                                                parser=parser)

