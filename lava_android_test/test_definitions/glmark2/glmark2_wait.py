#!/usr/bin/python

# Copyright (C) 2012 Linaro Limited

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
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
import pexpect
import sys
import time

if len(sys.argv) == 1:
    adb_cmd = "adb"
else:
    adb_cmd = "adb -s %s" % (sys.argv[1])

logcat_cmd = '%s logcat -v time' % (adb_cmd)
pattern1 = "glmark2 Score:"
#pattern1 = "\[loop\] fragment-steps=5:fragment-uniform=true:
#vertex-steps=5: FPS:"
pattern2 = "Process org.linaro.glmark2.+has died"
pattern3 = ("No suitable EGLConfig for GLES2.0 found."
            " Please check that proper GLES2.0 drivers are installed.")

try:
    proc = pexpect.spawn(logcat_cmd, logfile=sys.stdout)
    match_id = proc.expect([pattern1, pattern2, pattern3, pexpect.EOF],
                            timeout=1000)
    print "in glmark2_wait.py match_id = %s\n" % match_id
    if (match_id == 0) or (match_id == 1) or (match_id == 2):
        proc.sendcontrol('C')
except pexpect.TIMEOUT:
    print "glmark2 Test: TIMEOUT Fail\n"
    sys.exit(1)
finally:
    proc.sendcontrol('C')

time.sleep(3)
sys.exit(0)
