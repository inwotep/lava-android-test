# Copyright (c) 2010, 2011 Linaro
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

import os
import shutil
import tempfile
from datetime import datetime
from tests.tests_util import makerunner
from tests.imposters import OutputImposter, ConfigImposter
from tests.fixtures import TestCaseWithFixtures

class testTestRunner(TestCaseWithFixtures):
    def setUp(self):
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)
        self.test_id = "ABC"

    def tearDown(self):
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def test_starttime(self):
        runner = makerunner()
        runner.run('./')
        self.assertTrue(isinstance(runner.starttime, datetime))

    def test_endtime(self):
        runner = makerunner()
        runner.run('./')
        self.assertTrue(isinstance(runner.endtime, datetime))

    def test_timediff(self):
        steps = ['sleep 2']
        runner = makerunner(steps_host_pre=steps)
        runner.run('./')
        self.assertNotEqual(runner.starttime, runner.endtime)

    def test_runsteps(self):
        steps = ["echo test > foo"]
        runner = makerunner(steps_host_pre=steps)
        runner.run('./')
        self.assertTrue(os.path.exists("./foo"))

    def test_logoutput(self):
        steps = ["echo test"]
        runner = makerunner(steps_host_pre=steps)
        runner.run('./')
        self.assertTrue('test' in self.out.getvalue())

