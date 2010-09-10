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

from abrek.dashboard import (DashboardConfig,
                             cmd_dashboard,
                             subcmd_dashboard_setup)
from imposters import ConfigImposter, OutputImposter
from fixtures import TestCaseWithFixtures


class DashboardTests(TestCaseWithFixtures):
    def setUp(self):
        super(DashboardTests, self).setUp()
        self.config = self.add_fixture(ConfigImposter())

    def test_dashboard_setup(self):
        server = "foo"
        user = "bar"
        passwd = "baz"
        args = ["setup", server, "-u", user, "-p", passwd]
        cmd = cmd_dashboard()
        cmd.main(argv=args)
        conf = DashboardConfig()
        self.assertEqual(server, conf.host)
        self.assertEqual(user, conf.user)
        self.assertEqual(passwd, conf.password)

class DashboardOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(DashboardOutputTests, self).setUp()
        self.out = self.add_fixture(OutputImposter())

    def test_dashboard_noserver(self):
        errmsg = "You must specify a server"
        cmd = subcmd_dashboard_setup()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())
