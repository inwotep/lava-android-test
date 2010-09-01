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

import abrek.builtins
from faketests import FakeConfigTests, FakeOutputTests
from fixtures import TestCaseWithFixtures

class ListKnown(TestCaseWithFixtures):
    def test_list_tests(self):
        out = self.add_fixture(FakeOutputTests())
        cmd = abrek.builtins.cmd_list_tests()
        cmd.run()
        self.assertTrue("stream" in out.getvalue())
        self.cleanup()

class ListInstalled(FakeConfigTests):
    def test_list_installed(self):
        config = self.add_fixture(FakeConfigTests())
        out = self.add_fixture(FakeOutputTests())
        test_name="test_list_installed000"
        os.makedirs(os.path.join(self.installdir, test_name))
        cmd = abrek.builtins.cmd_list_installed()
        cmd.run()
        self.assertTrue(test_name in out.getvalue())
        self.cleanup()
