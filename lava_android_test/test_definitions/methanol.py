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

"""
The Methanol is a page load benchmarking engine.
The benchmark engine measures the overall page layouting and rendering time of the browser.
Only several test cases are attached to the engine, because of licensing issue.

**URL:** https://gitorious.org/methanol

**Default options:** None
"""

import os
import json

import lava_android_test.testdef

from lava_android_test.config import get_config

curdir = os.path.realpath(os.path.dirname(__file__))
config = get_config()

result_dir = config.resultsdir_android
RUN_STEPS_HOST_PRE = ["bash %s/methanol/methanol.sh $(SERIAL) $(OPTIONS)" % curdir]

class MethanolTestParser(lava_android_test.testdef.AndroidTestParser):

    def real_parse(self, result_filename=None, output_filename='methanol_result.json',
               test_name=''):
        """Parse test output to gather results
        Use the pattern specified when the class was instantiated to look
        through the results line-by-line and find lines that match it.
        Results are then stored in self.results.  If a fixupdict was supplied
        it is used to convert test result strings to a standard format.
        """
        with open(output_filename) as stream:
            test_results_data = stream.read()
            test_results_json = json.loads(test_results_data)
            self.results['test_results'] = test_results_json


inst = lava_android_test.testdef.AndroidTestInstaller()
run = lava_android_test.testdef.AndroidTestRunner(steps_host_pre=RUN_STEPS_HOST_PRE)
parser = MethanolTestParser()
testobj = lava_android_test.testdef.AndroidTest(testname="methanol",
            installer=inst, runner=run, parser=parser,
            org_ouput_file='/data/local/methanol/methanol_result.json',
            default_options='-b DEFAULT -d 192.168.1.10')
