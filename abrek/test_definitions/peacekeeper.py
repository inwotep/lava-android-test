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
   results parsing for the Peacekeeper browser benchmark.

   http://clients.futuremark.com/peacekeeper/index.action
"""

import abrek.testdef
import os

curdir = os.path.realpath(os.path.dirname(__file__))

INSTALLSTEPS = ['cp -rf %s/peacekeeper/* .'%curdir]
RUNSTEPS = ['python peacekeeper.py firefox']
DEPS = ['python-ldtp','firefox']

my_installer = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, deps=DEPS)
my_runner = abrek.testdef.AbrekTestRunner(RUNSTEPS)

PATTERN = "^(?P<result>\w+): Score = (?P<measurement>\d+)"

my_parser = abrek.testdef.AbrekTestParser(PATTERN,
                                          appendall={'units':'point'})

testobj = abrek.testdef.AbrekTest(testname="peacekeeper", installer=my_installer,
                                  runner=my_runner, parser=my_parser)
