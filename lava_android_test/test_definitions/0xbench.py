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
import os
import json

import lava_android_test.testdef

curdir = os.path.realpath(os.path.dirname(__file__))

INSTALL_STEPS_HOST_POST = ['python %s/android-0xbenchmark/android_0xbenchmark_modify_path.py $(SERIAL)' % curdir]

RUN_STEPS_HOST_PRE = ['python %s/android-0xbenchmark/android_0xbenchmark_kill.py $(SERIAL)' % curdir]
RUN_STEPS_ADB_SHELL = ['logcat -c',
                       'am start -n org.zeroxlab.zeroxbenchmark/org.zeroxlab.zeroxbenchmark.Benchmark --ez math true --ez 2d true --ez 3d true --ez vm true --ez autorun true']
RUN_STEPS_HOST_POST = ['python %s/android-0xbenchmark/android_0xbenchmark_wait.py $(SERIAL)' % curdir]

class ZeroXBenchmarkTestParser(lava_android_test.testdef.AndroidTestParser):

    def parse(self, result_filename=None, output_filename='0xBenchmark.bundle', test_name=''):
        """Parse test output to gather results
        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """
        with open(output_filename) as stream:
            test_results_data = stream.read()
            test_results_json = json.loads(test_results_data)
            self.results['test_results'] = test_results_json['test_runs'][0]['test_results']
        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()

save_dir = '/data/data/org.zeroxlab.zeroxbenchmark/files'
inst = lava_android_test.testdef.AndroidTestInstaller(steps_host_post=INSTALL_STEPS_HOST_POST)
run = lava_android_test.testdef.AndroidTestRunner(steps_host_pre=RUN_STEPS_HOST_PRE, adbshell_steps=RUN_STEPS_ADB_SHELL, steps_host_post=RUN_STEPS_HOST_POST)
parser = ZeroXBenchmarkTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname="0xbench", installer=inst,
                                  runner=run, parser=parser, org_ouput_file=os.path.join(save_dir, '0xBenchmark.bundle'))
