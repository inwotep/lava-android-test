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
import re
import sys
from lava_android_test.adb import ADB
from lava_android_test.utils import stop_at_pattern

adb = ADB(sys.argv[1])
curdir = os.path.realpath(os.path.dirname(__file__))


def get_not_executed():
    list_result_path = os.path.join(curdir, 'cts_list_result_wrapper.sh')
    list_result_cmd = "bash %s" % list_result_path

    pattern = 'CTS          unknown'
    if not stop_at_pattern(command=list_result_cmd,
                            pattern=pattern, timeout=5):
        print "Failed to list the cts result for device(%s)" % adb.get_serial()

    with open('cts_list_results.log') as fd:
        #0        17237  126   0             2012.06.23_03.31.49  CTS        unknown         
        pattern = "\s*\d+\s+\d+\s+\d+\s+(?P<no_executed>\d+)\s+.+CTS\s+unknown\s*$"
        pat = re.compile(pattern)
        for line in fd.readlines():
            match = pat.search(line)
            if not match:
                continue
            return match.groupdict()['no_executed']
        return 0

def prepare_cts():
    cts_prepare_path = os.path.join(curdir, 'cts_prepare.sh')
    cts_prepare_cmd = "bash %s" % cts_prepare_path
    if not stop_at_pattern(command="%s %s" % (cts_prepare_cmd, adb.get_serial()),
                           timeout=18000):
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
