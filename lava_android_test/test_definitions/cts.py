# Copyright (C) 2012 Linaro Limited

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

test_name = 'cts'

curdir = os.path.realpath(os.path.dirname(__file__))

RUN_STEPS_HOST_PRE = ['/bin/bash %s/cts/cts_wrapper.sh $(SERIAL)' % curdir]

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                steps_host_pre=RUN_STEPS_HOST_PRE)

#01-16 14:24:16 I/0123456789ABCDEF: android.telephony.cts.TelephonyManagerTest#testGetNetworkCountryIso PASS
pattern = '^\s*[\d-]+\s+[\d:]+\s+I\/\S+\:\s+(?P<test_case_id>\S+#\S+)\s+(?P<result>\S+)\s*$'
parser = lava_android_test.testdef.AndroidTestParser(pattern=pattern,
                                                    fixupdict={'PASS':'pass', 'FAIL':'fail'})
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser)
