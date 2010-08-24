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
