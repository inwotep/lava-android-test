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
from commands import getstatusoutput
# 'lava_android_test/test_definitions/android-0xbenchmark/'

source='ZeroxBench_Preference.xml'
target = '/data/data/org.zeroxlab.benchmark/shared_prefs/ZeroxBench_Preference.xml'

if len(sys.argv) == 1:
    cmd = 'adb push %s %s' % (source, target)
else:
    cmd = 'adb -s %s push %s %s' % (sys.argv[1], source, target)

rc, output = getstatusoutput(cmd)
if rc == 0:
    sys.exit(0)
else:
    print 'Failed to push file(%s) to file(%s): %s' % (source, target, output)
    sys.exit(1)