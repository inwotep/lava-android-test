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

import hashlib
import os
import shutil
import tempfile
import unittest

from abrek.testdef import AbrekTestInstaller

class testAbrekTestInstaller(unittest.TestCase):
    def setUp(self):
        self.origdir = os.path.abspath(os.curdir)
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.abspath(__file__)
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.origdir)
        shutil.rmtree(self.tmpdir)

    def makeinstaller(self,**kwargs):
        return AbrekTestInstaller(**kwargs)

    def test_bad_download(self):
        url = "file:///xxxyyyzzz"
        installer = self.makeinstaller(url=url)
        self.assertRaises(RuntimeError, installer._download)

    def test_bad_md5(self):
        url = "file://%s" % self.filename
        installer = self.makeinstaller(url=url, md5='foo')
        self.assertRaises(RuntimeError, installer._download)

    def test_good_md5(self):
        url = "file://%s" % self.filename
        md5 = hashlib.md5(file(self.filename).read()).hexdigest()
        installer = self.makeinstaller(url=url, md5=md5)
        location = installer._download()
        self.assertTrue(os.path.exists(location))

    def test_runsteps(self):
        steps = ["echo test > foo"]
        installer = self.makeinstaller(steps=steps)
        installer._runsteps()
        self.assertTrue(os.path.exists("./foo"))
