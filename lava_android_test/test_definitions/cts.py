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
"""
This test executes the Android Compatibility Test Suite (CTS) to verify if
a given build meets all the criteria.

**URL:** http://source.android.com/compatibility/cts-intro.html

**Default Options:** None
"""

import os

from lava_android_test.testdef import (Attachment,
                                       AndroidTest,
                                       AndroidTestInstaller,
                                       AndroidTestRunner,
                                       AndroidTestParser)

test_name = 'cts'

curdir = os.path.realpath(os.path.dirname(__file__))

RUN_STEPS_HOST_PRE = ['python %s/cts/cts_wrapper.py $(SERIAL) $(OPTIONS)' % (
                                            curdir)]

inst = AndroidTestInstaller()
run = AndroidTestRunner(steps_host_pre=RUN_STEPS_HOST_PRE)

#01-16 14:24:16 I/0123456789ABCDEF: android.telephony.cts.
#TelephonyManagerTest#testGetNetworkCountryIso PASS
pattern = ("\s*[\d-]+\s+[\d:]+\s+I\/\S+\:\s+(?P<test_case_id>\S+#\S+)"
           "\s+(?P<result>\S+)\s*$")
parser = AndroidTestParser(pattern=pattern,
                           fixupdict={'PASS': 'pass', 'FAIL': 'fail'})

attachments = [
        Attachment(pathname="/data/local/tmp/logcat.log",
               mime_type="text/plain"),
        Attachment(pathname="/data/local/tmp/kmsg.log",
               mime_type="text/plain"),
        Attachment(pathname="/data/local/tmp/cts-results.zip",
               mime_type="application/zip"),
        Attachment(pathname="/data/local/tmp/device_logcat.zip",
               mime_type="application/zip"),
        Attachment(pathname="/data/local/tmp/host_log.zip",
               mime_type="application/zip")
        ]
testobj = AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser,
                                                attachments=attachments)
