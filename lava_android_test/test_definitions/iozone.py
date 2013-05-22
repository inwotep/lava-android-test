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

#import lava_android_test.config 
from lava_android_test.config import get_config
import lava_android_test.testdef 
import os
import re

class IozoneParser(lava_android_test.testdef.AndroidTestParser):
    '''Custom parser for Iozone. -b with a results file must be specified. The results
       file is not parsed. However the addition of this parameter causes an organized results report
       to be printed at the bottom
    '''
    PATTERN_REPORT = '(?P<report_name>.*?)report' #used to find each report
    PATTERN_UNITS='Output is in (?P<units>\S*)'  #used to determined output units

    def parse(self,result_filename='stdout.log', output_filename='stdout.log', test_name=''):
        '''Parse the results of stdout. This requires the -b option be specified to IOZONE.
        '''
        #filename = artifacts.stdout_pathname
        pat_report = re.compile(self.PATTERN_REPORT)
        pat_units = re.compile(self.PATTERN_UNITS)
        units=''
        with open(output_filename, 'r') as fd:
            lines=fd.readlines()
            for i in range(0,len(lines)):
                line = lines[i]
                match_report = pat_report.search(line)
                match_units = pat_units.search(line)
                if match_report:  #found report.
                    print "match found"
                    ''' The results are the following format
                        <report name> report
                        reclen 1
                        block_size  results 1
                    '''
                    report_name=match_report.groupdict()['report_name'].replace("\"","")
                    i+=1
                    rclen_line = lines[i].replace("\"","")
                    i+=1
                    results_line = lines[i].replace("\"","")
                    reclen_split = rclen_line.split()            
                    results_split = results_line.split() 
                    size=results_split[0]  #first value is the block size
                    for n in range(0,len(reclen_split)):
                       results = {'test_case_id':"iozone_%sKB_%s_rclen_%s" % (report_name, str(size), str(reclen_split[n])),
                                'result':'pass',
                                 'measurement':int(results_split[n+1]),'units':units}
                       self.results['test_results'].append(results)
                elif match_units:
                    units= match_units.groupdict()['units']



test_name = 'iozone'

config = get_config()
curdir = os.path.realpath(os.path.dirname(__file__))
iozone_sh_name = 'iozone.sh'
iozone_dir_path = os.path.join(curdir, 'iozone')
#copy the whole directory over
#this will alow users to place the crosscompiled izone binary
#in the folder and modify iozone.sh to remount the root fs.
iozone_dir_android_path = os.path.join(config.installdir_android,
                                      test_name)
iozone_sh_android_path = os.path.join(iozone_dir_android_path,
                                      iozone_sh_name)

INSTALL_STEPS_ADB_PRE = ['push %s %s ' % (iozone_dir_path,
                                          iozone_dir_android_path),
                          'shell chmod -R 777 %s' % iozone_dir_android_path]

ADB_SHELL_STEPS = ["%s %s" %(iozone_sh_android_path, iozone_dir_android_path)]

inst = lava_android_test.testdef.AndroidTestInstaller(
                                steps_adb_pre=INSTALL_STEPS_ADB_PRE)
run = lava_android_test.testdef.AndroidTestRunner(
                                    adbshell_steps=ADB_SHELL_STEPS)
parser = IozoneParser()
testobj = lava_android_test.testdef.AndroidTest(testname=test_name,
                                    installer=inst,
                                    runner=run,
                                    parser=parser)

