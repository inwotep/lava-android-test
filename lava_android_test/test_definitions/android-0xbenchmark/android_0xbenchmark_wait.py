#!/usr/bin/python

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
import sys
import time

from lava_android_test.utils import stop_at_pattern

adb_cmd = "adb"
# here assumes that there is no serial number will start with '-'
# and the options passed are start with '-' as first option
if len(sys.argv) > 1 and (not sys.argv[1].startswith('-')):
    adb_cmd = "adb -s %s" % (sys.argv[1])

timeout = 2400
for index in range(1, len(sys.argv)):
    arg = sys.argv[index]
    if arg == '-timeout' and \
       (index + 1 < len(sys.argv)) and \
       sys.argv[index + 1]:
        try:
            timeout = int(sys.argv[index + 1])
        except ValueError:
            pass
        finally:
            break

logcat_cmd = '%s logcat' % (adb_cmd)
pattern = "Displayed org.zeroxlab.zeroxbenchmark/.Report"

if not stop_at_pattern(command=logcat_cmd, pattern=pattern, timeout=timeout):
    print "0xbench Test: TIMEOUT Fail"
    sys.exit(1)

time.sleep(3)
sys.exit(0)
