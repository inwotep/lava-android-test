#!/usr/bin/python

# Copyright (c) 2012 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
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
import sys
from lava_android_test.adb import ADB
from lava_android_test.utils import stop_at_pattern, get_pexpet_stdout

adb = ADB(sys.argv[1])
curdir = os.path.realpath(os.path.dirname(__file__))


def get_not_executed():
    pattern = 'cts-tf >'
    command = './android-cts/tools/cts-tradefed --serial %s' % adb.get_serial()
    if not stop_at_pattern(command=command, pattern=pattern):
        print ("Failed to get the cts prompt "
                "when executed command(%s).") % command
        return None

    command = 'list results'
    output = get_pexpet_stdout(command=command)
    if not output:
        print ("Failed to get the output of "
                "cts sub command(%s).") % command
        return None

    command = 'exit'
    get_pexpet_stdout(command=command)
    return output


def prepare_cts():
    cts_prepare_path = os.path.join(curdir, 'cts_prepare.sh')
    cts_prepare_cmd = "bash %s" % cts_prepare_path
    if not stop_at_pattern(command="%s %s" % (cts_prepare_cmd, adb.get_serial)):
        print "Preapration for CTS test times out"
        return False
    return True


def run_cts_with_plan(cts_cmd=None):
    pattern = "Time:"
    plan_command = '--plan CTS'
    if cts_cmd:
        plan_command = "%s %s" % (cts_cmd, plan_command)
    if not stop_at_pattern(command=plan_command, pattern=pattern,
                            timeout=36000):
        print "CTS test times out"
        return False

    return True

def run_cts_continue(cts_cmd=None):
    pattern = "Time:"
    continue_command = '--continue-session 0'
    if cts_cmd:
        continue_command = "%s %s" % (cts_cmd, continue_command)

    while True:
        number_of_not_executed = get_not_executed()
        if number_of_not_executed and int(number_of_not_executed) > 0:
            print ('Reconnect the adb connection before continuing '
                   'the CTS on device(%s)') % adb.get_serial()
            if not adb.reconnect():
                print "Faile to reconnect the adb connection for device()" % (
                                                             adb.get_serial())
                break

            print "Continue the uncompleted CTS test on device(%s)" % (
                                                           adb.get_serial())

            if not stop_at_pattern(command=continue_command,
                                   pattern=pattern,
                                   timeout=36000):
                print "CTS test times out"
        else:
            break


def main():
    run_wrapper_path = os.path.join(curdir, 'cts_run_wrapper.sh')
    run_wrapper_cmd = "bash %s" % run_wrapper_path
    run_wrapper_cmd = '%s run cts --serial %s' % (run_wrapper_cmd,
                                                      adb.get_serial())

    if not prepare_cts():
        sys.exit(1)

    run_cts_with_plan(run_cts_continue)
    run_cts_continue(run_cts_continue)

    sys.exit(0)


if __name__ == '__main__':
    main()
