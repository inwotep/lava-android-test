import os
import shutil
import sys
import tempfile
import unittest
import StringIO

import abrek.builtins
from abrek.config import set_config

class FakeOutputTests(unittest.TestCase):
    def setUp(self):
        self.origstdout = sys.stdout
        sys.stdout = self.fakestdout = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.origstdout

class ListKnown(FakeOutputTests):
    def test_list_tests(self):
        cmd = abrek.builtins.cmd_list_tests()
        cmd.run()
        self.assertTrue("stream" in self.fakestdout.getvalue())

class FakeConfigTests(FakeOutputTests):
    def setUp(self):
        super(FakeConfigTests, self).setUp()
        class fakeconfig:
            def __init__(self, basedir):
                self.configdir = os.path.join(basedir, "config")
                self.installdir = os.path.join(basedir, "install")
                self.resultsdir = os.path.join(basedir, "results")
        self.tmpdir = tempfile.mkdtemp()
        self.config = fakeconfig(self.tmpdir)
        set_config(self.config)

    def tearDown(self):
        super(FakeConfigTests, self).tearDown()
        shutil.rmtree(self.tmpdir)

    def test_list_installed(self):
        test_name="test_list_installed000"
        os.makedirs(os.path.join(self.config.installdir, test_name))
        cmd = abrek.builtins.cmd_list_installed()
        cmd.run()
        self.assertTrue(test_name in self.fakestdout.getvalue())

    def test_list_results(self):
        result_name = "test_list_results000"
        os.makedirs(os.path.join(self.config.resultsdir, result_name))
        cmd = abrek.builtins.cmd_list_results()
        cmd.run()
        self.assertTrue(result_name in self.fakestdout.getvalue())
