#!/usr/bin/python

# Copyright (c) 2010 Linaro
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
import pexpect

pattern = "Displayed org.zeroxlab.benchmark/.Report"
logcat_cmd = "adb logcat"
result = True
try:
    proc = pexpect.spawn(logcat_cmd, logfile=sys.stdout)
    id = proc.expect([pattern, pexpect.EOF])
    if id == 0:
        proc.sendcontrol('C')
except pexpect.TIMEOUT:
    print "0xbench Test: TIMEOUT Fail"
    result = False
finally:
    proc.sendcontrol('C')

if result:
    sys.exit(0)
else:
    sys.exit(1)