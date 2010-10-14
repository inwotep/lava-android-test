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

# Run tests automatically, 500 repetitions each
gtkperf_options = "-a -c 500"

RUNSTEPS = ["LANG=C gtkperf %s" % gtkperf_options]

class GtkTestParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        PAT1 = "^(?P<test_case_id>\w+) - (?P<subtest>\w*\W*\w*) - time:\W+(?P<measurement>\d+\.\d+)"
        PAT2 = "^(?P<test_case_id>\w+) - time:\W+(?P<measurement>\d+\.\d+)"
        filename = "testoutput.log"
        pat1 = re.compile(PAT1)
        pat2 = re.compile(PAT2)
        with open(filename) as fd:
            for line in fd:
                match = pat1.search(line)
                if match:
                    d = match.groupdict()
                    d['test_case_id'] = "%s.%s" % (d['test_case_id'],
                        d['subtest'])
                    d.pop('subtest')
                    d['test_case_id'] = d['test_case_id'].replace(" ", "_")
                    self.results['test_results'].append(d)
                else:
                    match = pat2.search(line)
                    if match:
                        self.results['test_results'].append(match.groupdict())
        self.appendtoall({'units':'seconds', 'result':'pass'})

parse = GtkTestParser()
inst = abrek.testdef.AbrekTestInstaller(deps=["gtkperf"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)

testobj = abrek.testdef.AbrekTest(testname="gtkperf", installer=inst,
                                  runner=run, parser=parse)
