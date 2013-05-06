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
import pexpect
import time
import xml.dom.minidom
from lava_android_test.adb import ADB
from lava_android_test.utils import stop_at_pattern

adb = ADB(sys.argv[1])
curdir = os.path.realpath(os.path.dirname(__file__))


def stop_at_cts_pattern(command=None, pattern=None, timeout=-1):
    if not command:
        return

    if not pattern:
        response = [pexpect.EOF]
    else:
        response = [pattern, pexpect.EOF]

    result = True
    proc_cts = pexpect.spawn(command, logfile=sys.stdout)
    time.sleep(200)
    try:
        match_id = proc_cts.expect(response, timeout=timeout)
        if match_id == 0:
            time.sleep(5)
    except pexpect.TIMEOUT:
        result = False
    finally:
        proc_cts.sendcontrol('C')
        proc_cts.sendline('')

    return result


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
    cts_helper_jar_path = os.path.join(curdir, 'ctshelper.jar')
    cts_prepare_cmd = "bash %s" % cts_prepare_path
    if not stop_at_pattern(command="%s %s %s" % (cts_prepare_cmd,
                                adb.get_serial(), cts_helper_jar_path),
                           timeout=18000):
        print "Preapration for CTS test times out"
        return False
    return True


def run_cts_with_plan(cts_cmd=None, plan='CTS', timeout=36000):
    pattern = "Time:"
    plan_command = '--plan %s' % plan
    if cts_cmd:
        plan_command = "%s %s --disable-reboot" % (cts_cmd, plan_command)
    if not stop_at_cts_pattern(command=plan_command, pattern=pattern,
                            timeout=timeout):
        print "CTS test times out"
        return False

    return True


def run_cts_with_package(cts_cmd=None, package=None, timeout=36000):
    if not package:
        return True
    pattern = "Time:"
    plan_command = '--package %s' % package
    if cts_cmd:
        plan_command = "%s %s --disable-reboot" % (cts_cmd, plan_command)
    if not stop_at_cts_pattern(command=plan_command, pattern=pattern,
                            timeout=timeout):
        print "CTS test times out"
        return False

    return True


def run_cts_with_class(cts_cmd=None, cls=None, method=None, timeout=36000):
    if not cls:
        return True
    pattern = "Time:"
    cmd = '--class %s' % cls
    if method:
        cmd = '%s --method %s' % (cmd, method)

    if cts_cmd:
        cmd = "%s %s --disable-reboot" % (cts_cmd, cmd)
    if not stop_at_cts_pattern(command=cmd, pattern=pattern,
                            timeout=timeout):
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

            if not stop_at_cts_pattern(command=continue_command,
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


def get_value_from_paras(paras=[], option=None, default=None):
    if not option:
        return default

    if not option in paras:
        return default

    index = paras.index(option)
    if len(paras) > index + 1:
        return paras[index + 1]

    return default


def main():

    package_name = None
    plan_name = 'CTS'
    class_name= None
    method_name = None
    timeout = 36000
    #--cts_pkg cts_package_file --package package_name --timeout 36000
    #--cts_pkg cts_package_file --plan plan_name --timeout 36000
    if len(sys.argv) > 2:
        paras = sys.argv[2:]
        cts_pkg = get_value_from_paras(paras=paras, option='--cts-pkg')
        if cts_pkg:
            os.environ["cts_pkg"] = cts_pkg

        package_name = get_value_from_paras(paras=paras, option='--package')
        plan_name = get_value_from_paras(paras=paras,
                                         option='--plan',
                                         default='CTS')
        timeout = get_value_from_paras(paras=paras, option='--timeout',
                                       default=36000)
        if timeout:
            timeout = int(timeout)

        class_name = get_value_from_paras(paras=paras, option='--class')
        method_name = get_value_from_paras(paras=paras, option='--method')

    run_wrapper_path = os.path.join('./android-cts/tools/cts-tradefed ')
    run_wrapper_cmd = "%s" % run_wrapper_path
    run_wrapper_cmd = '%s run cts --serial %s' % (run_wrapper_cmd,
                                                      adb.get_serial())

    logs = collect_logs()
    if not prepare_cts():
        sys.exit(1)

    try:
        if package_name:
            run_cts_with_package(cts_cmd=run_wrapper_cmd, package=package_name,
                                 timeout=timeout)
        elif class_name:
            run_cts_with_class(cts_cmd=run_wrapper_cmd, cls=class_name,
                               method=method_name, timeout=timeout)
        else:
            run_cts_with_plan(cts_cmd=run_wrapper_cmd, plan=plan_name,
                              timeout=timeout)

    finally:
        for log in logs:
            pid = log.get('pid')
            if pid:
                adb.run_cmd_host('kill -9 %s' % pid)

        print_log(logs)

    sys.exit(0)


if __name__ == '__main__':
    main()
