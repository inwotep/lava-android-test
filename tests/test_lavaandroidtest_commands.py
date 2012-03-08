# Copyright (c) 2011 Linaro
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

import re
from tests.tests_util import fake_adb, clear_fake

from tests.imposters import ConfigImposter, OutputImposter
from tests.fixtures import TestCaseWithFixtures
from lava_android_test.main import LAVAAndroidTestDispatcher


class LavaTestCommandTestCase(TestCaseWithFixtures):
    def setUp(self):
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())
        clear_fake()

    def tearDown(self):
        clear_fake()

    def _runLavaTest(self, cmds):
        LAVAAndroidTestDispatcher().dispatch(cmds)


class BadCommand(LavaTestCommandTestCase):
    def test_bad_cmd(self):
        # Running an unknown command that does not exist of a command that does
        # gives a nice error message.
        errmsg = "invalid choice: 'results'"

        self.assertRaises(SystemExit, LAVAAndroidTestDispatcher().dispatch,
                          ['results', 'foo'])
        self.assertNotEqual(None, re.search(errmsg, self.out.getvalue()),
                             re.MULTILINE)
        self.assertTrue(errmsg in self.out.getvalue())


class ListKnown(LavaTestCommandTestCase):
    def test_list_tests(self):
        self._runLavaTest(['list-tests'])
        self.assertTrue("monkey" in self.out.getvalue())

dir_list_info = '''monkey
0xbench
RET_CODE=0'''


class ListInstalled(LavaTestCommandTestCase):
    def test_list_installed(self):
        # test_name must be in the BuiltInProvider._builtin_tests
        fake_adb(output_str=dir_list_info)
        test_name = "monkey"
        self._runLavaTest(['list-installed'])
        self.assertTrue(test_name in self.out.getvalue())
        clear_fake()

devices_list_info = '''List of devices attached
192.168.1.109:5555    device
'''


class ListDevices(LavaTestCommandTestCase):
    def test_list_devices(self):
        # test_name must be in the BuiltInProvider._builtin_tests
        fake_adb(output_str=devices_list_info)
        self._runLavaTest(['list-devices'])
        self.assertTrue('192.168.1.109:5555    device' in self.out.getvalue())
        clear_fake()


class RunTest(LavaTestCommandTestCase):
    def test_run_command_test_not_install(self):
        errmsg = 'ERROR: The test (abc) has not been installed yet.'
        fake_adb(output_str='RET_CODE=1')
        ret_code = LAVAAndroidTestDispatcher().dispatch(['run', 'abc'])
        self.assertEqual(1, ret_code)
        self.assertTrue(errmsg in self.out.getvalue())
        clear_fake()

    def test_run_command_test_not_exist(self):
        errmsg = "unknown test 'abc'"
        fake_adb(output_str='RET_CODE=0')
        self.assertRaises(SystemExit, LAVAAndroidTestDispatcher().dispatch,
                           ['run', 'abc'])
        self.assertNotEqual(None, re.search(errmsg, self.out.getvalue()),
                             re.MULTILINE)
        self.assertTrue(errmsg in self.out.getvalue())


class TestHelp(LavaTestCommandTestCase):
    def test_command_help(self):
        self.assertRaises(SystemExit, LAVAAndroidTestDispatcher().dispatch,
                           ['--help'])
        self.assertTrue("--help" in self.out.getvalue())
