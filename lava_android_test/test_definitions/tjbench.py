# Copyright (c) 2011-2012 Linaro

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

"""
Tests the performance of libjpegturbo

**URL:** http://sourceforge.net/projects/libjpeg-turbo/

**Default options:** None
"""

import os
import re
import lava_android_test.testdef
from lava_android_test.config import get_config

test_name = 'tjbench'
config = get_config()
curdir = os.path.realpath(os.path.dirname(__file__))
ppm_file_name = 'nightshot_iso_100.ppm'
ppm_url = ("http://testdata.validation.linaro.org/tjbench/"
           "nightshot_iso_100.ppm")
ppm_temp_path = os.path.join(config.tempdir_host, ppm_file_name)
ppm_android_path = os.path.join(config.tempdir_android, test_name,
                                ppm_file_name)
ppm_tmpfs_path = os.path.join('/mnt/mytmpfs', ppm_file_name)
INSTALL_STEPS_HOST_PRE = ['wget --no-check-certificate -q "%s" -O ./%s' % (
                                                    ppm_url, ppm_file_name)]
INSTALL_STEPS_ADB_PRE = ['push %s %s' % (ppm_temp_path, ppm_android_path)]

RUN_STEPS_ADB_SHELL = ['mkdir /mnt/mytmpfs',
                       'mount -t tmpfs -o mode=777 tmpfs /mnt/mytmpfs',
                       'dd if=%s of=%s' % (ppm_android_path, ppm_tmpfs_path),
                       'tjbench %s 95 -rgb -quiet scale 1/2' % ppm_tmpfs_path,
                       'tjbench %s 95 -rgb -quiet' % ppm_tmpfs_path,
                       'umount /mnt/mytmpfs',
                       'rmdir /mnt/mytmpfs']


class TjbenchTestParser(lava_android_test.testdef.AndroidTestParser):

    def parse(self, result_filename='stdout.log', output_filename='stdout.log',
              test_name=''):
        """Parse test output to gather results
        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """
        try:
            unit_pat = re.compile(
                r'^\s*All performance values in (?P<units>\S+)\s*$')
            measure_pat = re.compile(
                ('^\s*(?P<format>\S+)\s+\S+\s+(?P<subsamp>\S+)\s+'
                 '(?P<qual>\d+)\s+\d+\s+\d+\s+(?P<comp_perf>[\d\.]+)\s+'
                 '(?P<comp_ratio>[\d\.]+)\s+(?P<dcomp_perf>[\d\.]+)\s*$')
                )
        except Exception as strerror:
            raise RuntimeError(
                "AndroidTestParser - Invalid regular expression '%s' - %s" % (
                    self.pattern, strerror))
        units = None
        prefix_hash = {}
        with open(output_filename, 'r') as stream:
            for lineno, line in enumerate(stream, 1):
                if units is None:
                    match = unit_pat.search(line)
                    if not match:
                        continue
                    else:
                        units = match.group('units')

                match = measure_pat.search(line)
                if match:
                    tmpdata = match.groupdict()
                    test_case_prefix = '%s_%s_%s' % (tmpdata['format'],
                                          tmpdata['subsamp'],
                                          tmpdata['qual'])
                    if not prefix_hash.get(test_case_prefix):
                        prefix_hash[test_case_prefix] = True
                        test_case_prefix = '%s_%s' % (test_case_prefix,
                                                      'scale_half')
                    common_data = {'log_filename': result_filename,
                                   'log_lineno': lineno,
                                   'result': 'pass'
                                   }
                    comp_perf = {'test_case_id': '%s_%s' % (test_case_prefix,
                                                            'comp_perf'),
                                 'units': units,
                                 'measurement': tmpdata['comp_perf']
                                 }
                    comp_perf.update(common_data)
                    comp_ratio = {'test_case_id': '%s_%s' % (test_case_prefix,
                                                             'comp_ratio'),
                                 'units': '%',
                                 'measurement': tmpdata['comp_ratio']
                                 }
                    comp_ratio.update(common_data)
                    dcomp_perf = {'test_case_id': '%s_%s' % (test_case_prefix,
                                                             'dcomp_perf'),
                                 'units': units,
                                 'measurement': tmpdata['dcomp_perf']
                                 }
                    dcomp_perf.update(common_data)
                    self.results['test_results'].extend([comp_perf, comp_ratio,
                                                         dcomp_perf])
        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)
        self.fixmeasurements()
        self.fixids(test_name=test_name)

inst = lava_android_test.testdef.AndroidTestInstaller(
                                steps_host_pre=INSTALL_STEPS_HOST_PRE,
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                adbshell_steps=RUN_STEPS_ADB_SHELL)
parser = TjbenchTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname="tjbench",
                                                installer=inst,
                                                runner=run,
                                                parser=parser)
