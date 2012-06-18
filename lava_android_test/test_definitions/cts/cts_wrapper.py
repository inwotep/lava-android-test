#!/usr/bin/python

# Copyright (c) 2012 Linaro

# Author: Linaro Validation Team <linaro-dev@lists.linaro.org>
#
# This file is part of LAVA Android Test.
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
import sys
from lava_android_test.utils import stop_at_pattern

curdir = os.path.realpath(os.path.dirname(__file__))
command = os.path.join(curdir, 'cts_wrapper.sh')
if not len(sys.argv) == 1:
    command = '%s %s' % (command, sys.argv[1])

pattern = "Time:"
if not stop_at_pattern(command="bash %s" % command, pattern=pattern, timeout=36000):
    print "CTS test times out"

sys.exit(0)
