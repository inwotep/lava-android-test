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
import StringIO

from abrek.config import set_config

class FakeOutputTests(object):
    def setUp(self):
        self.origstdout = sys.stdout
        sys.stdout = self.fakestdout = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.origstdout

    def getvalue(self):
        return self.fakestdout.getvalue()

class FakeConfigTests(object):
    def setUp(self):
        class fakeconfig:
            def __init__(self, basedir):
                self.configdir = os.path.join(basedir, "config")
                self.installdir = os.path.join(basedir, "install")
                self.resultsdir = os.path.join(basedir, "results")
        self.tmpdir = tempfile.mkdtemp()
        self.config = fakeconfig(self.tmpdir)
        set_config(self.config)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    @property
    def configdir(self):
        return self.config.configdir

    @property
    def installdir(self):
        return self.config.installdir

    @property
    def resultsdir(self):
        return self.config.resultsdir
