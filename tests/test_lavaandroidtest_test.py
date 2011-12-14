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

import re, os
import subprocess
from lava_android_test.config import get_config
from lava_android_test.adb import ADB
from tests.imposters import ConfigImposter, OutputImposter
from tests.fixtures import TestCaseWithFixtures
from tests.tests_util import maketest, makerunner, test_tmp, clear_fake, \
    fake_adb

class FakeAdb(ADB):
    def __init__(self):
        super(FakeAdb, self).__init__()
        self.tmp_dir = test_tmp
        if not os.path.exists(test_tmp):
            os.makedirs(test_tmp)

    def shell(self, command=None, stdout=None, stderr=None):
        if command.startswith('mkdir'):
            dir_path = command[len('mkdir '):]
            try:
                os.mkdir('%s/%s' % (test_tmp, dir_path))
            except:
                return 1
            return 0
        elif command.startswith('ls'):
            dir_path = command[len('ls '):]
            real_path = '%s/%s' % (test_tmp, dir_path)
            if os.path.exists(real_path):
                return 0
            else:
                return 1
        elif command.startswith('rm -r'):
            dir_path = command[len('rm -r '):]
            proc = subprocess.Popen('rm -fr %s/%s' % (test_tmp, dir_path), shell=True)
            return proc.wait()
        else:
            return 0

fake_output_str = '''[ro.build.display.id]: [sdk-eng 4.0.1 ICS_MR0 202595 test-keys]
RET_CODE=0'''
class TestAndroidTest(TestCaseWithFixtures):
    def setUp(self):
        super(TestAndroidTest, self).setUp()
        self.config = self.add_fixture(ConfigImposter())
        self.out = self.add_fixture(OutputImposter())
        clear_fake()

    def tearDown(self):
        clear_fake()

    def test_run(self):
        config = get_config()
        test_name = 'foo'
        clear_fake()
        testrunner = makerunner(steps_host_pre=["echo foo"])
        test = maketest(name=test_name, runner=testrunner)
        real_installed_path = '%s/%s/%s' % (test_tmp, config.installdir_android, test_name)
        test.setadb(FakeAdb())
        self.assertFalse(os.path.exists(real_installed_path))
        test.install()
        self.assertTrue(os.path.exists(real_installed_path))

        fake_adb(output_str=fake_output_str)
        result_id = test.run()
        self.assertTrue("LAVA: (stdout) foo" in self.out.getvalue())

        result_id_pattern = "foo\d+\.\d+"
        self.assertTrue(re.match(result_id_pattern, result_id))
        self.assertTrue("LAVA: (stdout) foo" in self.out.getvalue())

        test.uninstall()

        self.assertFalse(os.path.exists(real_installed_path))
