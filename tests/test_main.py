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

from abrek.main import main
from imposters import OutputImposter
from fixtures import TestCaseWithFixtures


class testMain(TestCaseWithFixtures):
    def setUp(self):
        super(testMain, self).setUp()
        self.out = self.add_fixture(OutputImposter())

    def test_bad_subcmd(self):
        # Running a subcommand that does not exist of a command that does
        # gives a nice error message.
        errmsg = "foo not found as a sub-command of results\n"
        main(['./abrek', 'results', 'foo'])
        self.assertEqual(errmsg, self.out.getvalue())

