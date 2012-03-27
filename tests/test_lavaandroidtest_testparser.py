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

from tests.fixtures import TestCaseWithFixtures
from tests.tests_util import makeparser


class testTestParser(TestCaseWithFixtures):

    def setUp(self):
        self.test_id = "ABC"

    def tearDown(self):
        os.unlink('stdout.log')

    def writeoutputlog(self, output_str):
        with open("stdout.log", "w") as fd:
            fd.write(output_str)

    def test_parse(self):
        pattern = "^(?P<testid>\w+):\W+(?P<result>\w+)"
        self.writeoutputlog("test001: pass")
        parser = makeparser(pattern)
        parser.parse()
        self.assertTrue(
            parser.results["test_results"][0]["testid"] == "test001" and
            parser.results["test_results"][0]["result"] == "pass")

    def test_fixupdict(self):
        pattern = "^(?P<testid>\w+):\W+(?P<result>\w+)"
        fixup = {"pass": "PASS"}
        self.writeoutputlog("test001: pass")
        parser = makeparser(pattern, fixupdict=fixup)
        parser.parse()
        self.assertEquals("PASS", parser.results["test_results"][0]["result"])

    def test_appendall(self):
        pattern = "^(?P<testid>\w+):\W+(?P<result>\w+)"
        append = {"units": "foo/s"}
        self.writeoutputlog("test001: pass")
        parser = makeparser(pattern, appendall=append)
        parser.parse()
        self.assertEqual("foo/s", parser.results["test_results"][0]["units"])
