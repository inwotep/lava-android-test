# Copyright (c) 2011 Linaro

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

import lava_android_test.testdef
from lava_android_test.utils import get_local_name

test_name = 'CTSTest'

#http://source.android.com/compatibility/downloads.html
cts_url = 'http://dl.google.com/dl/android/cts/android-cts-4.0.3_r1-linux_x86-arm.zip'
zip_name = get_local_name(cts_url)
RUN_STEPS_HOST_PRE = ['wget %s' % cts_url,
                      'unzip %s' % zip_name,
                      'sed s/name=\"maxTestCount\"\ value=\"200\"/name=\"maxTestCount\"\ value=\"0\"/ android-cts/repository/host_config.xml',
                      '/bin/bash android-cts/tools/startcts --device $(SERIAL) --plan CTS']

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                steps_host_pre=RUN_STEPS_HOST_PRE)
parser = lava_android_test.testdef.AndroidTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser)
