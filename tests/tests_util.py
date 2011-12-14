#!/usr/bin/env python
#
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
import os
import stat
import subprocess
from lava_android_test.testdef import AndroidTest, AndroidTestInstaller, AndroidTestRunner, AndroidTestParser

def maketest(name="foo", version="", installer=None, runner=None, parser=None):
    if installer is None:
        installer = makeinstaller()
    return AndroidTest(name, version, installer, runner, parser)

def makerunner(**kwargs):
    return AndroidTestRunner(**kwargs)

def makeinstaller(**kwargs):
    return AndroidTestInstaller(**kwargs)

def makeparser(*args, **kwargs):
        return AndroidTestParser(*args, **kwargs)

test_tmp = '/tmp/lava-android-test-tmp'
def fake_adb(output_str='', target_path=test_tmp, ret_code=0):
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    fake_adb_path = os.path.join(target_path, 'adb')
    adb_file = open(fake_adb_path, 'w')
    adb_file.write('#/bin/bash\n')
    adb_file.write('if [ "$2" == "chmod" ]; then\n')
    adb_file.write('\texit 0\n')
    adb_file.write('fi\n')
    if output_str is None  or output_str == '':
        pass
    else:
        adb_file.write('echo \'\n')
        adb_file.write(output_str)
        adb_file.write('\'\n')
    adb_file.write('exit %s\n' % ret_code)
    adb_file.close()
    os.chmod(fake_adb_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    os.chmod(target_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    os.environ['PATH'] = target_path + ':' + os.environ['PATH']

def clear_fake(target_path=test_tmp):
    if not os.path.exists(target_path):
        return
    if os.path.isdir(target_path):
        for sub_path in os.listdir(target_path):
            clear_fake(os.path.join(target_path, sub_path))
        os.rmdir(target_path)
    else:
        os.unlink(target_path)

def main():
    fake_adb('hello, \ntest');
    cmd = 'adb shell ls'
    p = subprocess.Popen(cmd, shell=True)
    p.wait()
    clear_fake()

if __name__ == '__main__':
    main()
