# Copyright (c) 2011 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
#
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
"""
Performs a test of monkey functionality in Android with some 
black list packages provided.

**URL:** http://android.git.linaro.org/gitweb?p=platform/development.git;a=blob;f=cmds/monkey/monkey

**Default options:** "generic_target"
"""
import os
import lava_android_test.testdef
from lava_android_test.config import get_config

test_name = 'monkey_long_run'
config = get_config()
curdir = os.path.realpath(os.path.dirname(__file__))
monkey_sh_name = 'monkey_long_run.sh'
monkey_sh_path = os.path.join(curdir, test_name, monkey_sh_name)
monkey_sh_android_path = os.path.join(config.installdir_android,
                                      test_name, monkey_sh_name)
monkey_blacklist_name = 'package_black_list'
monkey_blacklist_path = os.path.join(curdir, test_name, monkey_blacklist_name)
monkey_blacklist_android_path = os.path.join(config.installdir_android,
                                      test_name, monkey_blacklist_name)
juice_monkey_blacklist_name = 'juice_package_black_list'
juice_monkey_blacklist_path = os.path.join(curdir, test_name,
                                           juice_monkey_blacklist_name)
juice_monkey_blacklist_android_path = os.path.join(config.installdir_android,
                                                   test_name,
                                                   juice_monkey_blacklist_name)

DEFAULT_OPTIONS = 'generic_target'
INSTALL_STEPS_ADB_PRE = ['push %s %s ' % (monkey_sh_path,
                                          monkey_sh_android_path),
                         'push %s %s ' % (monkey_blacklist_path,
                                          monkey_blacklist_android_path),
                         'push %s %s ' % (juice_monkey_blacklist_path,
                                          juice_monkey_blacklist_android_path),
                         'shell chmod 777 %s' % monkey_sh_android_path]

ADB_SHELL_STEPS = ['%s $(OPTIONS) %s %s' % (monkey_sh_android_path,
                   juice_monkey_blacklist_android_path,
                   monkey_blacklist_android_path)]
#PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"
PATTERN = "## Network stats: elapsed time=(?P<measurement>\d+)ms"
FAILURE_PATTERNS = []
FAILURE_PATTERNS = ['\*\* Monkey aborted due to error.',
                    '\*\* System appears to have crashed']

inst = lava_android_test.testdef.AndroidTestInstaller(
                                    steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS)
parser = lava_android_test.testdef.AndroidTestParser(PATTERN,
               appendall={'units': 'ms'}, failure_patterns=FAILURE_PATTERNS)
testobj = lava_android_test.testdef.AndroidTest(
                                    testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser,
                                    default_options=DEFAULT_OPTIONS)
