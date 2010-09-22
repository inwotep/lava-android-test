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

"""
   This script automates the automate installation, execution, and
   results parsing for the OpenPosix test suite.
   The POSIX Test Suite is an open source test suite with the goal of
   performing conformance, functional, and stress testing of the IEEE
   1003.1-2001 System Interfaces specification However the automation here
   does not support the stress test runs.

"""
import re
import abrek.testdef

VERSION="20100831"
URL= "http://downloads.sourceforge.net/project/ltp/LTP Source/ltp-%s/"\
     "ltp-full-%s.bz2" % (VERSION, VERSION)
MD5="6982c72429a62f3917c13b2d529ad1ce"
INSTALLSTEPS = ['tar -xjf ltp-full-20100831.bz2']
RUNSTEPS = ['cd ltp-full-20100831/testcases/open_posix_testsuite/ && make']

PATTERN = "((?P<test_case_id>\A(\w+[/]+)+\w+[-]*\w*[-]*\w*) .*? (?P<result>\w+))"
FIXUPS = {
            "FAILED"      :  "fail",
            "INTERRUPTED" :  "skip",
            "PASSED"      :  "pass",
            "UNRESOLVED"  :  "unknown",
            "UNSUPPORTED" :  "skip",
            "UNTESTED"    :  "skip",
            "SKIPPING"    :  "skip"
         }


class PosixParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        filename = "testoutput.log"
        pat = re.compile(self.pattern)
        with open(filename) as fd:
            for line in fd:
                match = pat.match(line)
                if match:
                    results = match.groupdict()
                    test_case_id = results['test_case_id']
                    results['test_case_id'] = test_case_id.replace("/", ".")
                    self.results['test_results'].append(results)
        if self.fixupdict:
            self.fixresults(self.fixupdict)

posix_inst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, url=URL, md5=MD5)
posix_run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
posixparser = PosixParser(PATTERN, fixupdict = FIXUPS)
testobj = abrek.testdef.AbrekTest(testname="posixtestsuite", version=VERSION,
                                  installer=posix_inst, runner=posix_run,
                                  parser=posixparser)
