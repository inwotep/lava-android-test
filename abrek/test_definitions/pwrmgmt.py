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

import re

import abrek.testdef


INSTALLSTEPS = [' git clone git://git.linaro.org/people/torez/pm-qa.git ']
RUNSTEPS = [' cd pm-qa && awk -f testcases.awk  run_template ']

pwrmgmtinst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS)
pwrmgmtrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)

# test case name is between "pm-qa-"  and  ":"  and results and/or measurements are rest of the line
PATTERN = "^pm-qa-(?P<test_case_id>\w+):\s+(?P<message>.*)"


pwrmgmtparser = abrek.testdef.AbrekTestParser(PATTERN, appendall={'result':'pass'})

testobj = abrek.testdef.AbrekTest(testname="pwrmgmt", installer=pwrmgmtinst,
                                  runner=pwrmgmtrun, parser=pwrmgmtparser)
