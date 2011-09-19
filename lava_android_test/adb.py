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
import re
import subprocess
import tempfile
from lava_android_test.config import get_config

config = get_config()
class ADB(object):
    ERR_CHMOD = 260
    ERR_WRAPPER = 300
    ERR_SHELL = 350
    ERR_PUSH = 400
    ERR_INSTALL = 450
    ERR_UNINSTALL = 450
    adb = 'adb'
    serial = None

    target_dir = config.tempdir_android

    def __init__(self, serial=None):
        if serial is not None:
            self.serial = serial
            self.adb = 'adb -s %s' % serial

    def push(self, source=None, target=None):
        if source is None:
            return -1

        target_dir = self.target_dir
        if target is None:
            target = os.path.join(self.target_dir, os.path.basename(source))
        else:
            target_dir = os.path.dirname(target)


        subprocess.Popen('%s shell mkdir %s' % (self.adb, target_dir), shell=True, stdout=subprocess.PIPE)
        s = subprocess.Popen('%s push %s %s' % (self.adb, source, target), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = s.wait()
        return (ret, target)

    def pull(self, source=None, target=None):
        if source is None:
            return -1

        if target is None:
            s = subprocess.Popen('%s pull %s' % (self.adb, source), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            s = subprocess.Popen('%s pull %s %s' % (self.adb, source, target), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return s.wait()

    def shell(self, command=None, stdout=None, stderr=None):
        if command is None:
            return 0

        tmpdir = config.tempdir_host
        if not os.path.exists(tmpdir):
            os.mkdir(tmpdir)
        (tmpshell, tmpshell_name) = tempfile.mkstemp(suffix='.sh', prefix='lava-android-test', dir=tmpdir)
        tmpfile_path = os.path.join(tmpdir, tmpshell_name)
        os.write(tmpshell, '#/system/bin/sh\n')
        os.write(tmpshell, 'base=/system\n')
        os.write(tmpshell, 'export PATH=/sbin:/vendor/bin:/system/sbin:/system/bin:/system/xbin\n')
        org_cmd = command
        if stdout is not None:
            command = '%s 1>>%s' % (command, stdout)
        if stderr is not None:
            command = '%s 2>>%s' % (command, stderr)

        os.write(tmpshell, command + '\n')
        os.write(tmpshell, 'RET_CODE=$?\n')
        if stdout is not None:
            os.write(tmpshell, 'echo ANDROID_TEST_COMMAND="%s">>%s\n' % (org_cmd, stdout))
            os.write(tmpshell, 'echo ANDROID_TEST_RET_CODE=${RET_CODE} >>%s\n' % (stdout))

        os.write(tmpshell, 'echo RET_CODE=${RET_CODE}\n')
        os.close(tmpshell)

        (ret_code, target_path) = self.push(tmpfile_path)
        os.remove(tmpfile_path)
        if ret_code != 0:
            return self.ERR_PUSH

        s = subprocess.Popen('%s shell chmod 777 %s' % (self.adb, target_path), shell=True, stdout=subprocess.PIPE)
        ret_code = s.wait()
        if ret_code != 0:
            return self.ERR_CHMOD + ret_code
        #check the whether the output is empty
        if len(s.stdout.readlines()) != 0:
            return self.ERR_CHMOD

        s = subprocess.Popen('%s shell %s' % (self.adb, target_path), shell=True, stdout=subprocess.PIPE)
        ret_code = s.wait()
        if ret_code != 0:
            return self.ERR_SHELL + ret_code
        subprocess.Popen('%s shell rm %s' % (self.adb, target_path), shell=True, stdout=subprocess.PIPE)
        #check the whether the output is empty
        output = s.stdout.readlines()
        ret_code_line = output[len(output) - 1]
        ret_code_pattern = "^RET_CODE=(?P<ret_code>\d+)\s*$"
        pat = re.compile(ret_code_pattern)
        match = pat.search(ret_code_line)
        if not match:
            return self.ERR_SHELL
        else:
            data = match.groupdict()
            return int(data['ret_code'], 10)

    def exists(self, path):
        ret_code = self.shell("ls %s" % path)
        return ret_code == 0

    def installapk(self, apkpath):
        s = subprocess.Popen('%s install %s' % (self.adb, apkpath), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret_code = s.wait()
        if ret_code != 0:
            return self.ERR_INSTALL + ret_code
        return 0

    def uninstallapk(self, package):
        s = subprocess.Popen('%s uninstall %s' % (self.adb, package), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret_code = s.wait()
        if ret_code != 0:
            return self.ERR_UNINSTALL + ret_code
        return 0

    def makedirs(self, path):
        parent_path = os.path.dirname(path)
        if not self.exists(parent_path):
            ret_code = self.makedirs(parent_path)
            if ret_code != 0:
                return ret_code
        return self.shell("mkdir %s" % path)

    def rmtree(self, dirpath):
        ret_code = self.shell("rm -r %s" % dirpath)
        return ret_code

    def move(self, srcdir, destdir):
        if srcdir is None:
            return 0
        if destdir is None:
            return 0
        ret_code = self.shell("mv %s %s" % (srcdir, destdir))
        return ret_code

    def copy(self, source_file, target_file):
        if source_file is None:
            return 0
        if target_file is None:
            return 0
        ret_code = self.shell("dd if=%s of=%s" % (source_file, target_file))
        return ret_code

    def listdir(self, dirpath):
        ret_code = self.shell("ls %s" % dirpath)
        if ret_code == 0:
            (ret_code, output) = self.run_cmd_host('%s shell ls %s ' % (self.adb, dirpath), False)
            return (ret_code, output)
        else:
            return (ret_code, None)

    def read_file(self, filepath):
        cmd = '%s shell cat %s' % (self.adb, filepath)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True)
        returncode = proc.wait()
        stdout = proc.stdout

        if returncode == 0:
            return stdout
        else:
            return None

    def get_shellcmdoutput(self, cmd=None):
        if cmd is None:
            return None
        cmd = '%s shell %s' % (self.adb, cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True)
        returncode = proc.wait()
        stdout = proc.stdout

        if returncode == 0:
            return stdout
        else:
            return None

    def run_cmd_host(self, cmd, quiet=False):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True)
        returncode = proc.wait()
        stdout = proc.stdout.readlines()

        return (returncode, stdout)

    def run_adb_cmd(self, cmd, quiet=False):
        cmd = '%s %s' % (self.adb, cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True)
        returncode = proc.wait()
        stdout = proc.stdout.readlines()

        return (returncode, stdout)

    def devices(self):
        return self.run_cmd_host('%s devices' % self.adb)
