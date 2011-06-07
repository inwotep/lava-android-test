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

from abrek.testdef import AbrekTest, AbrekTestInstaller, AbrekTestRunner
from imposters import OutputImposter, ConfigImposter
from fixtures import TestCaseWithFixtures

def maketest(name="foo", version="", installer=None, runner=None, parser=None):
    if installer is None:
        installer = makeinstaller()
    return AbrekTest(name, version, installer, runner, parser)

def makerunner(**kwargs):
    return AbrekTestRunner(**kwargs)

def makeinstaller(**kwargs):
    return AbrekTestInstaller(**kwargs)

class AbrekTestConfigOutput(TestCaseWithFixtures):
    def setUp(self):
        super(AbrekTestConfigOutput, self).setUp()
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())

    def test_run(self):
        testrunner = makerunner(steps=["echo foo"])
        test = maketest(name="foo", runner=testrunner)
        test.install()
        test.run()
        self.assertEqual("foo", self.out.getvalue().splitlines()[0])
        completion_message = self.out.getvalue().splitlines()[1]
        completion_pattern = "ABREK TEST RUN COMPLETE: Result id is 'foo\d+\.0'"
        self.assertTrue(re.match(completion_pattern, completion_message))

