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
INSTALLSTEPS = ['cp -rf %s/android-0xbenchmark/* .'%curdir,
                'tar jxvf system.tar.bz2', 
                'cp system/app/ZeroXBenchmark.apk ./']
#RUNSTEPS = ['adb shell am start -n org.zeroxlab.benchmark/org.zeroxlab.benchmark.Benchmark --ez math true --ez 2d true --ez 3d true --ez vm true --ez autorun true',
RUNSTEPS = ['rm -fr ./0xBenchmark ./0xBenchmark.bundle ./0xBenchmark.xml'
            'adb shell rm /sdcard/0xBenchmark',
            'adb shell rm /sdcard/0xBenchmark.bundle',
            'adb shell rm /sdcard/0xBenchmark.xml',
            'adb uninstall org.zeroxlab.benchmark',
            'adb install ZeroXBenchmark.apk',
            'adb logcat -c',
            'adb shell am start -n org.zeroxlab.benchmark/org.zeroxlab.benchmark.Benchmark --ez math true --ez vm true --ez autorun true', 
            'python android_0xbenchmark_wait.py',
            'sleep 3']
COPYSTEPS =['adb pull /sdcard/0xBenchmark',
            'adb pull /sdcard/0xBenchmark.bundle',
            'adb pull /sdcard/0xBenchmark.xml']

class ZeroXBenchmarkTestParser(lava_android_test.testdef.AndroidTestParser):

    def parse(self):
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
        filename = "0xBenchmark.bundle"
        with open(filename) as stream:
            test_results_data =  stream.read()
            test_results_json = json.loads(test_results_data)
            self.results['test_results'] = test_results_json['test_runs'][0]['test_results']
        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids()

inst = lava_android_test.testdef.AndroidTestInstaller(INSTALLSTEPS, url=URL)
run = lava_android_test.testdef.AndroidTestRunner(RUNSTEPS, copysteps=COPYSTEPS)
parser = ZeroXBenchmarkTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname="android-0xbenchmark", installer=inst,
                                  runner=run, parser=parser)
