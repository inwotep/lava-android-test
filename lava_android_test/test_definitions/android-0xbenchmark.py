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
import json

import lava_android_test.testdef

curdir = os.path.realpath(os.path.dirname(__file__))

URL='https://android-build.linaro.org/jenkins/job/linaro-android_leb-panda/lastSuccessfulBuild/artifact/build/out/target/product/pandaboard/system.tar.bz2'
INSTALL_STEPS_HOST = ['tar jxvf system.tar.bz2', 
                          'cp system/app/ZeroXBenchmark.apk ./']
APK_FILE = 'ZeroXBenchmark.apk'

#RUNSTEPS = ['adb shell am start -n org.zeroxlab.benchmark/org.zeroxlab.benchmark.Benchmark --ez math true --ez 2d true --ez 3d true --ez vm true --ez autorun true',

RUN_STEPS_HOST_PRE=[] 
RUN_STEPS_ADB_SHELL = ['am start -n org.zeroxlab.benchmark/org.zeroxlab.benchmark.Benchmark --ez math true --ez vm true --ez autorun true']
RUN_STEPS_HOST_POST = ['cp -rf %s/peacekeeper/* .'%curdir,
                       'python android_0xbenchmark_wait.py \%serial\%']

class ZeroXBenchmarkTestParser(lava_android_test.testdef.AndroidTestParser):

    def parse(self, resultname, output_filename='0xBenchmark.bundle'):
        """Parse test output to gather results
        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """
        #don't know when the bundle format will be created,
        #so first use the xml format
        #filename = '0xBenchmark.xml'
        #self.results['test_results']={'test':'ok'}
#        filename = "0xBenchmark.bundle"
        with open(output_filename) as stream:
            test_results_data =  stream.read()
            test_results_json = json.loads(test_results_data)
            self.results['test_results'] = test_results_json['test_runs'][0]['test_results']
        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()

inst = lava_android_test.testdef.AndroidTestInstaller(steps_host=INSTALL_STEPS_HOST, apks=[APK_FILE],url=URL)
run = lava_android_test.testdef.AndroidTestRunner(RUNSTEPS, adbshell_steps=RUN_STEPS_ADB_SHELL)
parser = ZeroXBenchmarkTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname="android-0xbenchmark", installer=inst,
                                  runner=run, parser=parser, org_ouput_file='/sdcard/0xBenchmark.bundle')
