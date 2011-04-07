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
import unittest

import abrek.swprofile
from abrek.utils import fake_file, clear_fakes


class Version:
    def __init__(self, version):
        self.version = version

class Package:
    def __init__(self, name, version, is_installed=True):
        self.is_installed = is_installed
        self.name = name
        self.installed = Version(version)

class AptCache:
    def __init__(self, packages=[]):
        self.packages = packages

    def __iter__(self):
        return iter(self.packages)

class SwprofileTests(unittest.TestCase):
    def setUp(self):
        self.lsb_desc = 'test description'
        self.lsb_information = {'DESCRIPTION':self.lsb_desc}
        self.testpackage = Package('testpkg', '7.77')
        self.cache = AptCache([self.testpackage])

    def make_profile(self, cache=None, info=None):
        if cache == None:
            cache = self.cache
        if info == None:
            info = self.lsb_information
        return abrek.swprofile.get_software_context(apt_cache=cache,
                lsb_information=info)

    def test_pkg_name(self):
        a = self.make_profile()
        for pkg in a['packages']:
            self.assertEqual(self.testpackage.name, pkg['name'])

    def test_pkg_version(self):
        a = self.make_profile()
        for pkg in a['packages']:
            self.assertEqual(self.testpackage.installed.version, pkg['version'])

    def test_image_name_lsb(self):
        a = self.make_profile()
        if os.path.exists('/etc/buildstamp'):
            return
        self.assertEqual(self.lsb_desc, a['image']['name'])

    def test_image_name_buildstamp(self):
        BUILDSTAMP = "linaro-m-headless-20101101-0"
        BUILDSTAMPFILE = "lexbuild6 Mon, 01 Nov 2010 02:11:39 -0400\n%s" % (
                         BUILDSTAMP)
        fake_file('/etc/buildstamp', BUILDSTAMPFILE)
        a = self.make_profile()
        clear_fakes()
        self.assertEqual(BUILDSTAMP, a['image']['name'])

