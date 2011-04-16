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
   results parsing for the Pybench test suite.
   The Pybench test Suite is an open source test suite that provides a
   standardized way to measure the performance of Python implementations.
"""

import abrek.testdef

VERSION='r27'
URL="http://svn.python.org/projects/python/tags/%s/Tools/pybench/" %(VERSION)

INSTALLSTEPS = ["svn export %s" %(URL)]
RUNSTEPS = ['python pybench/pybench.py']
DEPS = ['subversion']

my_installer = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, deps=DEPS)
my_runner = abrek.testdef.AbrekTestRunner(RUNSTEPS)

# test case name is first column and measurement is average column
#
#Test                             minimum  average  operation  overhead
#         BuiltinFunctionCalls:     85ms    151ms    0.30us    0.147ms
#         BuiltinMethodLookup:      68ms    113ms    0.11us    0.171ms

PATTERN = "^\s+(?P<test_case_id>\w+):\s+(\d+)ms\s+(?P<measurement>\d+)ms"

my_parser = abrek.testdef.AbrekTestParser(PATTERN,
                                          appendall={'units':'ms',
                                                     'result':'pass'})

testobj = abrek.testdef.AbrekTest(testname="pybench", installer=my_installer,
                                  runner=my_runner, parser=my_parser)
