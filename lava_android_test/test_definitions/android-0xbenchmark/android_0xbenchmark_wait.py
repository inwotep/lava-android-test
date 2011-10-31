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
import pexpect
import sys
import time

if len(sys.argv) == 1:
    adb_cmd = "adb"
else:
    adb_cmd = "adb -s %s" % (sys.argv[1])

logcat_cmd = '%s logcat' % (adb_cmd)
pattern = "Displayed org.zeroxlab.zeroxbenchmark/.Report"
try:
    proc = pexpect.spawn(logcat_cmd, logfile=sys.stdout)
    id = proc.expect([pattern, pexpect.EOF], timeout=2400)
    if id == 0:
        proc.sendcontrol('C')
except pexpect.TIMEOUT:
    print "0xbench Test: TIMEOUT Fail"
    sys.exit(1)
finally:
    proc.sendcontrol('C')

time.sleep(3)
sys.exit(0)
