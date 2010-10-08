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

RUNSTEPS = ["glmemperf -e shmimage"]
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+) fps"

inst = abrek.testdef.AbrekTestInstaller(deps=["glmemperf"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
parse = abrek.testdef.AbrekTestParser(PATTERN,
                                      appendall={'units':'fps',
                                                 'result':'pass'})

testobj = abrek.testdef.AbrekTest(testname="glmemperf", installer=inst,
                                  runner=run, parser=parse)
