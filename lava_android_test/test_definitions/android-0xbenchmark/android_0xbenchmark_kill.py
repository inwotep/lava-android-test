#!/usr/bin/python

# Copyright (c) 2011 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
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

import re
import sys
import time
from commands import getstatusoutput

if len(sys.argv) == 1:
    adb_cmd = "adb"
else:
    adb_cmd = "adb -s %s" % (sys.argv[1])

def back():
    back_cmd = '%s shell input keyevent 4' % (adb_cmd)
    rc, output = getstatusoutput(back_cmd)
    if rc != 0:
        print 'Failed to execute command %s:%s' % (back_cmd, output)
        sys.exit(1)
back()
back()
back()

##app_76    861   80    165896 28848 ffffffff afd0eb18 S org.zeroxlab.zeroxbenchmark
pattern = re.compile('^\S+\s+(?P<pid>\d+?)\s+.*org\.zeroxlab\.zeroxbenchmark\s*$')
while True:
    pscmd = '%s shell ps' % (adb_cmd)
    rc, output = getstatusoutput(pscmd)
    if rc != 0:
        print 'Failed to get process information about org.zeroxlab.zeroxbenchmark:%s' % output
        sys.exit(1)
    pid = None
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            pid = match.group('pid')
            break

    if pid is None:
       sys.exit(0)

    killcmd = '%s shell kill %s' % (adb_cmd, pid)
    rc, output = getstatusoutput(killcmd)
    if rc != 0:
        print 'Failed to kill process(%s):%s' % (pid, output)
        sys.exit(1)
    time.sleep(2)
