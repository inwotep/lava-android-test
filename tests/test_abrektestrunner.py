import os
import shutil
import tempfile
import unittest
from datetime import datetime

from abrek.testdef import AbrekTestRunner

class testAbrekTestInstaller(unittest.TestCase):
    def setUp(self):
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def makerunner(self,**kwargs):
        return AbrekTestRunner(**kwargs)

    def test_starttime(self):
        runner = self.makerunner()
        runner.run(self.tmpdir)
        self.assertTrue(isinstance(runner.starttime, datetime))

    def test_endtime(self):
        runner = self.makerunner()
        runner.run(self.tmpdir)
        self.assertTrue(isinstance(runner.endtime, datetime))

    def test_timediff(self):
        steps = ['sleep 2']
        runner = self.makerunner(steps=steps)
        runner.run(self.tmpdir)
        self.assertNotEqual(runner.starttime, runner.endtime)

    def test_runsteps(self):
        steps = ["echo test > foo"]
        runner = self.makerunner(steps=steps)
        runner._runsteps(self.tmpdir)
        self.assertTrue(os.path.exists("./foo"))

    def test_logoutput(self):
        steps = ["echo test > foo"]
        runner = self.makerunner(steps=steps)
        runner._runsteps(self.tmpdir)
        self.assertTrue(os.path.exists("./testoutput.log"))
