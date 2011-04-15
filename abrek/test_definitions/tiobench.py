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
#
"""
   This script automates the installation, execution, and
   results parsing for the tiobench test suite.
   tiobench is a multi-threaded I/O benchmark. It is used to measure
   file system performance in four basic operations: sequential read,
   random read, sequential write, and random write.
"""
import re
import abrek.testdef

VERSION="0.3.3"
URL="http://prdownloads.sourceforge.net/tiobench/tiobench-%s.tar.gz" %(VERSION)
MD5="bf485bf820e693c79e6bd2a38702a128"
INSTALLSTEPS = ['tar -zxvf tiobench-%s.tar.gz' % VERSION,
                'cd tiobench-%s && make' % VERSION]
RUNSTEPS = ["cd tiobench-%s && "\
            "./tiobench.pl --block=4096 --block=8192 --threads=2 "\
            "--numruns=2" % (VERSION)]


class TIObenchTestParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        # Pattern to match the test case name
        pattern1="(?P<test_id>^(Sequential|Random) (Writes|Reads))"
        # Pattern to match the parameter details and measurement
        pattern2=".*?(?P<file_size>\d+)\s+(?P<blks_size>\d+)\s+.*?  "\
                 "(?P<measurement>((\d|#)+\.?\d*))"
        filename = "testoutput.log"
        pat1 = re.compile(pattern1)
        pat2 = re.compile(pattern2)
        tc_id = None
        with open(filename) as fd:
            for line in fd:
                match1 = pat1.match(line)
                match2 = pat2.search(line)
                if match1:
                    tc_id = match1.group('test_id').replace(" ", "")
                if match2 and tc_id != None:
                    results = match2.groupdict()
                    blks_size = results.pop('blks_size')
                    filesize = results.pop('file_size')
                    results['test_case_id'] = (
                        '%s_%sMBfilesize_%sbytesblksize') % (
                            tc_id, filesize, blks_size)
                    self.results['test_results'].append(results)

        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()

tiobench_inst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, url=URL,
    md5=MD5)
tiobench_run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
parse = TIObenchTestParser(appendall={'units':'MB/s', 'result':'pass'})
testobj = abrek.testdef.AbrekTest(testname="tiobench", version=VERSION,
    installer=tiobench_inst, runner=tiobench_run, parser=parse)
