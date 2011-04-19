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
from uuid import uuid1
from abrek.dashboard import (
    DashboardConfig,
    cmd_dashboard,
    )
from imposters import ConfigImposter, OutputImposter
from fixtures import TestCaseWithFixtures


class SetupTests(TestCaseWithFixtures):
    def setUp(self):
        super(SetupTests, self).setUp()
        self.config = self.add_fixture(ConfigImposter())

    def test_dashboard_setup(self):
        host, user, passwd = setup_dashboard()
        conf = DashboardConfig()
        self.assertEqual(host, conf.host)
        self.assertEqual(user, conf.user)
        self.assertEqual(passwd, conf.password)


class SetupOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(SetupOutputTests, self).setUp()
        self.out = self.add_fixture(OutputImposter())

    def test_dashboard_setup_noserver(self):
        errmsg = "You must specify a server"
        cmd = cmd_dashboard.cmd_setup()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())


class BundleOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(BundleOutputTests, self).setUp()
        self.out = self.add_fixture(OutputImposter())

    def test_dashboard_bundle_badresult(self):
        errmsg = "Result directory not found"
        cmd = cmd_dashboard.cmd_bundle()
        self.assertRaises(SystemExit, cmd.main, argv=['badresult'])
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_dashboard_bundle_noresult(self):
        errmsg = "You must specify a result"
        cmd = cmd_dashboard.cmd_bundle()
        self.assertRaises(SystemExit, cmd.main, argv=[])
        self.assertEqual(errmsg, self.out.getvalue().strip())

class BundleConfigOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(BundleConfigOutputTests, self).setUp()
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())

    def test_dashboard_bundle_good(self):
        cmd = cmd_dashboard.cmd_bundle()
        (testname, testuuid) = make_stream_result(self.config)
        expected_dict = {
            "format": "Dashboard Bundle Format 1.2",
            "test_runs": [{
            "analyzer_assigned_date": "2010-10-10T00:00:00Z",
            "analyzer_assigned_uuid": testuuid,
            "hardware_context": {
                "devices": []
            },
            "software_context": {},
            "test_id": "stream",
            "test_results": [{
                    "measurement": 1111.1111,
                    "result": "pass",
                    "test_case_id": "Copy",
                    "units": "MB/s",
                    "log_filename": "testoutput.log",
                    "log_lineno": 3
                },
                {
                    "measurement": 2222.2222,
                    "result": "pass",
                    "test_case_id": "Scale",
                    "units": "MB/s",
                    "log_filename": "testoutput.log",
                    "log_lineno": 4
                },
                {
                    "measurement": 3333.3333,
                    "result": "pass",
                    "test_case_id": "Add",
                    "units": "MB/s",
                    "log_filename": "testoutput.log",
                    "log_lineno": 5
                },
                {
                    "measurement": 4444.4444,
                    "result": "pass",
                    "test_case_id": "Triad",
                    "units": "MB/s",
                    "log_filename": "testoutput.log",
                    "log_lineno": 6
                }],
            "time_check_performed": False,
            "attachments": [
                {
                "mime_type": "text/plain",
                "pathname": "testoutput.log",
                "content": "CkZ1bmN0aW9uICAgICAgUmF0ZSAoTUIvcykgICBBdmcgdGltZSAgICAgTWluIHRpbWUgICAgIE1heCB0aW1lCkNvcHk6ICAgICAgICAxMTExLjExMTEgICAgICAgMC4wMTgwICAgICAgIDAuMDExMiAgICAgICAwLjAyNDIKU2NhbGU6ICAgICAgIDIyMjIuMjIyMiAgICAgICAwLjAxOTggICAgICAgMC4wMTIyICAgICAgIDAuMDI0MwpBZGQ6ICAgICAgICAgMzMzMy4zMzMzICAgICAgIDAuMDIwMSAgICAgICAwLjAxNzYgICAgICAgMC4wMjIzClRyaWFkOiAgICAgICA0NDQ0LjQ0NDQgICAgICAgMC4wMTk3ICAgICAgIDAuMDEzOCAgICAgICAwLjAyMjMK"
                }]
             }]
        }
        cmd.main(argv=[testname])
        returned_dict = json.loads(self.out.getvalue())
        self.assertEqual(expected_dict, returned_dict)


class PutConfigOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(PutConfigOutputTests, self).setUp()
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())

    def test_put_nosetup(self):
        testname, testuuid = make_stream_result(self.config)
        errmsg = "Error connecting to server, please run 'abrek dashboard " \
                "setup [host]'"
        args = ["put", "somestream", testname]
        cmd = cmd_dashboard()
        self.assertRaises(SystemExit, cmd.main, argv=args)
        self.assertEqual(errmsg, self.out.getvalue().strip())

    def test_put_badhost(self):
        testname, testuuid = make_stream_result(self.config)
        host, user, passwd = setup_dashboard(host = "http://badhost.foo")
        errmsg = "Unable to connect to host: [Errno -2] Name or service " \
                "not known"
        args = ["put", "somestream", testname]
        cmd = cmd_dashboard()
        self.assertRaises(SystemExit, cmd.main, argv=args)
        self.assertEqual(errmsg, self.out.getvalue().strip())


class PutOutputTests(TestCaseWithFixtures):
    def setUp(self):
        super(PutOutputTests, self).setUp()
        self.out = self.add_fixture(OutputImposter())

    def test_put_noargs(self):
        errmsg = "You must specify a stream and a result"
        cmd = cmd_dashboard()
        self.assertRaises(SystemExit, cmd.main, argv=["put"])
        self.assertEqual(errmsg, self.out.getvalue().strip())


def make_stream_result(config):
    """
    Make a fake set of test results for the stream test
    """
    testname = "stream000"
    testuuid = str(uuid1())
    testdata_data = """
{
"format": "Dashboard Bundle Format 1.2",
"test_runs": [{
    "analyzer_assigned_date": "2010-10-10T00:00:00Z",
    "analyzer_assigned_uuid": "%s",
    "hardware_context": {
        "devices": []
    },
    "software_context": {},
    "test_id": "stream",
    "time_check_performed": false,
    "test_results": []
    }]
}
""" % testuuid
    testoutput_data = """
Function      Rate (MB/s)   Avg time     Min time     Max time
Copy:        1111.1111       0.0180       0.0112       0.0242
Scale:       2222.2222       0.0198       0.0122       0.0243
Add:         3333.3333       0.0201       0.0176       0.0223
Triad:       4444.4444       0.0197       0.0138       0.0223
"""
    result_dir = os.path.join(config.resultsdir, testname)
    os.makedirs(result_dir)
    with open(os.path.join(result_dir, "testdata.json"), "w") as fd:
        fd.write(testdata_data)
    with open(os.path.join(result_dir, "testoutput.log"), "w") as fd:
        fd.write(testoutput_data)
    return (testname, testuuid)

def setup_dashboard(host="http://localhost:8080", user="foo", passwd="baz"):
    args = ["setup", host, "-u", user, "-p", passwd]
    cmd = cmd_dashboard()
    cmd.main(argv=args)
    return host, user, passwd
