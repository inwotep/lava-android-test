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
import time
from lava_android_test.adb import ADB

adb = ADB(sys.argv[1])

source='ZeroxBench_Preference.xml'
target = '/data/data/org.zeroxlab.benchmark/shared_prefs/ZeroxBench_Preference.xml'
(ret, target)=adb.push(source, target)
if ret == 0:
    sys.exit(0)
else:
    print 'Failed to push file(%s) to file(%s)' % (source, target)
    sys.exit(1)