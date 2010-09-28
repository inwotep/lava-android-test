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
"""
   This script automates the automate installation, execution, and
   results parsing for the GMPbench test suite.
   The GMPbench test Suite is an open source test suite with the goal of
   comparing different processors performance against eachother.

"""

import re

import abrek.testdef

VERSION='0.2'
URL="ftp://ftp.gmplib.org/pub/misc/gmpbench-%s.tar.bz2" %(VERSION)
URL_gexpr="http://www.gmplib.org/gexpr.c"
DEPS = ['libgmp3-dev', 'wget']

INSTALLSTEPS = ['tar -xjf  gmpbench-0.2.tar.bz2',
                    'wget -c %s' %(URL_gexpr),
                    'mv gexpr.c gmpbench-0.2', 
                    'cd gmpbench-0.2 && gcc -o gexpr gexpr.c  -static -lm']
                       
RUNSTEPS = ['cd  gmpbench-0.2 && PATH=$PATH:. ./runbench ']
PATTERN = "\s*(?P<test_case_id>GMPbench\.*\w*\.*\w*):?\s*(?P<result>\d+.\d+)"

class GMPParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        filename = "testoutput.log"
        pat = re.compile(self.pattern)
        with open(filename) as fd:
            for line in fd:
                match = pat.match(line)
                if match:
                    results = match.groupdict()
                    self.results['test_results'].append(results)


gmpbenchinst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, deps=DEPS, 
                                                url=URL)
gmpbenchrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
gmpbenchparser = GMPParser(PATTERN)
testobj = abrek.testdef.AbrekTest(testname="gmpbench", installer=gmpbenchinst, 
                                  runner=gmpbenchrun, parser=gmpbenchparser)
