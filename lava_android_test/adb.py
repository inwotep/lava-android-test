# Copyright (c) 2011 Linaro
#
# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.

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

import threading
import os
import re
import subprocess
import tempfile

from Queue import Queue
from lava_android_test.config import get_config

try:
    import posix
except ImportError:
    posix = None

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

    def __init__(self, serial=None, quiet=True):
        if serial is not None:
            self.serial = serial
            self.adb = 'adb -s %s' % serial
        self.cmdExecutor = CommandExecutor(quiet)

    def push(self, source=None, target=None):
        if source is None:
            return (-1, None)

        target_dir = self.target_dir
        if target is None:
            target = os.path.join(self.target_dir, os.path.basename(source))
        else:
            target_dir = os.path.dirname(target)

        self.cmdExecutor.run('%s shell mkdir %s' % (self.adb, target_dir))
        s = self.cmdExecutor.run('%s push %s %s' % (self.adb, source, target))
        ret = s.returncode
        return (ret, target)

    def pull(self, source=None, target=None):
        if source is None:
            return -1

        if target is None:
            cmd = '%s pull %s' % (self.adb, source)
        else:
            cmd = '%s pull %s %s' % (self.adb, source, target)
        s = self.cmdExecutor.run(cmd)
        return s.returncode

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

        s = self.cmdExecutor.run('%s shell chmod 777 %s' % (self.adb, target_path))
        ret_code = s.returncode
        if ret_code != 0:
            return self.ERR_CHMOD + ret_code
        #check the whether the output is empty
        if len(s.stdout) != 0:
            return self.ERR_CHMOD

        self.cmdExecutor.say('Begin to execute shell command: %s' % command)
        s = self.cmdExecutor.run('%s shell %s' % (self.adb, target_path))
        ret_code = s.returncode
        if ret_code != 0:
            return self.ERR_SHELL + ret_code
        output = s.stdout
        ret_code_line = output[len(output) - 1]
        self.cmdExecutor.run('%s shell rm %s' % (self.adb, target_path))

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
        cmd = '%s install %s' % (self.adb, apkpath)
        s = self.cmdExecutor.run(cmd)
        ret_code = s.returncode
        if ret_code != 0:
            return self.ERR_INSTALL + ret_code
        return 0

    def uninstallapk(self, package):
        cmd = '%s uninstall %s' % (self.adb, package)
        s = self.cmdExecutor.run(cmd)
        ret_code = s.returncode
        if ret_code != 0:
            return self.ERR_UNINSTALL + ret_code
        return 0

    def makedirs(self, path):
        parent_path = os.path.dirname(path)
        if parent_path == '/' or self.exists(parent_path):
            return self.shell("mkdir %s" % path)
        else:
            ret = self.makedirs(parent_path)
            if ret == 0:
                return self.shell("mkdir %s" % path)
            else:
                return ret

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
        if self.exists(dirpath):
            (ret_code, output) = self.run_cmd_host('%s shell ls %s ' % (self.adb, dirpath))
            return (ret_code, output)
        else:
            return (1, None)

    def read_file(self, filepath):
        tmpfile_name = tempfile.mkstemp(prefix='read_file_', dir=config.tempdir_host)[1]
        ret_code = self.pull(filepath, tmpfile_name)
        if ret_code != 0:
            return None
        data = None
        try:
            with open(tmpfile_name) as fd:
                data = fd.read()
        finally:
            os.remove(tmpfile_name)
        return data

    def get_shellcmdoutput(self, cmd=None):
        if cmd is None:
            return None
        cmd = '%s shell %s' % (self.adb, cmd)
        return self.run_cmd_host(cmd)

    def run_cmd_host(self, cmd, quiet=True):
        result = self.cmdExecutor.run(cmd, quiet)
        return (result.returncode, result.stdout)

    def run_adb_cmd(self, cmd, quiet=True):
        cmd = '%s %s' % (self.adb, cmd)
        result = self.cmdExecutor.run(cmd, quiet)
        return (result.returncode, result.stdout)

    def devices(self):
        return self.run_cmd_host('%s devices' % self.adb)

    def run_adb_shell_for_test(self, cmd, stdoutlog=None, stderrlog=None, quiet=False):
        cmd = '%s shell %s' % (self.adb, cmd)
        result = self.cmdExecutor.run(cmd, quiet)
        if result.returncode != 0:
            return result.returncode
        self.push_stream_to_device(result.stdout, stdoutlog)
        self.push_stream_to_device(result.stderr, stderrlog)
        return result.returncode

    def push_stream_to_device(self, stream_lines, path):
        basename = os.path.basename(path)
        tmp_path = os.path.join(config.tempdir_host, basename)
        if self.exists(path):
            retcode = self.pull(path, tmp_path)
            if retcode != 0:
                raise Exception('Failed to pull file(%s)stdout to android %s' % path)

        with open(tmp_path, 'a') as tmp_fd:
            tmp_fd.writelines(stream_lines)
            tmp_fd.close()

        if self.push(tmp_path, path)[1] is None:
            raise Exception('Failed to push stdout to android %s' % path)
        os.remove(tmp_path)

class CommandExecutor(object):
    def __init__(self, quiet=True):
        self._queue = Queue()
        self.quiet = quiet
        self.stdout = []
        self.stderr = []

    def say(self, text, *args, **kwargs):
        if not self.quiet:
            print "LAVA:", text.format(*args, **kwargs)

    def display_subprocess_output(self, stream_name, line):
        if stream_name == 'stdout':
            self.say('(stdout) {0}', line.rstrip())
        elif stream_name == 'stderr':
            self.say('(stderr) {0}', line.rstrip())

    def _drain_queue(self):
        while True:
            args = self._queue.get()
            if args is None:
                break
            self.display_subprocess_output(*args)

    def _read_stream(self, stream, stream_name):
        if stream is None:
            return
        for line in iter(stream.readline, ''):
            output_line = (stream_name, line)
            self._queue.put(output_line)
            if stream_name == 'stdout':
                self.stdout.append(line)
            elif stream_name == 'stderr':
                self.stderr.append(line)

    def run(self, cmd, quiet=True):
        self.quiet = quiet
        self.stdout = []
        self.stderr = []
        self.say("Begin to execute command: %s" % cmd.replace('{', '{{').replace('}', '}}'))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    shell=True)

        stdout_reader = threading.Thread(
            target=self._read_stream, args=(proc.stdout, "stdout"))
        stderr_reader = threading.Thread(
            target=self._read_stream, args=(proc.stderr, "stderr"))
        ui_printer = threading.Thread(
            target=self._drain_queue)

        ui_printer.start()
        stdout_reader.start()
        stderr_reader.start()
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
        finally:
            stdout_reader.join()
            stderr_reader.join()
            self._queue.put(None)
            ui_printer.join()
        return CommandResult(proc.returncode, self.stdout, self.stderr)

class CommandResult(object):
    def __init__(self, returncode, stdout=[], stderr=[]):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
