#!/usr/bin/python
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
import string
import sys

import simplejson as json

if len(sys.argv) < 3:
    basename = os.path.basename(sys.argv[0])
    print 'Please specified the merge target file and source files like:'
    print '\t %s target-result-file source-file1 source-file2 ...'
    sys.exit(1)

target_file = sys.argv[1]
test_results = []
for f in sys.argv[2:]:
    if not os.path.exists(f):
        print "The file(%s) does not exist" % f
        continue

    with open(f) as stream:
        f_basename = os.path.basename(f)
        last_hyphen_index = string.rfind(f_basename, '-')
        if last_hyphen_index != -1:
            file_id = f_basename[:last_hyphen_index]
        else:
            file_id = ''

        jobdata = stream.read()
        results_data = json.loads(jobdata)
        for res in  results_data:
            test_case_id = res.get('test_case_id')
            average = res.get('average')
            avg_dev = res.get('average_deviate')
            if file_id and test_case_id == 'summary':
                test_case_id = '%s-summary' % file_id
            test_case_id = test_case_id.replace('/', '_')
            badchars = "[^a-zA-Z0-9\._-]"
            test_case_id = re.sub(badchars, "", test_case_id.replace(" ", "_"))
            test_results.append({'test_case_id': '%s_avg' % test_case_id,
                                 'result': 'pass',
                                 'measurement': average,
                                 'units': 'ms'})
            test_results.append({'test_case_id': '%s_avg_dev' % test_case_id,
                                 'result': 'pass',
                                 'measurement': avg_dev,
                                 'units': '%'})


with open(target_file, 'w') as fd:
    indent = ' ' * 2
    separators = (', ', ': ')
    json.dump(test_results, fd,
               use_decimal=True,
               indent=indent,
               separators=separators,
               sort_keys=False)

print "The result has been merged in file: %s" % target_file
sys.exit(0)
