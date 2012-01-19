# Copyright (c) 2012 Linaro

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
import os
import re
import lava_android_test.testdef

test_name = 'skia'

INSTALL_STEPS_ADB_PRE = []
# Skia can do many more benchmarks, but it becomes almost too much data
# to make a nice chart for. The -match limits the ones we run
ADB_SHELL_STEPS = [ 'logcat -c',
                    'skia_bench -repeat 6 -timers w -config 565 -match bitmap',
                    'skia_bench -repeat 6 -timers w -config 565 -match rects',
                    'skia_bench -repeat 6 -timers w -config 565 -match repeat',
                    'logcat -d -s "skia:*"']

class SkiaTestParser(lava_android_test.testdef.AndroidTestParser):

    def parse(self, result_filename=None, output_filename=None, test_name=test_name):
        pat_test = re.compile(r'running bench \[.*?\]\W+(?P<test>\w+)\W+$')
        pat_type = re.compile(r'\d+\):\W+(?P<type>\w+):\W+msecs =\W+(?P<time>\d+.\d+)')

        test = None
        with open(output_filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                match = pat_test.search(line)
                if match:
                    test = match.group('test')
                else:
                    match = pat_type.search(line)
                    if match:
                        data = {}
                        data['test_case_id'] = "%s_%s" % (test, match.group('type'))
                        data['measurement'] = match.group('time')
                        data['result'] = 'pass'
                        data['units'] = 'ms'
                        data['log_filename'] = result_filename
                        data['log_lineno'] = lineno
                        self.results['test_results'].append(data)

        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()

inst = lava_android_test.testdef.AndroidTestInstaller(
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS)
parser = SkiaTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser)
