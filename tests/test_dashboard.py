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

import json
import os
from abrek.dashboard import (DashboardConfig,
                             cmd_dashboard,
                             subcmd_dashboard_bundle,
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

    def test_dashboard_setup_noserver(self):
        errmsg = "You must specify a server"
        cmd = subcmd_dashboard_setup()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_dashboard_bundle_badresult(self):
        errmsg = "Result directory not found"
        cmd = subcmd_dashboard_bundle()
        self.assertRaises(SystemExit, cmd.main, argv=['badresult'])
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_dashboard_bundle_noresult(self):
        errmsg = "You must specify a result"
        cmd = subcmd_dashboard_bundle()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())


class DashboardConfigOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(DashboardConfigOutputTests, self).setUp()
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())

    def test_dashboard_bundle_good(self):
        expected_dict = {
            "test_runs": [{
            "analyzer_assigned_date": "2010-10-10T00:00:00Z",
            "analyzer_assigned_uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "hw_context": {},
            "sw_context": {},
            "test_id": "stream",
            "test_results": [{
                    "measurement": "1111.1111",
                    "result": "pass",
                    "test_case_id": "Copy",
                    "units": "MB/s"
                },
                {
                    "measurement": "2222.2222",
                    "result": "pass",
                    "test_case_id": "Scale",
                    "units": "MB/s"
                },
                {
                    "measurement": "3333.3333",
                    "result": "pass",
                    "test_case_id": "Add",
                    "units": "MB/s"
                },
                {
                    "measurement": "4444.4444",
                    "result": "pass",
                    "test_case_id": "Triad",
                    "units": "MB/s"
                }],
            "time_check_performed": False
             }]
        }

        cmd = subcmd_dashboard_bundle()
        make_stream_result(self.config)
        cmd.main(argv=['stream000'])
        returned_dict = json.loads(self.out.getvalue())
        self.assertEqual(expected_dict, returned_dict)


def make_stream_result(config):
    """
    Make a fake set of test results for the stream test
    """
    testdata_data = """
{"test_runs": [{
    "analyzer_assigned_date": "2010-10-10T00:00:00Z",
    "analyzer_assigned_uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "hw_context": {},
    "sw_context": {},
    "test_id": "stream",
    "time_check_performed": false
    }]
}
"""
    testoutput_data = """
Function      Rate (MB/s)   Avg time     Min time     Max time
Copy:        1111.1111       0.0180       0.0112       0.0242
Scale:       2222.2222       0.0198       0.0122       0.0243
Add:         3333.3333       0.0201       0.0176       0.0223
Triad:       4444.4444       0.0197       0.0138       0.0223
"""
    result_dir = os.path.join(config.resultsdir, "stream000")
    os.makedirs(result_dir)
    with open(os.path.join(result_dir, "testdata.json"), "w") as fd:
        fd.write(testdata_data)
    with open(os.path.join(result_dir, "testoutput.log"), "w") as fd:
        fd.write(testoutput_data)
