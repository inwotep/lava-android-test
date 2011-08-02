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

import abrek.testdef

RUNSTEPS = ['adb shell monkey -s 1 --pct-touch 10 --pct-motion 20 --pct-nav 20 --pct-majornav 30 --pct-appswitch 20 --throttle 500 500']
#PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"
PATTERN = "## Network stats: elapsed time=(?P<measurement>\d+)ms"
FAILURE_PATTERNS = ['\*\* Monkey aborted due to error.',
                    '\*\* System appears to have crashed']

streaminst = abrek.testdef.AbrekTestInstaller()
streamrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
streamparser = abrek.testdef.AbrekTestParser(PATTERN,
               appendall={'units':'ms'}, failure_patterns=FAILURE_PATTERNS)
testobj = abrek.testdef.AbrekTest(testname="android-monkey", installer=streaminst,
                                  runner=streamrun, parser=streamparser)