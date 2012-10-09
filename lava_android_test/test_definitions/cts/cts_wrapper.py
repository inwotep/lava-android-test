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
import xml.dom.minidom
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
        #0        17237  126   0     2012.06.23_03.31.49  CTS        unknown
        pattern = ("\s*\d+\s+\d+\s+\d+\s+(?P<no_executed>\d+)"
                   "\s+.+CTS\s+unknown\s*$")
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
    if not stop_at_pattern(command="%s %s" % (cts_prepare_cmd,
                                              adb.get_serial()),
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


def run_cts_with_package(cts_cmd=None, package=None):
    pattern = "I/CommandScheduler: All done"
    if not package:
        return False
    package_command = '--package %s' % package
    if cts_cmd:
        cts_command = "%s %s" % (cts_cmd, package_command)
    if not stop_at_pattern(command=cts_command, pattern=pattern,
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
                print "Faile to reconnect the adb connection of device(%s)" % (
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


def collect_log(command=None, output_file=None):
    if command and output_file:
        print 'Redirect the output of command[%s] to file[%s]' % (command,
                                                                  output_file)
        cmd = 'bash %s %s "%s"' % (os.path.join(curdir, 'cts_redirect.sh'),
                                 output_file, command)
        stdout = adb.run_cmd_host(cmd)[1]
        if stdout:
            return stdout[0].strip()

    return None


def collect_logs():

    kmsg = {'command':
                    'adb -s %s shell cat /proc/kmsg' % (adb.get_serial()),
            'output_file': 'kmsg.log'}

    logcat = {'command':
                'adb -s %s logcat -c; adb -s %s logcat -v time' % (
                                    adb.get_serial(), adb.get_serial()),
              'output_file': 'logcat.log'}

    ## define all the logs need to be collected
    logs = [kmsg, logcat]
    for log in logs:
        pid = collect_log(command=log.get('command'),
                         output_file=log.get('output_file'))
        if pid:
            log['pid'] = pid
    return logs


def print_log(logs=[]):
    for log in logs:
        log_file = log.get('output_file')
        if log_file:
            with open(log_file) as log_fd:
                print '=========Log file [%s] starts=========>>>>>' % log_file
                for line in log_fd.readlines():
                    print line.rstrip()
                print '<<<<<=========Log file [%s] ends=========' % log_file


def get_all_packages(plan_file=None):
    if not plan_file:
        return []
    if not os.path.exists(plan_file):
        print "file(%s) does not exist" % plan_file
        return []

    package_list = []
    try:
        dom = xml.dom.minidom.parse(plan_file)
        test_plan = dom.getElementsByTagName("TestPlan")[0]
        for entry in test_plan.getElementsByTagName("Entry"):
            package_list.append(entry.attributes.get('uri').value)
    except Exception as e:
        print "Has exception to parse the xml file"
        print "Exception: %s" % e
    finally:
        return package_list


def main():
    run_wrapper_path = os.path.join(curdir, 'cts_run_wrapper.sh')
    run_wrapper_cmd = "bash %s" % run_wrapper_path
    run_wrapper_cmd = '%s run cts --serial %s' % (run_wrapper_cmd,
                                                      adb.get_serial())

    logs = collect_logs()
    if not prepare_cts():
        sys.exit(1)

    cts_plan = './android-cts/repository/plans/CTS.xml'
    pkg_list = get_all_packages(plan_file=cts_plan)
    try:
        for pkg in pkg_list:
            run_cts_with_package(cts_cmd=run_wrapper_cmd, package=pkg)
            #if not run_cts_with_package(cts_cmd=run_wrapper_cmd, package=pkg):
                #run_cts_continue(run_wrapper_cmd)
    finally:
        for log in logs:
            pid = log.get('pid')
            if pid:
                adb.run_cmd_host('kill -9 %s' % pid)

        print_log(logs)

    sys.exit(0)


if __name__ == '__main__':
    main()
