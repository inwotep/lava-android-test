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

import os
import shutil
import tempfile
import unittest
from datetime import datetime

from abrek.testdef import AbrekTestRunner
from imposters import OutputImposter
from fixtures import TestCaseWithFixtures

def makerunner(**kwargs):
    return AbrekTestRunner(**kwargs)

class testAbrekTestRunner(unittest.TestCase):
    def setUp(self):
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def test_starttime(self):
        runner = makerunner()
        runner.run(self.tmpdir)
        self.assertTrue(isinstance(runner.starttime, datetime))

    def test_endtime(self):
        runner = makerunner()
        runner.run(self.tmpdir)
        self.assertTrue(isinstance(runner.endtime, datetime))

    def test_timediff(self):
        steps = ['sleep 2']
        runner = makerunner(steps=steps)
        runner.run(self.tmpdir)
        self.assertNotEqual(runner.starttime, runner.endtime)

    def test_runsteps(self):
        steps = ["echo test > foo"]
        runner = makerunner(steps=steps)
        runner._runsteps(self.tmpdir)
        self.assertTrue(os.path.exists("./foo"))

    def test_logoutput(self):
        steps = ["echo test > foo"]
        runner = makerunner(steps=steps)
        runner._runsteps(self.tmpdir)
        self.assertTrue(os.path.exists("./testoutput.log"))

class testAbrekTestRunnerVerbosity(TestCaseWithFixtures):
    def setUp(self):
        super(testAbrekTestRunnerVerbosity, self).setUp()
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)
        self.out = self.add_fixture(OutputImposter())

    def tearDown(self):
        super(testAbrekTestRunnerVerbosity, self).tearDown()
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def test_runsteps_quiet_true(self):
        steps = ["echo test"]
        runner = makerunner(steps=steps)
        runner._runsteps(self.tmpdir, quiet=True)
        self.assertEqual("", self.out.getvalue().strip())

    def test_runsteps_quiet_false(self):
        steps = ["echo test"]
        runner = makerunner(steps=steps)
        runner._runsteps(self.tmpdir, quiet=False)
        self.assertEqual("test", self.out.getvalue().strip())

    def test_run_quiet_true(self):
        steps = ["echo test"]
        runner = makerunner(steps=steps)
        runner.run(self.tmpdir, quiet=True)
        self.assertEqual("", self.out.getvalue().strip())

    def test_run_quiet_false(self):
        steps = ["echo test"]
        runner = makerunner(steps=steps)
        runner.run(self.tmpdir, quiet=False)
        self.assertEqual("test", self.out.getvalue().strip())
