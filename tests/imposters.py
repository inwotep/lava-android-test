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
import sys
import tempfile
import StringIO

from lava_test.core.config import set_config


class OutputImposter(object):
    def setUp(self):
        self.origstdout = sys.stdout
        self.origstderr = sys.stderr
        sys.stdout = sys.stderr = self.fakestdout = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.origstdout
        sys.stderr = self.origstderr

    def getvalue(self):
        return self.fakestdout.getvalue()

class ConfigImposter(object):
    def setUp(self):
        class fakeconfig:
            def __init__(self, basedir):
                self.configdir = os.path.join(basedir, "config")
                self.installdir = os.path.join(basedir, "install")
                self.resultsdir = os.path.join(basedir, "results")
                self.registry =  {
                      "format": "LAVA Test Test Registry 1.0",
                      "providers": [
                          {
                              "entry_point": "lava_test.core.providers:BuiltInProvider"
                          },
                          {
                              "entry_point": "lava_test.core.providers:PkgResourcesProvider",
                              "config": {"namespace": "lava_test.test_definitions" }
                          },
                          {
                              "entry_point": "lava_test.core.providers:RegistryProvider",
                              "config": {
                                  "entries": []
                              }
                          }
                      ]
                }

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

