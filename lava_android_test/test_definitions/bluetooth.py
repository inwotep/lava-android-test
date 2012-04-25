# copyright (C) 2012 Linaro Limited
#
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
import re
import lava_android_test.testdef

test_name = 'bluetooth'

cmd = ("am instrument -r -w "
       "com.android.bluetooth.tests/android.bluetooth.BluetoothTestRunner")
RUN_ADB_SHELL_STEPS = [cmd]


class BluetoothTestTestParser(lava_android_test.testdef.AndroidTestParser):

    def parse(self, result_filename='stdout.log', output_filename='stdout.log',
               test_name=test_name):
        """Parse test output to gather results
        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """
        pat_test = re.compile(
            r'^\s*INSTRUMENTATION_STATUS:\s*test=(?P<test_case_id>.+)\s*$')
        pat_status_code = re.compile(
            r'^\s*INSTRUMENTATION_STATUS_CODE:\s*(?P<status_code>[\d-]+)\s*$')
        data = {}
        with open(output_filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                match = pat_test.search(line)
                if match:
                    data['test_case_id'] = match.group('test_case_id')
                    continue

                match = pat_status_code.search(line)
                if match:
                    status_code = match.group('status_code')
                    if status_code == '1':
                        # test case started
                        data = {}
                    elif data['test_case_id']:
                        if status_code == '0':
                            data['result'] = 'pass'
                        else:
                            data['result'] = 'fail'
                        data["log_filename"] = result_filename
                        data["log_lineno"] = lineno
                        self.results['test_results'].append(data)
                        data = {}
                    continue

        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()

inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(
                                adbshell_steps=RUN_ADB_SHELL_STEPS)
parser = BluetoothTestTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                                installer=inst,
                                                runner=run,
                                                parser=parser)
