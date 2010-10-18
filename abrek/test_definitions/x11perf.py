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
#

import abrek.testdef

x11perf_options = "-repeat 3"

x11perf_tests = [
    # Antialiased text (using XFT)
    "-aa10text",
    "-aa24text",

    # Antialiased drawing (using XRENDER)
    "-aatrapezoid300",
    "-aatrap2x300",

    # Normal blitting
    "-copypixwin500",
    "-copypixpix500",

    # Composited blitting
    "-comppixwin500",

    # SHM put image
    "-shmput500",
    "-shmputxy500",

    "-scroll500",
    ]

RUNSTEPS = ["x11perf %s %s" % (x11perf_options,  " ".join(x11perf_tests))]
PATTERN = "trep @.*\(\W*(?P<measurement>\d+.\d+)/sec\):\W+(?P<test_case_id>.+)"

inst = abrek.testdef.AbrekTestInstaller(deps=["x11-apps"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
parse = abrek.testdef.AbrekTestParser(PATTERN,
                                      appendall={'units':'reps/s',
                                                 'result':'pass'})

testobj = abrek.testdef.AbrekTest(testname="x11perf", installer=inst,
                                  runner=run, parser=parse)
